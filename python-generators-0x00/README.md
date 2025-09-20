# Database Seeding Script

This script sets up a MySQL database called `ALX_prodev` with a `user_data` table and populates it with sample data from a CSV file.

## Prerequisites

1. MySQL Server installed and running
2. Python 3.x installed
3. MySQL Connector for Python installed

## Installation

1. Install the required Python package:
```bash
pip install -r requirements.txt
```

## Database Setup

The script will create:
- Database: `ALX_prodev`
- Table: `user_data` with the following structure:
  - `user_id` (CHAR(36) PRIMARY KEY, Indexed)
  - `name` (VARCHAR(255) NOT NULL)
  - `email` (VARCHAR(255) NOT NULL)
  - `age` (DECIMAL(5,2) NOT NULL)

## Usage

1. Update the database credentials in the script if needed:
   - Modify the `user` and `password` parameters in the connection functions
   - Default values are set to `root` user with no password

2. Run the script:
```bash
python seed.py
```

## Functions

- `connect_db()`: Connects to the MySQL database server
- `create_database(connection)`: Creates the ALX_prodev database if it doesn't exist
- `connect_to_prodev()`: Connects to the ALX_prodev database
- `create_table(connection)`: Creates the user_data table if it doesn't exist
- `insert_data(connection, data)`: Inserts data into the database if it doesn't already exist
- `load_data_from_csv(csv_file_path)`: Loads data from the CSV file
- `main()`: Orchestrates the entire database seeding process

## Sample Data

The script uses sample data from `user_data.csv` which contains 10 sample user records with UUIDs, names, emails, and ages.

## Notes

- The script checks for existing records before inserting to avoid duplicates
- All database operations are wrapped in try-catch blocks for error handling
- Connections are properly closed in the finally block
- The script provides detailed console output for monitoring progress
