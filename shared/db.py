import os
import pyodbc


def get_connection():
    connection_string = os.getenv("SQL_CONNECTION_STRING")

    if not connection_string:
        raise Exception("SQL_CONNECTION_STRING is not configured")

    return pyodbc.connect(connection_string)