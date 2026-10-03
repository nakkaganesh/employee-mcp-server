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

if __name__ == "__main__":
    connection = get_db_connection()

    if connection.is_connected():
        print("Connected to MySQL successfully.")

    connection.close()