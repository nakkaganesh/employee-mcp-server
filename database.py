import os

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


def get_db_connection():
    """Create and return a connection to the MySQL database."""

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

    return connection
def get_employee_leave_balance(employee_id: str):
    """Get an employee's leave information from MySQL."""

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

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

def get_ticket_by_id(ticket_number: int):
    """Get an IT ticket from MySQL by its database ID."""

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

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

def get_tickets_by_employee(employee_id: str):
    """Get all IT tickets for an employee from MySQL."""

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, issue, status, created_at
            FROM tickets
            WHERE employee_id = %s
            ORDER BY created_at DESC
            """,
            (employee_id,),
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def insert_ticket(employee_id: str, issue: str):
    """Create an IT support ticket in MySQL."""

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO tickets (employee_id, issue, status)
            VALUES (%s, %s, %s)
            """,
            (employee_id, issue, "created"),
        )

        connection.commit()

        return cursor.lastrowid

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def update_ticket_status_db(ticket_number: int, status: str) -> bool:
    """Update an IT ticket status in MySQL."""

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE tickets
            SET status = %s
            WHERE id = %s
            """,
            (status, ticket_number),
        )

        updated = cursor.rowcount > 0

        connection.commit()

        return updated

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    connection = get_db_connection()

    if connection.is_connected():
        print("Connected to MySQL successfully.")

    connection.close()