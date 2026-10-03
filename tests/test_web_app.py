from fastapi.testclient import TestClient

from web_app import app, pending_approvals


client = TestClient(app)


def setup_function():
    pending_approvals.clear()


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Employee MCP API is running"
    assert response.json()["docs"] == "/docs"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_empty_chat_message():
    response = client.post(
        "/chat",
        json={"message": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Message cannot be empty."


def test_unknown_approval():
    response = client.post(
        "/approve/does-not-exist",
    )

    assert response.status_code == 404


def test_unknown_rejection():
    response = client.delete(
        "/approve/does-not-exist",
    )

    assert response.status_code == 404


def test_reject_pending_action():
    approval_id = "test-approval"

    pending_approvals[approval_id] = {
        "tool_name": "create_it_ticket",
        "arguments": {
            "employee_id": "EMP001",
            "issue": "Test issue",
        },
    }

    response = client.delete(
        f"/approve/{approval_id}",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert approval_id not in pending_approvals


def test_approval_is_single_use_after_rejection():
    approval_id = "single-use-test"

    pending_approvals[approval_id] = {
        "tool_name": "create_it_ticket",
        "arguments": {
            "employee_id": "EMP001",
            "issue": "Test issue",
        },
    }

    first_response = client.delete(
        f"/approve/{approval_id}",
    )

    second_response = client.delete(
        f"/approve/{approval_id}",
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 404

from client import ApprovalRequired


def test_chat_returns_agent_response(monkeypatch):
    async def fake_run_agent(
        client,
        openai_tools,
        messages,
        question,
        approval_callback=None,
    ):
        return "EMP002 has 6 annual leave days remaining."

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def list_tools(self):
            class Result:
                tools = []

            return Result()

    monkeypatch.setattr(
        "web_app.Client",
        lambda server: FakeClient(),
    )

    monkeypatch.setattr(
        "web_app.run_agent",
        fake_run_agent,
    )

    response = client.post(
        "/chat",
        json={
            "message": "How much leave does EMP002 have?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["response"] == (
        "EMP002 has 6 annual leave days remaining."
    )
    assert data["approval_required"] is False
    assert data["approval_id"] is None


def test_chat_returns_approval_request(monkeypatch):
    async def fake_run_agent(
        client,
        openai_tools,
        messages,
        question,
        approval_callback=None,
    ):
        raise ApprovalRequired(
            "create_it_ticket",
            {
                "employee_id": "EMP001",
                "issue": "Keyboard is not working",
            },
        )

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def list_tools(self):
            class Result:
                tools = []

            return Result()

    monkeypatch.setattr(
        "web_app.Client",
        lambda server: FakeClient(),
    )

    monkeypatch.setattr(
        "web_app.run_agent",
        fake_run_agent,
    )

    response = client.post(
        "/chat",
        json={
            "message": (
                "Create an IT ticket for EMP001 "
                "because my keyboard is not working"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["approval_required"] is True
    assert data["approval_id"] is not None
    assert data["tool_name"] == "create_it_ticket"

    assert data["arguments"] == {
        "employee_id": "EMP001",
        "issue": "Keyboard is not working",
    }

    assert data["approval_id"] in pending_approvals


def test_approve_pending_action_executes_tool(monkeypatch):
    approval_id = "approved-action-test"

    pending_approvals[approval_id] = {
        "tool_name": "create_it_ticket",
        "arguments": {
            "employee_id": "EMP001",
            "issue": "Keyboard is not working",
        },
    }

    class TextContent:
        text = "IT ticket created successfully."

    class ToolResult:
        is_error = False
        content = [TextContent()]

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def call_tool(self, tool_name, arguments):
            assert tool_name == "create_it_ticket"

            assert arguments == {
                "employee_id": "EMP001",
                "issue": "Keyboard is not working",
            }

            return ToolResult()

    monkeypatch.setattr(
        "web_app.Client",
        lambda server: FakeClient(),
    )

    response = client.post(
        f"/approve/{approval_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "approved"
    assert data["response"] == "IT ticket created successfully."

    assert approval_id not in pending_approvals