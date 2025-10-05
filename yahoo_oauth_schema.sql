-- Yahoo OAuth Integration Schema
-- Add these tables to support Yahoo Fantasy Sports integration

-- Table to store OAuth states for CSRF protection
CREATE TABLE IF NOT EXISTS yahoo_oauth_states (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    state VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)  -- One active state per user
);

-- Table to store Yahoo OAuth tokens
CREATE TABLE IF NOT EXISTS yahoo_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)  -- One token set per user
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_yahoo_oauth_states_user_id ON yahoo_oauth_states(user_id);
CREATE INDEX IF NOT EXISTS idx_yahoo_oauth_states_state ON yahoo_oauth_states(state);
CREATE INDEX IF NOT EXISTS idx_yahoo_oauth_states_created_at ON yahoo_oauth_states(created_at);

CREATE INDEX IF NOT EXISTS idx_yahoo_tokens_user_id ON yahoo_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_yahoo_tokens_expires_at ON yahoo_tokens(expires_at);

-- Optional: Table to track Yahoo import history
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

CREATE INDEX IF NOT EXISTS idx_yahoo_import_history_user_id ON yahoo_import_history(user_id);
CREATE INDEX IF NOT EXISTS idx_yahoo_import_history_roster_id ON yahoo_import_history(roster_id);
CREATE INDEX IF NOT EXISTS idx_yahoo_import_history_imported_at ON yahoo_import_history(imported_at);

-- Function to cleanup old OAuth states (run periodically)
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