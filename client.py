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

async def run_agent(client, openai_tools, question):
    messages = [
        {
            "role": "user",
            "content": question,
        }
    ]

    response = llm.chat.completions.create(
        model="gpt-5.6",
        messages=messages,
        tools=openai_tools,
        tool_choice="auto",
        reasoning_effort="none",
    )

    message = response.choices[0].message

    print("\nModel decision:")
    print(message)

    if message.tool_calls:
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print("\nSelected MCP tool:")
            print(tool_name)

            print("\nArguments:")
            print(arguments)

            tool_result = await client.call_tool(
                tool_name,
                arguments,
            )

            print("\nMCP tool result:")
            print(tool_result)

            messages.append(message)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result.content),
                }
            )

            final_response = llm.chat.completions.create(
                model="gpt-5.6",
                messages=messages,
                tools=openai_tools,
                reasoning_effort="none",
            )

            final_message = final_response.choices[0].message

            print("\nFinal answer:")
            print(final_message.content)


async def main() -> None:
    async with Client(server) as client:
        print("Connected to MCP server")

        result = await client.list_tools()

        openai_tools = convert_mcp_tools(result.tools)

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
                question,
            )

if __name__ == "__main__":
    anyio.run(main)