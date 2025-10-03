"""
Database connection utilities
"""
import psycopg2
import os
from contextlib import contextmanager

def get_db():
    """
    Get database connection

    Returns:
        psycopg2 connection object
    """
    return psycopg2.connect(os.getenv('DATABASE_URL'))


@contextmanager
def get_db_cursor():
    """
    Context manager for database cursor

    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
