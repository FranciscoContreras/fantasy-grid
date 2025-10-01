import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db_connection():
    """Get a database connection with RealDictCursor for dict-like row access"""
    conn = psycopg2.connect(
        os.getenv('DATABASE_URL'),
        cursor_factory=RealDictCursor
    )
    return conn

def init_db():
    """Initialize the database schema from schema.sql"""
    conn = get_db_connection()
    cursor = conn.cursor()

    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schema.sql')
    with open(schema_path, 'r') as f:
        cursor.execute(f.read())

    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized successfully")

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a database query

    Args:
        query: SQL query string
        params: Query parameters tuple
        fetch_one: Return single row
        fetch_all: Return all rows

    Returns:
        Query results or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, params or ())

        # Auto-detect RETURNING clause
        is_returning = 'RETURNING' in query.upper()

        if fetch_one or (is_returning and 'INSERT' in query.upper()):
            result = cursor.fetchone()
            if result:
                result = [result]  # Wrap in list for consistency
        elif fetch_all or 'SELECT' in query.upper() or is_returning:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = None

        if result is None or (isinstance(result, list) and len(result) == 0):
            conn.commit()

        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
