#!/usr/bin/env python3
"""
Initialize Yahoo OAuth database schema on Heroku
"""
from app.database import execute_query
import logging

logger = logging.getLogger(__name__)

def init_yahoo_schema():
    """Initialize Yahoo OAuth database tables"""

    # Yahoo OAuth states table
    oauth_states_sql = """
    CREATE TABLE IF NOT EXISTS yahoo_oauth_states (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        state VARCHAR(255) NOT NULL UNIQUE,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        UNIQUE(user_id)
    );
    """

    # Yahoo tokens table
    tokens_sql = """
    CREATE TABLE IF NOT EXISTS yahoo_tokens (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        access_token TEXT NOT NULL,
        refresh_token TEXT,
        expires_at TIMESTAMP,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
        UNIQUE(user_id)
    );
    """

    # Import history table
    history_sql = """
    CREATE TABLE IF NOT EXISTS yahoo_import_history (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        roster_id INTEGER NOT NULL REFERENCES rosters(id) ON DELETE CASCADE,
        yahoo_team_key VARCHAR(255) NOT NULL,
        yahoo_league_name VARCHAR(255),
        players_imported INTEGER DEFAULT 0,
        import_status VARCHAR(50) DEFAULT 'completed',
        imported_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    """

    # Indexes
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_yahoo_oauth_states_user_id ON yahoo_oauth_states(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_yahoo_oauth_states_state ON yahoo_oauth_states(state);",
        "CREATE INDEX IF NOT EXISTS idx_yahoo_oauth_states_created_at ON yahoo_oauth_states(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_yahoo_tokens_user_id ON yahoo_tokens(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_yahoo_tokens_expires_at ON yahoo_tokens(expires_at);",
        "CREATE INDEX IF NOT EXISTS idx_yahoo_import_history_user_id ON yahoo_import_history(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_yahoo_import_history_roster_id ON yahoo_import_history(roster_id);",
        "CREATE INDEX IF NOT EXISTS idx_yahoo_import_history_imported_at ON yahoo_import_history(imported_at);"
    ]

    # Cleanup function
    cleanup_function_sql = """
    CREATE OR REPLACE FUNCTION cleanup_old_yahoo_oauth_states()
    RETURNS INTEGER AS $$
    DECLARE
        deleted_count INTEGER;
    BEGIN
        DELETE FROM yahoo_oauth_states
        WHERE created_at < NOW() - INTERVAL '1 hour';

        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RETURN deleted_count;
    END;
    $$ LANGUAGE plpgsql;
    """

    try:
        print("Creating Yahoo OAuth tables...")

        # Create tables
        execute_query(oauth_states_sql)
        print("✓ yahoo_oauth_states table created")

        execute_query(tokens_sql)
        print("✓ yahoo_tokens table created")

        execute_query(history_sql)
        print("✓ yahoo_import_history table created")

        # Create indexes
        for index_sql in indexes_sql:
            execute_query(index_sql)
        print("✓ All indexes created")

        # Create cleanup function
        execute_query(cleanup_function_sql)
        print("✓ Cleanup function created")

        print("\n🎉 Yahoo OAuth schema initialization complete!")
        print("Users can now authenticate with Yahoo and import their rosters.")

        return True

    except Exception as e:
        print(f"❌ Error initializing Yahoo schema: {e}")
        logger.error(f"Yahoo schema initialization failed: {e}")
        return False

if __name__ == "__main__":
    init_yahoo_schema()