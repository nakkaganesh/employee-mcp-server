# Employee MCP Server

[![Tests](https://github.com/nakkaganesh/employee-mcp-server/actions/workflows/tests.yml/badge.svg)](https://github.com/nakkaganesh/employee-mcp-server/actions/workflows/tests.yml)

An AI-powered employee support assistant built using **Model Context Protocol (MCP), OpenAI, Python, FastAPI, MySQL, Docker, and Docker Compose**.

The assistant understands natural-language employee requests, dynamically selects MCP tools, retrieves employee information, manages IT support tickets, and requires human approval before performing database-changing operations.

---

## Features

- Model Context Protocol (MCP) server
- OpenAI-powered agent
- Dynamic MCP tool discovery and selection
- Employee leave balance lookup
- IT support ticket creation
- IT ticket lookup
- Employee ticket history
- Ticket status updates
- Human-in-the-loop approval for write operations
- FastAPI REST API
- Browser-based chat interface
- MySQL persistence
- Database transactions with commit and rollback
- Input validation and error handling
- Automated testing with pytest
- Mocked dependencies for unit/API testing
- GitHub Actions continuous integration
- Dockerized Python application
- Dockerized MySQL database
- Docker Compose orchestration
- Persistent MySQL Docker volume
- Automatic database initialization

---

## Architecture

```text
                    User
                     |
                     v
              Browser / CLI
                     |
                     v
                OpenAI Agent
                     |
                     v
                 MCP Client
                     |
          +----------+----------+
          |                     |
          v                     v
     Tool Selection       Human Approval
                                |
                                v
                           Write Actions
          |                     |
          +----------+----------+
                     |
                     v
                 MCP Server
                     |
          +----------+----------+
          |                     |
          v                     v
    Leave Balance          IT Tickets
          |                     |
          +----------+----------+
                     |
                     v
                database.py
                     |
                     v
                   MySQL
```

### Web Application Flow

```text
Browser
   |
   v
static/index.html
   |
   v
FastAPI
web_app.py
   |
   v
client.py
   |
   v
MCP Server
server.py
   |
   v
database.py
   |
   v
MySQL
```

For write operations:

```text
User Request
     |
     v
OpenAI selects write tool
     |
     v
Approval Required
     |
 +---+---+
 |       |
 v       v
Approve Reject
 |       |
 v       v
Execute Cancel
```

---

## Project Structure

```text
employee-mcp-server/
├── .github/
│   └── workflows/
│       └── tests.yml
├── docker/
│   └── init.sql
├── src/
│   └── employee_mcp_server/
│       └── __init__.py
├── static/
│   └── index.html
├── tests/
│   ├── test_server.py
│   └── test_web_app.py
├── .dockerignore
├── .gitignore
├── .python-version
├── client.py
├── compose.yml
├── database.py
├── Dockerfile
├── pyproject.toml
├── README.md
├── server.py
├── uv.lock
└── web_app.py
```

---

## MCP Tools

The MCP server exposes employee-support tools that the AI agent can select dynamically based on the user's request.

### `get_leave_balance`

Returns the remaining annual leave balance for an employee.

Example:

```text
How much leave does EMP002 have?
```

Example response:

```text
Employee EMP002 has 6 annual leave days remaining.
```

---

### `create_it_ticket`

Creates an IT support ticket for a valid employee.

Because this operation modifies persistent data, explicit user approval is required before execution.

Example:

```text
Create an IT ticket for EMP001 because my laptop keyboard is not working
```

---

### `get_it_ticket`

Retrieves an IT support ticket using its ticket ID.

Example:

```text
What is the status of IT-1001?
```

---

### `get_employee_tickets`

Returns the IT support tickets belonging to an employee.

Example:

```text
Show all tickets for EMP001
```

---

### `update_ticket_status`

Updates an IT ticket to one of the supported statuses:

- `created`
- `in_progress`
- `resolved`
- `closed`

Example:

```text
Change IT-1001 to resolved
```

Ticket status changes require human approval before execution.

---

## Human-in-the-Loop Approval

Actions that modify persistent data require explicit user approval.

Human approval currently applies to:

- Creating IT tickets
- Updating ticket statuses

Read-only operations can execute directly.

```text
User Request
     |
     v
OpenAI Agent
     |
     v
Select MCP Tool
     |
     v
Write operation?
     |
 +---+---+
 |       |
No      Yes
 |       |
 v       v
Execute Approval Required
         |
      +--+--+
      |     |
      v     v
   Approve Reject
      |     |
      v     v
   Execute Cancel
```

This prevents the AI assistant from modifying persistent data without user confirmation.

---

## Database

The application uses **MySQL** for employee and IT ticket data.

The database access logic is separated from the MCP tool layer:

```text
MCP Tool
   |
   v
server.py
   |
   v
database.py
   |
   v
MySQL
```

### Tables

The application uses two main tables:

```text
employees
tickets
```

The `employees` table contains:

- Employee ID
- Name
- Department
- Leave balance

The `tickets` table contains:

- Ticket ID
- Employee ID
- Issue
- Status
- Created timestamp

The `tickets.employee_id` column references the employee through a foreign key.

### Transactions

Database write operations use transactions.

Successful writes call:

```python
connection.commit()
```

Database errors trigger:

```python
connection.rollback()
```

---

## Sample Employees

The Docker development database is initialized with sample employee records:

| Employee ID | Name | Department | Leave Balance |
|---|---|---|---:|
| EMP001 | Rahul Sharma | Engineering | 12 |
| EMP002 | Priya Reddy | Finance | 6 |
| EMP003 | Arjun Kumar | Operations | 8 |

These records are intended for development and demonstration.

---

## Requirements

### Local Development

- Python 3.14+
- uv
- MySQL
- OpenAI API key

### Containerized Setup

- Docker
- Docker Compose
- OpenAI API key

---

## Installation

Clone the repository:

```bash
git clone https://github.com/nakkaganesh/employee-mcp-server.git
cd employee-mcp-server
```

Install dependencies:

```bash
uv sync
```

---

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
OPENAI_API_KEY=your_openai_api_key

DB_HOST=localhost
DB_PORT=3306
DB_USER=employee_app
DB_PASSWORD=your_database_password
DB_NAME=employee_mcp

MYSQL_ROOT_PASSWORD=your_mysql_root_password
```

Never commit your real `.env` file.

The project `.gitignore` and `.dockerignore` exclude `.env`.

When using Docker Compose, `DB_HOST` is overridden so that the application connects to the `mysql` service.

---

## Run the CLI Agent

Make sure MySQL is running and your environment variables are configured.

Run:

```bash
uv run client.py
```

You should see:

```text
Connected to MCP server

Employee MCP Agent started.
Type 'exit' to stop.
```

Example:

```text
You: How much leave does EMP002 have?

Tool: get_leave_balance
Arguments: {'employee_id': 'EMP002'}

Agent:
Employee EMP002 has 6 annual leave days remaining.
```

Exit using:

```text
exit
```

---

## Run the Web Application

Start the FastAPI application:

```bash
uv run uvicorn web_app:app --reload
```

Then open the local application in your browser.

The browser interface supports:

- Natural-language employee requests
- Leave balance lookup
- IT ticket lookup
- IT ticket creation
- Ticket status updates
- Human approval and rejection

The web interface communicates with the FastAPI backend using HTTP requests.

---

## API Endpoints

### Health Check

```text
GET /health
```

Returns:

```json
{
  "status": "healthy"
}
```

### Chat

```text
POST /chat
```

Example request:

```json
{
  "message": "How much leave does EMP002 have?"
}
```

### Approve Action

```text
POST /approve/{approval_id}
```

Executes a pending database-changing action after user approval.

### Reject Action

```text
DELETE /approve/{approval_id}
```

Rejects the pending action without executing it.

---

## Docker

Build the application image:

```bash
docker build -t employee-mcp-server .
```

The Dockerfile runs the FastAPI web application by default.

---

## Docker Compose

Docker Compose provides the application and MySQL environment.

The MySQL service includes:

- MySQL 8.4
- Persistent storage
- Health check
- Automatic schema initialization
- Sample employee records

Start MySQL:

```bash
docker compose up -d mysql
```

Check its status:

```bash
docker compose ps
```

Wait until MySQL reports:

```text
healthy
```

Run the CLI application through Compose:

```bash
docker compose run --rm app
```

When finished:

```bash
docker compose down
```

This preserves the MySQL volume.

To remove the containers and database volume:

````markdown
Start the complete application:

```bash
docker compose down -v
```

Use the `-v` command carefully because it deletes the containerized database data.

---

## Testing

The project uses **pytest** for automated testing.

Run:

```bash
uv run python -m pytest -v
```

The current test suite contains **22 passing tests**.

Tests cover areas including:

- Employee leave balance lookup
- Missing employee handling
- IT ticket creation
- Empty ticket issue validation
- Ticket lookup
- Missing ticket handling
- Employee ticket history
- Ticket status updates
- Invalid ticket statuses
- FastAPI health endpoint
- Empty chat validation
- Agent responses
- Approval requests
- Approval execution
- Approval rejection
- Single-use approval behavior

Database and MCP dependencies are mocked where appropriate so unit/API tests can run without modifying the real database.

---

## Continuous Integration

The repository uses **GitHub Actions** for continuous integration.

The workflow is located at:

```text
.github/workflows/tests.yml
```

Whenever code is pushed to `main` or a pull request targets `main`, GitHub Actions:

```text
Checkout repository
        |
        v
Install uv
        |
        v
Install Python 3.14
        |
        v
Install dependencies
        |
        v
Run pytest
        |
        v
Pass / Fail
```

---

## Security

Sensitive configuration is supplied through environment variables.

The following should never be committed:

```text
.env
API keys
Database passwords
Other credentials
```

The `.env` file is excluded through `.gitignore` and `.dockerignore`.

The Docker image does not contain the local `.env` file.

Write operations also require explicit human approval before execution.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| MCP | Tool communication protocol |
| OpenAI | Natural-language reasoning and tool selection |
| FastAPI | REST API and web backend |
| HTML/CSS/JavaScript | Browser interface |
| MySQL | Persistent employee and ticket data |
| mysql-connector-python | Python-to-MySQL connectivity |
| python-dotenv | Environment variable management |
| Pydantic | API request/response validation |
| pytest | Automated testing |
| uv | Python dependency and environment management |
| Docker | Application containerization |
| Docker Compose | Multi-container development |
| Git | Version control |
| GitHub | Source repository |
| GitHub Actions | Continuous integration |

---

## Key Concepts Demonstrated

This project demonstrates:

- Agentic AI workflows
- Model Context Protocol (MCP)
- LLM function/tool calling
- Dynamic MCP tool discovery
- Human-in-the-loop AI
- Read and write tool separation
- FastAPI REST APIs
- Browser-to-backend communication
- Relational database integration
- SQL persistence
- Database transactions
- Foreign-key relationships
- Input validation
- Error handling
- Unit and API testing
- Dependency mocking
- Environment-based configuration
- Secret management
- Docker containerization
- Docker Compose
- Persistent Docker volumes
- GitHub Actions CI
- Git/GitHub workflow

---

## Example Interaction

```text
Employee MCP Agent started.
Type 'exit' to stop.

You: How much leave does EMP002 have?

Tool: get_leave_balance
Arguments: {'employee_id': 'EMP002'}

Agent:
Employee EMP002 has 6 annual leave days remaining.

You: Create an IT ticket for EMP001 because my keyboard is not working

Requested action: create_it_ticket

This action will modify data. Approve? (yes/no): yes

Agent:
The IT support ticket was created.
```

---

## Current Limitations

- Web chat requests do not currently persist conversation history between separate HTTP requests.
- Pending web approvals are stored in memory and are lost when the application restarts.
- The project does not currently implement employee authentication or authorization.
- The included database records are demonstration data.

These limitations keep the project simple and understandable while demonstrating the core MCP and agent workflow.

---

## Future Improvements

Potential future improvements include:

- Authentication and authorization
- Role-based access control
- Persistent conversation sessions
- Persistent approval storage
- Structured application logging
- Integration tests using containerized MySQL
- Cloud deployment
- Managed production database

---

## Repository

Project repository:

`https://github.com/nakkaganesh/employee-mcp-server`

---

## Author

**Nakka Ganesh**

AI / Agentic AI Engineering Portfolio Project