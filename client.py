import json
import os

import anyio
from dotenv import load_dotenv
from mcp import Client, StdioServerParameters
from openai import OpenAI


load_dotenv()

llm = OpenAI()

server = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
    env=os.environ.copy(),
)


def convert_mcp_tools(mcp_tools):
    """Convert MCP tool definitions into OpenAI function-tool definitions."""

    openai_tools = []

    for tool in mcp_tools:
        openai_tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.input_schema,
                },
            }
        )

    return openai_tools


async def run_agent(
    client,
    openai_tools,
    messages,
    question,
    approval_callback=None,
):
    """Run one conversation turn and return the agent's final response."""

    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    while True:
        response = llm.chat.completions.create(
            model="gpt-5.6",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto",
            reasoning_effort="none",
        )

        message = response.choices[0].message

        messages.append(message)

        # No tool call means the model has produced its final answer.
        if not message.tool_calls:
            return message.content or ""

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"\nTool: {tool_name}")
            print(f"Arguments: {arguments}")

            # Database-changing tools require explicit approval.
            if tool_name in {"create_it_ticket", "update_ticket_status"}:
                approved = False

                if approval_callback is not None:
                    approved = await approval_callback(
                        tool_name,
                        arguments,
                    )

                if not approved:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": "The user rejected this tool action.",
                        }
                    )
                    continue

            try:
                tool_result = await client.call_tool(
                    tool_name,
                    arguments,
                )

                if tool_result.content:
                    tool_content = "\n".join(
                        item.text
                        for item in tool_result.content
                        if hasattr(item, "text")
                    )
                else:
                    tool_content = ""

                if tool_result.is_error:
                    print("\nMCP tool returned an error:")
                    print(tool_content)
                else:
                    print(f"Result: {tool_content}")

            except Exception as error:
                tool_content = f"Tool execution failed: {error}"

                print("\nTool error:")
                print(error)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_content,
                }
            )


async def cli_approval(tool_name, arguments):
    """Request approval for database-changing tools in the terminal."""

    print(f"\nRequested action: {tool_name}")
    print(f"Arguments: {arguments}")

    approval = input(
        "This action will modify data. Approve? (yes/no): "
    ).strip().lower()

    return approval in {"yes", "y"}


async def main() -> None:
    async with Client(server) as client:
        print("Connected to MCP server")

        result = await client.list_tools()

        openai_tools = convert_mcp_tools(result.tools)

        messages = []

        print("\nEmployee MCP Agent started.")
        print("Type 'exit' to stop.")

        while True:
            question = input("\nYou: ").strip()

            if question.lower() in {"exit", "quit"}:
                print("\nGoodbye!")
                break

            if not question:
                continue

            answer = await run_agent(
                client,
                openai_tools,
                messages,
                question,
                approval_callback=cli_approval,
            )

            print("\nAgent:")
            print(answer)


if __name__ == "__main__":
    anyio.run(main)