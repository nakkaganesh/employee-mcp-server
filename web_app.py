import uuid

from fastapi import FastAPI, HTTPException
from mcp import Client
from pydantic import BaseModel

from client import (
    ApprovalRequired,
    convert_mcp_tools,
    run_agent,
    server,
)


app = FastAPI(
    title="Employee MCP API",
    description="Web API for the Employee MCP Agent",
    version="1.0.0",
)


# Temporary in-memory storage for actions awaiting approval.
pending_approvals = {}


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str | None = None
    approval_required: bool = False
    approval_id: str | None = None
    tool_name: str | None = None
    arguments: dict | None = None


class ApprovalResponse(BaseModel):
    status: str
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

    except ApprovalRequired as approval:
        approval_id = str(uuid.uuid4())

        pending_approvals[approval_id] = {
            "tool_name": approval.tool_name,
            "arguments": approval.arguments,
        }

        return ChatResponse(
            response="This action requires your approval.",
            approval_required=True,
            approval_id=approval_id,
            tool_name=approval.tool_name,
            arguments=approval.arguments,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Agent request failed: {error}",
        ) from error


@app.post(
    "/approve/{approval_id}",
    response_model=ApprovalResponse,
)
async def approve_action(approval_id: str):
    pending_action = pending_approvals.pop(
        approval_id,
        None,
    )

    if pending_action is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found or already processed.",
        )

    tool_name = pending_action["tool_name"]
    arguments = pending_action["arguments"]

    try:
        async with Client(server) as client:
            result = await client.call_tool(
                tool_name,
                arguments,
            )

            if result.content:
                tool_content = "\n".join(
                    item.text
                    for item in result.content
                    if hasattr(item, "text")
                )
            else:
                tool_content = ""

            if result.is_error:
                raise HTTPException(
                    status_code=400,
                    detail=tool_content or "MCP tool execution failed.",
                )

            return ApprovalResponse(
                status="approved",
                response=tool_content,
            )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Approved action failed: {error}",
        ) from error


@app.delete(
    "/approve/{approval_id}",
    response_model=ApprovalResponse,
)
async def reject_action(approval_id: str):
    pending_action = pending_approvals.pop(
        approval_id,
        None,
    )

    if pending_action is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found or already processed.",
        )

    return ApprovalResponse(
        status="rejected",
        response="The requested action was rejected and was not executed.",
    )