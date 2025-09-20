#!/usr/bin/env python3
"""
Database seeding script for ALX_prodev database.
This script creates the database, table, and populates it with sample data.
"""

import mysql.connector
import csv
import uuid
from mysql.connector import Error


def connect_db():
    """
    Connects to the MySQL database server.

    Returns:
        connection: MySQL database connection object
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  
            password=''   
        )
        if connection.is_connected():
            print("Successfully connected to MySQL server")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def create_database(connection):
    """
    Creates the ALX_prodev database if it does not exist.

    Args:
        connection: MySQL database connection object
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database 'ALX_prodev' created successfully or already exists")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")


def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL.

    Returns:
        connection: MySQL database connection object connected to ALX_prodev
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  
            password='',  
            database='ALX_prodev'
        )
        if connection.is_connected():
            print("Successfully connected to ALX_prodev database")
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None


def create_table(connection):
    """
    Creates the user_data table if it does not exist with the required fields.

    Args:
        connection: MySQL database connection object
    """
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(5,2) NOT NULL,
            INDEX idx_user_id (user_id)
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'user_data' created successfully or already exists")
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")


def insert_data(connection, data):
    """
    Inserts data into the database if it does not exist.

    Args:
        connection: MySQL database connection object
        data: List of tuples containing user data
    """
    try:
        cursor = connection.cursor()

        # Check if user_id already exists
        for user in data:
            user_id = user[0]
            cursor.execute("SELECT COUNT(*) FROM user_data WHERE user_id = %s", (user_id,))
            count = cursor.fetchone()[0]

            if count == 0:
                insert_query = """
                INSERT INTO user_data (user_id, name, email, age)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_query, user)
                print(f"Inserted user: {user[1]}")
            else:
                print(f"User with ID {user_id} already exists, skipping...")

        connection.commit()
        cursor.close()
        print("Data insertion completed")
    except Error as e:
        print(f"Error inserting data: {e}")


def load_data_from_csv(csv_file_path):
    """
    Loads data from CSV file.

    Args:
        csv_file_path: Path to the CSV file

    Returns:
        List of tuples containing user data
    """
    data = []
    try:
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            for row in csv_reader:
                if len(row) == 4:  # Ensure we have all 4 fields
                    data.append(tuple(row))
        print(f"Loaded {len(data)} records from CSV file")
        return data
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file_path}' not found")
        return []
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []


def main():
    """
    Main function to execute the database seeding process.
    """
    # Step 1: Connect to MySQL server
    connection = connect_db()
    if not connection:
        return

    try:
        # Step 2: Create database
        create_database(connection)

        # Step 3: Connect to ALX_prodev database
        prodev_connection = connect_to_prodev()
        if not prodev_connection:
            return

        # Step 4: Create table
        create_table(prodev_connection)

        # Step 5: Load data from CSV
        csv_file_path = 'user_data.csv'
        data = load_data_from_csv(csv_file_path)

        if data:
            # Step 6: Insert data
            insert_data(prodev_connection, data)
        else:
            print("No data to insert")

    except Error as e:
        print(f"Database error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL server connection closed")

        if 'prodev_connection' in locals() and prodev_connection.is_connected():
            prodev_connection.close()
            print("ALX_prodev database connection closed")


if __name__ == "__main__":
    main()
