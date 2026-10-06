from mcp.server.mcpserver import MCPServer
from database import get_employee_leave_balance,get_ticket_by_id,get_tickets_by_employee,insert_ticket,update_ticket_status_db

import mysql.connector

mcp=MCPServer("employee MCP server")


@mcp.tool()
def get_leave_balance(employee_id: str) -> str:
    """Get the remaining leave balance of an employee."""

    employee_id = employee_id.upper().strip()

    employee = get_employee_leave_balance(employee_id)

    if employee is None:
        return f"Employee '{employee_id}' was not found."

    return (
        f"Employee {employee['employee_id']} has "
        f"{employee['leave_balance']} annual leave days remaining."
    )

@mcp.tool()
def create_it_ticket(
    employee_id: str,
    issue: str,
) -> dict:
    """Create an IT support ticket for an employee."""

    employee_id = employee_id.upper().strip()
    issue = issue.strip()

    if not issue:
        return {
            "status": "error",
            "message": "Issue cannot be empty.",
        }

    employee = get_employee_leave_balance(employee_id)

    if employee is None:
        return {
            "status": "error",
            "message": f"Employee '{employee_id}' was not found.",
        }

    try:
        ticket_number = insert_ticket(employee_id, issue)

        return {
            "ticket_id": f"IT-{1000 + ticket_number}",
            "employee_id": employee_id,
            "issue": issue,
            "status": "created",
        }

    except mysql.connector.Error as error:
        return {
            "status": "error",
            "message": f"Database error: {error}",
        }

@mcp.tool()
def get_it_ticket(ticket_id: str) -> dict:
    """Get the details of an IT support ticket."""

    ticket_id = ticket_id.upper().strip()

    if not ticket_id.startswith("IT-"):
        return {
            "status": "error",
            "message": "Invalid ticket ID format.",
        }

    try:
        ticket_number = int(ticket_id.removeprefix("IT-")) - 1000
    except ValueError:
        return {
            "status": "error",
            "message": "Invalid ticket ID format.",
        }

    ticket = get_ticket_by_id(ticket_number)

    if ticket is None:
        return {
            "status": "error",
            "message": f"Ticket '{ticket_id}' was not found.",
        }

    return {
        "ticket_id": f"IT-{1000 + ticket['id']}",
        "employee_id": ticket["employee_id"],
        "issue": ticket["issue"],
        "status": ticket["status"],
        "created_at": str(ticket["created_at"]),
    }

@mcp.tool()
def update_ticket_status(
    ticket_id: str,
    status: str,
) -> dict:
    """Update the status of an IT support ticket."""

    ticket_id = ticket_id.upper().strip()
    status = status.lower().strip().replace(" ", "_")

    valid_statuses = {
        "created",
        "in_progress",
        "resolved",
        "closed",
    }

    if status not in valid_statuses:
        return {
            "status": "error",
            "message": (
                "Invalid status. Valid statuses are: "
                "created, in_progress, resolved, closed."
            ),
        }

    if not ticket_id.startswith("IT-"):
        return {
            "status": "error",
            "message": "Invalid ticket ID format.",
        }

    try:
        ticket_number = int(ticket_id.removeprefix("IT-")) - 1000
    except ValueError:
        return {
            "status": "error",
            "message": "Invalid ticket ID format.",
        }

    try:
        updated = update_ticket_status_db(
            ticket_number,
            status,
        )

        if not updated:
            return {
                "status": "error",
                "message": f"Ticket '{ticket_id}' was not found.",
            }

        return {
            "ticket_id": ticket_id,
            "status": status,
            "message": "Ticket status updated successfully.",
        }

    except mysql.connector.Error as error:
        return {
            "status": "error",
            "message": f"Database error: {error}",
        }
@mcp.tool()
def get_employee_tickets(employee_id: str) -> dict:
    """Get all IT support tickets for an employee."""

    employee_id = employee_id.upper().strip()

    # Check whether employee exists
    employee = get_employee_leave_balance(employee_id)

    if employee is None:
        return {
            "status": "error",
            "message": f"Employee '{employee_id}' was not found.",
        }

    # Get tickets from database.py
    tickets = get_tickets_by_employee(employee_id)

    formatted_tickets = []

    for ticket in tickets:
        formatted_tickets.append(
            {
                "ticket_id": f"IT-{1000 + ticket['id']}",
                "issue": ticket["issue"],
                "status": ticket["status"],
                "created_at": str(ticket["created_at"]),
            }
        )

    return {
        "employee_id": employee_id,
        "ticket_count": len(formatted_tickets),
        "tickets": formatted_tickets,
    }

if __name__ == "__main__":
    mcp.run()