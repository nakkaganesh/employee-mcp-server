from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from client import convert_mcp_tools, run_agent, server
from mcp import Client


app = FastAPI(
    title="Employee MCP API",
    description="Web API for the Employee MCP Agent",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
def root():
    return {
        "message": "Employee MCP API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    question = request.message.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:
        async with Client(server) as client:
            result = await client.list_tools()

            openai_tools = convert_mcp_tools(result.tools)

            messages = []

            answer = await run_agent(
                client,
                openai_tools,
                messages,
                question,
            )

            return ChatResponse(
                response=answer,
            )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Agent request failed: {error}",
        ) from error