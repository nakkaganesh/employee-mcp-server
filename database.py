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

if __name__ == "__main__":
    connection = get_db_connection()

    if connection.is_connected():
        print("Connected to MySQL successfully.")

    connection.close()