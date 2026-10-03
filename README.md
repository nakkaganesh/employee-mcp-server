# Employee MCP Server

[![Tests](https://github.com/nakkaganesh/employee-mcp-server/actions/workflows/tests.yml/badge.svg)](https://github.com/nakkaganesh/employee-mcp-server/actions/workflows/tests.yml)

An AI-powered employee support agent built using the **Model Context Protocol (MCP), OpenAI, Python, MySQL, Docker, and Docker Compose**.

The agent understands natural-language employee requests, dynamically selects MCP tools, retrieves employee information, calculates GST, creates and manages IT support tickets, maintains conversation context, and requires human approval before performing database-changing operations.

---

## Features

- Model Context Protocol (MCP) server
- OpenAI-powered agent
- Dynamic MCP tool discovery and selection
- Multi-turn conversation memory
- Employee leave balance lookup
- GST calculation
- IT support ticket creation
- IT ticket status lookup
- Employee ticket history
- Ticket status updates
- Human-in-the-loop approval for write operations
- MySQL persistence
- Dedicated database access layer
- Database transactions with commit and rollback
- Input validation and error handling
- Automated unit testing with pytest
- Mocked database dependencies for safe unit testing
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
                OpenAI Agent
                      |
                      v
                 MCP Client
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
    Conversation   Dynamic      Human
      Memory        Tool       Approval
                   Selection
                      |
                      v
                  MCP Server
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
 Leave Balance    IT Tickets       GST
        |             |
        +------+------+
               |
               v
         Database Layer
          database.py
               |
               v
             MySQL
```

When running with Docker Compose:

```text
Host Machine
     |
     v
Docker Compose
     |
     +-------------------------------+
     |                               |
     v                               v
App Container                  MySQL Container
     |                               |
     |-- OpenAI Agent                |-- employees
     |-- MCP Client                  |
     |-- MCP Server                  |-- tickets
     |-- database.py                 |
     |                               |
     +------------- mysql -----------+
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
├── tests/
│   └── test_server.py
├── .dockerignore
├── .gitignore
├── .python-version
├── client.py
├── compose.yml
├── database.py
├── Dockerfile
├── pyproject.toml
├── README.md
├── requirements.txt
├── server.py
└── uv.lock
```

---

## MCP Tools

The MCP server exposes tools that the AI agent can select dynamically based on the user's request.

### `get_leave_balance`

Returns the remaining annual leave balance for an employee.

Example:

```text
How much leave does EMP002 have?
```

Example response:

```text
EMP002 has 6 annual leave days remaining.
```

---

### `calculate_gst`

Calculates GST and the total amount including GST.

Example:

```text
Calculate 18% GST on 50000
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

Retrieves an IT support ticket by ticket ID.

Example:

```text
What is the status of IT-1001?
```

---

### `get_employee_tickets`

Returns IT support tickets belonging to an employee.

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
Is this a write operation?
     |
     +------ No ------> Execute Tool
     |
    Yes
     |
     v
Request Human Approval
     |
 +---+---+
 |       |
 v       v
Approve Reject
 |       |
 v       v
Execute Cancel
```

Human approval applies to operations such as:

- Creating IT tickets
- Updating ticket statuses

This prevents the AI agent from modifying persistent data without user confirmation.

---

## Database

The application uses MySQL for persistent employee and IT ticket data.

The database access logic is separated from the MCP tool layer:

```text
MCP Server
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

The application uses two primary tables:

```text
employees
tickets
```

The `employees` table contains employee information and leave balances.

The `tickets` table stores IT support requests and references employees through a foreign key.

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

This helps protect database consistency when write operations fail.

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

For local development:

- Python 3.14+
- uv
- MySQL
- OpenAI API key

For the containerized setup:

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

Install dependencies using `uv`:

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

The project `.gitignore` excludes `.env` from Git.

When the application runs through Docker Compose, `DB_HOST` is overridden so that the application connects to the `mysql` Compose service rather than `localhost`.

---

## Run Locally

Make sure your local MySQL database is running and the environment variables point to it.

Start the agent:

```bash
uv run client.py
```

You should see:

```text
Connected to MCP server

Employee MCP Agent started.
Type 'exit' to stop.

You:
```

Example:

```text
You: How much leave does EMP002 have?

Tool: get_leave_balance
Arguments: {'employee_id': 'EMP002'}

Agent:
EMP002 has 6 annual leave days remaining.
```

Exit with:

```text
exit
```

---

# Docker

The Python application can also run inside Docker.

## Build the Image

Start Docker Desktop and run:

```bash
docker build -t employee-mcp-server .
```

Verify the image:

```bash
docker images employee-mcp-server
```

---

## Run Against MySQL on the Host

On Docker Desktop for macOS, a container can access MySQL running on the host through:

```text
host.docker.internal
```

Run:

```bash
docker run --rm -it \
  --env-file .env \
  -e DB_HOST=host.docker.internal \
  employee-mcp-server
```

This architecture looks like:

```text
Docker App Container
        |
        v
host.docker.internal
        |
        v
MySQL on macOS
```

For a fully containerized environment, use Docker Compose instead.

---

# Docker Compose

Docker Compose runs both the application and MySQL in containers.

This is the recommended way to run the complete development environment.

## Start MySQL

Start Docker Desktop.

Then run:

```bash
docker compose up -d mysql
```

Check the service:

```bash
docker compose ps
```

Wait until MySQL reports:

```text
healthy
```

The initialization script:

```text
docker/init.sql
```

automatically creates the required tables and sample employee records when the MySQL volume is initialized for the first time.

---

## Run the Agent

Run:

```bash
docker compose run --rm app
```

You should see:

```text
Connected to MCP server

Employee MCP Agent started.
Type 'exit' to stop.

You:
```

Example:

```text
You: How much leave does EMP002 have?

Agent:
EMP002 has 6 annual leave days remaining.
```

---

## Test a Write Operation

For example:

```text
Create an IT ticket for EMP001 because the laptop keyboard is not working
```

The agent should request human approval before creating the ticket.

After approval, verify it with:

```text
Show all tickets for EMP001
```

This tests the complete flow:

```text
User
  |
  v
OpenAI
  |
  v
MCP Client
  |
  v
MCP Server
  |
  v
database.py
  |
  v
MySQL Container
```

---

## Stop Docker Compose

When finished:

```bash
docker compose down
```

This stops the Compose environment while preserving the MySQL data stored in the Docker volume.

You can then quit Docker Desktop if it is no longer needed.

---

## Delete the Docker Database

To remove containers **and the persistent MySQL volume**:

```bash
docker compose down -v
```

Use this command carefully.

Deleting the volume removes the containerized database data.

---

## Testing

The project includes automated unit tests using `pytest`.

Run:

```bash
uv run python -m pytest -v
```

The test suite covers areas including:

- GST calculation
- Employee leave balance lookup
- Missing employee handling
- IT ticket creation
- Invalid ticket creation
- Ticket lookup
- Missing ticket handling
- Employee ticket history
- Ticket status updates
- Invalid ticket statuses

Database functions are mocked where appropriate so unit tests do not modify the production/development database.

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
Install Python
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

The CI status is displayed using the badge at the top of this README.

---

## Security

Sensitive configuration is stored using environment variables.

The following should never be committed:

```text
.env
API keys
Database passwords
Other credentials
```

The `.env` file is excluded through `.gitignore` and `.dockerignore`.

The Docker image does not contain the local `.env` file.

Secrets are supplied to the application at runtime.

---

## Development Workflow

A typical development workflow is:

```bash
# Start Docker Desktop
open -a Docker

# Start MySQL
docker compose up -d mysql

# Run the application
docker compose run --rm app

# Run tests
uv run python -m pytest -v

# Stop the containers
docker compose down
```

Then commit changes:

```bash
git add .
git commit -m "Describe your change"
git push
```

GitHub Actions automatically runs the test suite after the push.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| MCP | Tool communication protocol |
| OpenAI | Natural-language reasoning and tool selection |
| MySQL | Persistent application data |
| mysql-connector-python | Python-to-MySQL connectivity |
| python-dotenv | Environment variable management |
| pytest | Automated testing |
| uv | Python dependency and environment management |
| Docker | Application containerization |
| Docker Compose | Multi-container orchestration |
| Git | Version control |
| GitHub | Source repository |
| GitHub Actions | Continuous integration |

---

## Key Engineering Concepts Demonstrated

This project demonstrates:

- Agentic AI workflows
- Model Context Protocol
- LLM function/tool calling
- Dynamic tool discovery
- Multi-turn conversation state
- Human-in-the-loop AI systems
- Relational database integration
- SQL persistence
- Database transaction management
- Separation of application and database layers
- Input validation
- Error handling
- Unit testing
- Dependency mocking
- Environment-based configuration
- Secret management
- Docker containerization
- Multi-container orchestration
- Persistent Docker volumes
- CI/CD fundamentals
- Git/GitHub development workflow

---

## Example Interaction

```text
Employee MCP Agent started.
Type 'exit' to stop.

You: How much leave does EMP002 have?

Tool: get_leave_balance
Arguments: {'employee_id': 'EMP002'}

Agent:
EMP002 has 6 annual leave days remaining.

You: Create an IT ticket for EMP001 because my keyboard is not working

Agent:
Approval is required before creating the ticket.

You: yes

Agent:
The IT support ticket was created.

You: Show all tickets for EMP001

Agent:
Displays the employee's IT support tickets.
```

---

## Future Improvements

Potential future improvements include:

- Web-based frontend
- Authentication and authorization
- Role-based access control
- REST API layer
- More employee-support MCP tools
- Integration tests using containerized MySQL
- Structured application logging
- Observability and monitoring
- Production cloud deployment
- Managed production database
- Additional CI/CD deployment automation

---

## Repository

Project repository:

https://github.com/nakkaganesh/employee-mcp-server

---

## Author

**Nakka Ganesh**

AI / Agentic AI Engineering Portfolio Project