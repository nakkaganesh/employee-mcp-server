from mcp.server.mcpserver import MCPServer
from database import get_db_connection


mcp=MCPServer("employee MCP server")


@mcp.tool()
def get_leave_balance(employee_id: str) -> str:
    """Get the remaining leave balance of an employee."""

    employee_id = employee_id.upper().strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT employee_id, leave_balance
            FROM employees
            WHERE employee_id = %s
            """,
            (employee_id,),
        )

        employee = cursor.fetchone()

        if employee is None:
            return f"Employee '{employee_id}' was not found."

        return (
            f"Employee {employee['employee_id']} has "
            f"{employee['leave_balance']} annual leave days remaining."
        )

    finally:
        cursor.close()
        connection.close()

@mcp.tool()
def calculate_gst(amount:float,rate:float)->dict:
    """ calculate gst for given amount and tax rate"""
    gst_amount=amount*rate/100

    total_amount=amount+gst_amount


    return {
        "amount": amount,
        "rate": rate,
        "gst_amount": gst_amount,
        "total_amount": total_amount,
    }
@mcp.tool()
def create_it_ticket(employee_id: str,issue: str) -> dict:
    """Create an IT support ticket for an employee."""

    employee_id = employee_id.upper().strip()
    issue = issue.strip()

    if not issue:
        return {
            "status": "error",
            "message": "Issue description cannot be empty.",
        }

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check whether the employee exists
        cursor.execute(
            """
            SELECT employee_id
            FROM employees
            WHERE employee_id = %s
            """,
            (employee_id,),
        )

        employee = cursor.fetchone()

        if employee is None:
            return {
                "status": "error",
                "message": f"Employee '{employee_id}' was not found.",
            }

        # Create the ticket
        cursor.execute(
            """
            INSERT INTO tickets (employee_id, issue, status)
            VALUES (%s, %s, %s)
            """,
            (employee_id, issue, "created"),
        )

        connection.commit()

        ticket_number = cursor.lastrowid
        ticket_id = f"IT-{1000 + ticket_number}"

        return {
            "ticket_id": ticket_id,
            "employee_id": employee_id,
            "issue": issue,
            "status": "created",
        }

    finally:
        cursor.close()
        connection.close()

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

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, employee_id, issue, status, created_at
            FROM tickets
            WHERE id = %s
            """,
            (ticket_number,),
        )

        ticket = cursor.fetchone()

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

    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    mcp.run()