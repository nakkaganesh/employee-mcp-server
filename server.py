from mcp.server.mcpserver import MCPServer

mcp=MCPServer("employee MCP server")


@mcp.tool()
def get_leave_balance(employee_id: str) -> str:
    """Get the remaining leave balance of an employee."""

    employees = [
        {"employee_id": "EMP001", "leave_balance": 12},
        {"employee_id": "EMP002", "leave_balance": 6},
        {"employee_id": "EMP003", "leave_balance": 8},
    ]

    employee_id = employee_id.upper().strip()

    employee = next(
        (
            emp
            for emp in employees
            if emp["employee_id"] == employee_id
        ),
        None,
    )

    if employee is None:
        return f"Employee '{employee_id}' was not found."

    return (
        f"Employee {employee_id} has "
        f"{employee['leave_balance']} annual leave days remaining."
    )

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
def create_it_ticket(
    employee_id: str,
    issue: str,
) -> dict:
    """Create an IT support ticket for an employee."""

    ticket_id = "IT-1001"

    return {
        "ticket_id": ticket_id,
        "employee_id": employee_id.upper(),
        "issue": issue,
        "status": "created",
    }


if __name__ == "__main__":
    mcp.run()