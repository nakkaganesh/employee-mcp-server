from mcp.server.mcpserver import MCPServer

mcp=MCPServer("employee MCP server")

@mcp.tool()

def get_leave_balance(employee_id : str)-> str :
    """ Get the remaining leave balance of an employee"""

    leave_balance={
        "EMP001": 12,
        "EMP002": 6,
        "EMP003": 23
    }
    days=leave_balance.get(employee_id.upper())

    if days is None:
        return "employee not found"

    return (f"Employee {employee_id.upper()} "f"has {days} annual leave days remaining.")

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