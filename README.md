# Employee MCP Server

An AI-powered employee support agent built using the Model Context Protocol (MCP), OpenAI, Python, and MySQL.

The agent dynamically selects MCP tools based on natural-language requests and can retrieve employee information, calculate GST, create and manage IT support tickets, and maintain conversational context.

## Features

- MCP server with dynamically discovered tools
- OpenAI-powered tool selection
- Multi-turn conversation memory
- Employee leave balance lookup
- GST calculation
- IT ticket creation
- IT ticket status lookup
- Employee ticket history
- Ticket status updates
- MySQL persistence
- Input validation and error handling
- Human approval for database-changing actions
- Transaction handling with commit and rollback
- Automated unit testing with pytest
- Mocked database dependencies for safe testing

## Architecture

```text
User
  |
  v
OpenAI Agent
  |
  v
MCP Client
  |
  |-- Conversation Memory
  |-- Dynamic Tool Selection
  |-- Human Approval
  |
  v
MCP Server
  |
  |-- get_leave_balance
  |-- calculate_gst
  |-- create_it_ticket
  |-- get_it_ticket
  |-- get_employee_tickets
  |-- update_ticket_status
  |
  v
Database Layer
  |
  v
MySQL
```

## Project Structure

```text
employee-mcp-server/
├── client.py
├── server.py
├── database.py
├── tests/
│   └── test_server.py
├── src/
│   └── employee_mcp_server/
│       └── __init__.py
├── pyproject.toml
├── uv.lock
├── requirements.txt
├── .python-version
├── .gitignore
└── README.md
```

## MCP Tools

### `get_leave_balance`

Returns the remaining annual leave balance for an employee.

Example:

```text
How much leave does EMP002 have?
```

### `calculate_gst`

Calculates GST and the total amount including GST.

Example:

```text
Calculate 18% GST on 50000
```

### `create_it_ticket`

Creates an IT support ticket for a valid employee.

Database-changing operations require human approval before execution.

Example:

```text
Create an IT ticket for EMP001 because my laptop won't start
```

### `get_it_ticket`

Retrieves an IT support ticket by ticket ID.

Example:

```text
What is the status of IT-1001?
```

### `get_employee_tickets`

Returns all IT support tickets belonging to an employee.

Example:

```text
Show all tickets for EMP001
```

### `update_ticket_status`

Updates a ticket to one of the supported statuses:

- `created`
- `in_progress`
- `resolved`
- `closed`

Example:

```text
Change IT-1001 to resolved
```

## Database

The application uses MySQL for persistent employee and IT ticket data.

The database layer is separated from the MCP server:

```text
server.py
    |
    v
database.py
    |
    v
MySQL
```

Database write operations use transactions with `commit()` and `rollback()`.

## Human-in-the-Loop

Actions that modify persistent data require explicit user approval.

For example:

```text
User request
    |
    v
Agent selects create_it_ticket
    |
    v
Approval required
    |
    +-- Approved --> Execute MCP tool
    |
    +-- Rejected --> Cancel operation
```

This applies to ticket creation and ticket status updates.

## Installation

Clone the repository:

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd employee-mcp-server
```

Install dependencies using uv:

```bash
uv sync
```

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
OPENAI_API_KEY=your_openai_api_key

DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=employee_mcp
```

Do not commit `.env` to Git.

## Run the Agent

```bash
uv run client.py
```

Then interact with the agent:

```text
You: How much leave does EMP002 have?

Agent:
EMP002 has 6 annual leave days remaining.
```

## Testing

Run the automated test suite:

```bash
uv run python -m pytest -v
```

The unit tests mock database dependencies, allowing MCP business logic to be tested without modifying the real MySQL database.

## Technology Stack

- Python
- Model Context Protocol (MCP)
- OpenAI API
- MySQL
- mysql-connector-python
- pytest
- uv
- Git

## Key Concepts Demonstrated

This project demonstrates:

- Agentic AI tool use
- MCP client/server architecture
- Dynamic function calling
- LLM orchestration
- Human-in-the-loop workflows
- Conversational memory
- Database persistence
- Separation of concerns
- SQL transactions
- Error handling and validation
- Dependency mocking
- Automated unit testing

## Future Improvements

- Authentication and authorization
- Role-based tool permissions
- Structured logging
- Database connection pooling
- Integration tests
- REST API or web interface
- Docker deployment
- Cloud-hosted MySQL
- CI/CD with GitHub Actions# employee-map-server
