"""
Database connection and query execution helper module for LibraryDB.
Strictly interfaces with MySQL 8.x using mysql-connector-python.
"""

from contextlib import contextmanager
import mysql.connector
from mysql.connector import Error, errorcode
from config import Config

def get_connection_params():
    """Returns database connection configuration dictionary."""
    return {
        'host': Config.DB_HOST,
        'port': Config.DB_PORT,
        'user': Config.DB_USER,
        'password': Config.DB_PASSWORD,
        'database': Config.DB_NAME,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'autocommit': False
    }

def get_raw_connection():
    """
    Establishes and returns a new MySQL database connection.
    Raises descriptive RuntimeError if MySQL is offline or misconfigured.
    """
    params = get_connection_params()
    try:
        conn = mysql.connector.connect(**params)
        return conn
    except Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            msg = f"Database authentication failed: Invalid username or password for user '{params['user']}'."
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            msg = f"Database '{params['database']}' does not exist. Please run 'database/schema.sql' first."
        elif err.errno in (errorcode.CR_CONN_HOST_ERROR, 2003):
            msg = f"Cannot connect to MySQL server at {params['host']}:{params['port']}. Ensure MySQL service is running."
        else:
            msg = f"MySQL Error [{err.errno}]: {err.msg}"
        raise RuntimeError(msg) from err

@contextmanager
def get_db_connection():
    """
    Context manager that yields a managed MySQL connection and ensures
    it is closed upon completion.
    """
    conn = get_raw_connection()
    try:
        yield conn
    finally:
        if conn.is_connected():
            conn.close()

@contextmanager
def transaction():
    """
    Context manager for atomic ACID transactions.
    Automatically commits on normal completion or rolls back on any error.
    Yields (cursor, connection).
    """
    conn = get_raw_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        yield cursor, conn
        conn.commit()
    except Exception:
        if conn.is_connected():
            conn.rollback()
        raise
    finally:
        cursor.close()
        if conn.is_connected():
            conn.close()

def execute_query(query, params=None, fetchone=False, dictionary=True):
    """
    Executes a parameterized SELECT query and returns the fetched results.
    Guarantees parameterized query execution to prevent SQL injection.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=dictionary)
        try:
            cursor.execute(query, params or ())
            if fetchone:
                return cursor.fetchone()
            return cursor.fetchall()
        finally:
            cursor.close()

def execute_non_query(query, params=None, get_last_id=False):
    """
    Executes a parameterized INSERT, UPDATE, or DELETE statement.
    Commits changes and returns affected row count (and optionally last_insert_id).
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            if get_last_id:
                return cursor.rowcount, cursor.lastrowid
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

def check_connection():
    """
    Tests whether the MySQL database is reachable and initialized.
    Returns (is_connected: bool, message: str).
    """
    try:
        with get_db_connection() as conn:
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("SELECT DATABASE(), VERSION()")
                db_name, version = cursor.fetchone()
                cursor.close()
                return True, f"Connected to MySQL {version} (Database: {db_name})"
    except Exception as e:
        return False, str(e)
    return False, "Unknown connection status."
