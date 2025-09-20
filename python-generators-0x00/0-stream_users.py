#!/usr/bin/env python3
"""
Generator function to stream user data from MySQL database one row at a time.
"""

import mysql.connector
from mysql.connector import Error


def stream_users():
    """
    Generator function that streams rows from the user_data table one by one.

    Yields:
        dict: A dictionary containing user data with keys: user_id, name, email, age
    """
    connection = None
    cursor = None

    try:
        # Connect to the ALX_prodev database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='ALX_prodev'
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Execute query to fetch all users
            cursor.execute("SELECT * FROM user_data")

            # Stream rows one by one using the generator
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                yield row

    except Error as e:
        print(f"Database error: {e}")
        yield None
    except Exception as e:
        print(f"Unexpected error: {e}")
        yield None
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
