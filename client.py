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

async def main() -> None:
        async with Client(server) as client:
            print("connected to mcp server")

            result=await client.list_tools()

            openai_tools = []
            question = input("asks a question")

            messages = [
    {
        "role": "user",
        "content": question,
    }
]

            for tool in result.tools:

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
            print("\nOpenAI tools:")
            for tool in openai_tools:
                  print(tool)

            print("\n available tools")

            response = llm.chat.completions.create(
                            model="gpt-5.6",
                            messages=messages,
                            tools=openai_tools,
                            tool_choice="auto",
                            reasoning_effort="none"
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

                    # Execute the tool through MCP
                    tool_result = await client.call_tool(
                        tool_name,
                        arguments,
                    )

                    print("\nMCP tool result:")
                    print(tool_result)

                    # Add the assistant's tool-call message
                    messages.append(message)

                    # Add the MCP tool result
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(tool_result.content),
                        }
                    )

                    # Send the tool result back to the LLM
                    final_response = llm.chat.completions.create(
                        model="gpt-5.6",
                        messages=messages,
                        tools=openai_tools,
                        reasoning_effort="none",
                    )

                    final_message = final_response.choices[0].message

                    print("\nFinal answer:")
                    print(final_message.content)


if __name__ == "__main__":
    anyio.run(main)