"""
Automated Database Setup Script for Library Management System.
Connects to local MySQL, executes schema.sql and sample_data.sql,
and configures the .env file automatically.
"""

import os
import sys
import getpass
import mysql.connector

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')
SAMPLE_DATA_PATH = os.path.join(BASE_DIR, 'database', 'sample_data.sql')
ENV_PATH = os.path.join(BASE_DIR, '.env')

def run_sql_file(cursor, file_path):
    """Reads a SQL file and executes its statements sequentially."""
    print(f"Reading: {os.path.basename(file_path)}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Split by semicolon while ignoring comments and empty statements
    statements = sql_content.split(';')
    executed_count = 0
    for statement in statements:
        stmt = statement.strip()
        # Filter out comments and blank lines
        lines = [line for line in stmt.splitlines() if not line.strip().startswith('--')]
        clean_stmt = '\n'.join(lines).strip()
        if clean_stmt:
            try:
                cursor.execute(clean_stmt)
                executed_count += 1
            except Exception as e:
                # Ignore dropping non-existent tables if any
                if 'Unknown table' not in str(e) and 'Can\'t drop' not in str(e):
                    print(f"Warning on statement: {e}")
    print(f"Executed {executed_count} statements from {os.path.basename(file_path)}.")

def update_env_file(password):
    """Writes the valid MySQL configuration to .env."""
    env_content = f"""# Flask Application Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=college-project-secret-key-993812

# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD={password}
DB_NAME=LibraryDB

# Library Business Logic Configuration
FINE_PER_DAY=1.00
DEFAULT_LOAN_DAYS=14
"""
    with open(ENV_PATH, 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("Updated .env with verified database credentials.")

def main():
    print("=" * 60)
    print("  LIBRARY MANAGEMENT SYSTEM — DATABASE AUTO-SETUP")
    print("=" * 60)

    # Allow password from command line argument if passed
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = input("Enter your MySQL root password (press Enter if none): ")

    print(f"\nTesting connection to MySQL at localhost:3306 with user 'root'...")

    try:
        conn = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password=password,
            autocommit=True
        )
        print("Connected to MySQL Server successfully!")
    except mysql.connector.Error as err:
        print(f"\n[ERROR] Could not connect to MySQL: {err}")
        print("Please verify your root password and try again.")
        sys.exit(1)

    try:
        cursor = conn.cursor()

        # Step 1: Run schema.sql
        run_sql_file(cursor, SCHEMA_PATH)

        # Step 2: Run sample_data.sql
        run_sql_file(cursor, SAMPLE_DATA_PATH)

        # Step 3: Verify created tables
        cursor.execute("USE LibraryDB")
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\nVerified LibraryDB tables ({len(tables)} created):")
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cursor.fetchone()[0]
            print(f"  - {t:<15} : {cnt} rows")

        # Step 4: Update .env file
        update_env_file(password)

        conn.close()
        print("\n" + "=" * 60)
        print("  DATABASE SETUP COMPLETE! All tables and seed data loaded.")
        print("  You can now log in at http://127.0.0.1:5000")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] An error occurred during SQL execution: {e}")
        conn.close()
        sys.exit(1)

if __name__ == '__main__':
    main()
