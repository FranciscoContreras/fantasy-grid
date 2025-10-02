import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
import os
import logging

logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool = None

def init_connection_pool(minconn=2, maxconn=10):
    """
    Initialize the database connection pool.
    
    Args:
        minconn: Minimum number of connections to maintain
        maxconn: Maximum number of connections allowed
    """
    global _connection_pool
    
    if _connection_pool is None:
        try:
            _connection_pool = pool.SimpleConnectionPool(
                minconn,
                maxconn,
                os.getenv('DATABASE_URL')
            )
            logger.info(f"Database connection pool initialized: min={minconn}, max={maxconn}")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

def get_db_connection():
    """Get a database connection from the pool with RealDictCursor for dict-like row access"""
    global _connection_pool
    
    # Initialize pool if not already done
    if _connection_pool is None:
        init_connection_pool()
    
    try:
        conn = _connection_pool.getconn()
        # Set cursor factory for dict-like access
        conn.cursor_factory = RealDictCursor
        return conn
    except Exception as e:
        logger.error(f"Failed to get connection from pool: {e}")
        raise

def return_db_connection(conn):
    """Return a connection to the pool"""
    global _connection_pool
    
    if _connection_pool is not None and conn is not None:
        _connection_pool.putconn(conn)

def close_all_connections():
    """Close all connections in the pool (for cleanup)"""
    global _connection_pool
    
    if _connection_pool is not None:
        _connection_pool.closeall()
        logger.info("All database connections closed")

def init_db():
    """Initialize the database schema from schema.sql"""
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schema.sql')
        with open(schema_path, 'r') as f:
            cursor.execute(f.read())

        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database initialization failed: {e}")
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            return_db_connection(conn)

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a database query using connection pool

    Args:
        query: SQL query string
        params: Query parameters tuple
        fetch_one: Return single row
        fetch_all: Return all rows

    Returns:
        Query results or None
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, params or ())

        # Auto-detect RETURNING clause
        is_returning = 'RETURNING' in query.upper()
        is_modification = any(keyword in query.upper() for keyword in ['INSERT', 'UPDATE', 'DELETE'])

        if fetch_one or (is_returning and 'INSERT' in query.upper()):
            result = cursor.fetchone()
            if result:
                result = [result]  # Wrap in list for consistency
        elif fetch_all or 'SELECT' in query.upper() or is_returning:
            result = cursor.fetchall()
        else:
            result = None

        # Commit if this was a modification query (INSERT, UPDATE, DELETE)
        if is_modification:
            conn.commit()

        return result
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database query failed: {e}")
        raise e
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            return_db_connection(conn)
