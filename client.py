import anyio

import json


from mcp import Client, StdioServerParameters

from dotenv import load_dotenv

from openai import OpenAI


load_dotenv()

llm = OpenAI()

server=StdioServerParameters(
    command="uv",
    args=["run","server.py"]

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

async def run_agent(client, openai_tools, messages, question):
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

        # Add the assistant message to conversation history
        messages.append(message)

        # If there are no tool calls, we have the final answer
        if not message.tool_calls:
            print("\nAgent:")
            print(message.content)
            break

        # Execute every tool requested by the model
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"\nTool: {tool_name}")
            print(f"Arguments: {arguments}")

            tool_result = await client.call_tool(
                tool_name,
                arguments,
            )

            print(f"Result: {tool_result}")

            # Extract cleaner text from MCP result
            if tool_result.content:
                tool_content = "\n".join(
                    item.text
                    for item in tool_result.content
                    if hasattr(item, "text")
                )
            else:
                tool_content = ""

            # Return this specific result to the model
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_content,
                }
            )
async def main() -> None:
    async with Client(server) as client:
        print("Connected to MCP server")

        result = await client.list_tools()

        openai_tools = convert_mcp_tools(result.tools)

        messages=[]

        print("\nEmployee MCP Agent started.")
        print("Type 'exit' to stop.")

        while True:
            question = input("\nYou: ").strip()

            if question.lower() in {"exit", "quit"}:
                print("\nGoodbye!")
                break

            if not question:
                continue

            await run_agent(
                client,
                openai_tools,
                messages,
                question,
            )

if __name__ == "__main__":
    anyio.run(main)