from server import calculate_gst
from server import (
    calculate_gst,
    get_leave_balance,
    create_it_ticket,
    update_ticket_status,
    get_it_ticket,
    get_employee_tickets
)

def test_calculate_gst():
    result = calculate_gst(50000, 18)

    assert result["amount"] == 50000
    assert result["rate"] == 18
    assert result["gst_amount"] == 9000
    assert result["total_amount"] == 59000

from unittest.mock import patch

from server import calculate_gst, get_leave_balance


def test_calculate_gst():
    result = calculate_gst(50000, 18)

    assert result["amount"] == 50000
    assert result["rate"] == 18
    assert result["gst_amount"] == 9000
    assert result["total_amount"] == 59000


@patch("server.get_employee_leave_balance")
def test_get_leave_balance(mock_get_employee):
    mock_get_employee.return_value = {
        "employee_id": "EMP002",
        "leave_balance": 6,
    }

    result = get_leave_balance("EMP002")

    assert result == "Employee EMP002 has 6 annual leave days remaining."

    mock_get_employee.assert_called_once_with("EMP002")


@patch("server.get_employee_leave_balance")
def test_get_leave_balance_employee_not_found(mock_get_employee):
    mock_get_employee.return_value = None

    result = get_leave_balance("EMP999")

    assert result == "Employee 'EMP999' was not found."

    mock_get_employee.assert_called_once_with("EMP999")

@patch("server.insert_ticket")
@patch("server.get_employee_leave_balance")
def test_create_it_ticket(
    mock_get_employee,
    mock_insert_ticket,
):
    # Pretend EMP001 exists
    mock_get_employee.return_value = {
        "employee_id": "EMP001",
        "leave_balance": 10,
    }

    # Pretend MySQL created row ID 3
    mock_insert_ticket.return_value = 3

    result = create_it_ticket(
        "EMP001",
        "Laptop screen is not working",
    )

    assert result == {
        "ticket_id": "IT-1003",
        "employee_id": "EMP001",
        "issue": "Laptop screen is not working",
        "status": "created",
    }

    mock_get_employee.assert_called_once_with("EMP001")

    mock_insert_ticket.assert_called_once_with(
        "EMP001",
        "Laptop screen is not working",
    )


@patch("server.insert_ticket")
@patch("server.get_employee_leave_balance")
def test_create_it_ticket_employee_not_found(
    mock_get_employee,
    mock_insert_ticket,
):
    mock_get_employee.return_value = None

    result = create_it_ticket(
        "EMP999",
        "Laptop is not working",
    )

    assert result == {
        "status": "error",
        "message": "Employee 'EMP999' was not found.",
    }

    # Important: no INSERT should happen
    mock_insert_ticket.assert_not_called()


@patch("server.insert_ticket")
@patch("server.get_employee_leave_balance")
def test_create_it_ticket_empty_issue(
    mock_get_employee,
    mock_insert_ticket,
):
    result = create_it_ticket(
        "EMP001",
        "   ",
    )

    assert result == {
        "status": "error",
        "message": "Issue cannot be empty.",
    }

    # Validation should stop before any database operation
    mock_get_employee.assert_not_called()
    mock_insert_ticket.assert_not_called()


@patch("server.update_ticket_status_db")
def test_update_ticket_status(mock_update_status):
    mock_update_status.return_value = True

    result = update_ticket_status(
        "IT-1001",
        "in progress",
    )

    assert result == {
        "ticket_id": "IT-1001",
        "status": "in_progress",
        "message": "Ticket status updated successfully.",
    }

    mock_update_status.assert_called_once_with(
        1,
        "in_progress",
    )

@patch("server.update_ticket_status_db")
def test_update_ticket_status_invalid_status(mock_update_status):
    result = update_ticket_status(
        "IT-1001",
        "pending",
    )

    assert result == {
        "status": "error",
        "message": (
            "Invalid status. Valid statuses are: "
            "created, in_progress, resolved, closed."
        ),
    }

    # Invalid status must never reach MySQL
    mock_update_status.assert_not_called()


@patch("server.update_ticket_status_db")
def test_update_ticket_status_ticket_not_found(mock_update_status):
    mock_update_status.return_value = False

    result = update_ticket_status(
        "IT-9999",
        "resolved",
    )

    assert result == {
        "status": "error",
        "message": "Ticket 'IT-9999' was not found.",
    }

    mock_update_status.assert_called_once_with(
        8999,
        "resolved",
    )

@patch("server.get_ticket_by_id")
def test_get_it_ticket(mock_get_ticket):
    mock_get_ticket.return_value = {
        "id": 1,
        "employee_id": "EMP001",
        "issue": "Laptop won't start",
        "status": "resolved",
        "created_at": "2026-10-03 10:47:07",
    }

    result = get_it_ticket("IT-1001")

    assert result == {
        "ticket_id": "IT-1001",
        "employee_id": "EMP001",
        "issue": "Laptop won't start",
        "status": "resolved",
        "created_at": "2026-10-03 10:47:07",
    }

    mock_get_ticket.assert_called_once_with(1)


@patch("server.get_ticket_by_id")
def test_get_it_ticket_not_found(mock_get_ticket):
    mock_get_ticket.return_value = None

    result = get_it_ticket("IT-9999")

    assert result == {
        "status": "error",
        "message": "Ticket 'IT-9999' was not found.",
    }

    mock_get_ticket.assert_called_once_with(8999)

@patch("server.get_tickets_by_employee")
@patch("server.get_employee_leave_balance")
def test_get_employee_tickets(
    mock_get_employee,
    mock_get_tickets,
):
    mock_get_employee.return_value = {
        "employee_id": "EMP001",
        "leave_balance": 10,
    }

    mock_get_tickets.return_value = [
        {
            "id": 1,
            "issue": "Laptop won't start",
            "status": "resolved",
            "created_at": "2026-10-03 10:47:07",
        },
        {
            "id": 2,
            "issue": "Keyboard is not working",
            "status": "created",
            "created_at": "2026-10-03 11:00:00",
        },
    ]

    result = get_employee_tickets("EMP001")

    assert result["employee_id"] == "EMP001"
    assert result["ticket_count"] == 2

    assert result["tickets"][0]["ticket_id"] == "IT-1001"
    assert result["tickets"][1]["ticket_id"] == "IT-1002"

    mock_get_employee.assert_called_once_with("EMP001")
    mock_get_tickets.assert_called_once_with("EMP001")

@patch("server.get_tickets_by_employee")
@patch("server.get_employee_leave_balance")
def test_get_employee_tickets_employee_not_found(
    mock_get_employee,
    mock_get_tickets,
):
    mock_get_employee.return_value = None

    result = get_employee_tickets("EMP999")

    assert result == {
        "status": "error",
        "message": "Employee 'EMP999' was not found.",
    }

    mock_get_employee.assert_called_once_with("EMP999")

    # Critical: don't query tickets when employee doesn't exist
    mock_get_tickets.assert_not_called()