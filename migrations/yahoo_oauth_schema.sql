-- Yahoo OAuth Integration Migration
-- Created: 2025-10-04
-- Purpose: Add Yahoo Fantasy OAuth support and roster import tracking

-- Yahoo OAuth tokens table (secure token storage)
CREATE TABLE IF NOT EXISTS yahoo_oauth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_type VARCHAR(20) DEFAULT 'bearer',
    expires_at TIMESTAMP NOT NULL,
    yahoo_guid VARCHAR(100), -- Yahoo user identifier
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Add Yahoo tracking columns to rosters table
ALTER TABLE rosters
    ADD COLUMN IF NOT EXISTS yahoo_team_key VARCHAR(100),
    ADD COLUMN IF NOT EXISTS yahoo_league_key VARCHAR(100),
    ADD COLUMN IF NOT EXISTS last_synced_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS import_source VARCHAR(20) DEFAULT 'manual'; -- 'manual' or 'yahoo'

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_yahoo_tokens_user ON yahoo_oauth_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_yahoo_tokens_expires ON yahoo_oauth_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_rosters_yahoo_team ON rosters(yahoo_team_key) WHERE yahoo_team_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_rosters_yahoo_league ON rosters(yahoo_league_key) WHERE yahoo_league_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_rosters_import_source ON rosters(import_source);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_yahoo_token_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at on yahoo_oauth_tokens
DROP TRIGGER IF EXISTS update_yahoo_oauth_tokens_timestamp ON yahoo_oauth_tokens;
CREATE TRIGGER update_yahoo_oauth_tokens_timestamp
    BEFORE UPDATE ON yahoo_oauth_tokens
    FOR EACH ROW
    EXECUTE FUNCTION update_yahoo_token_timestamp();

-- Comments for documentation
COMMENT ON TABLE yahoo_oauth_tokens IS 'Stores Yahoo OAuth 2.0 tokens for fantasy roster import';
COMMENT ON COLUMN yahoo_oauth_tokens.access_token IS 'Yahoo API access token (expires after 1 hour)';
COMMENT ON COLUMN yahoo_oauth_tokens.refresh_token IS 'Token to refresh access token';
COMMENT ON COLUMN yahoo_oauth_tokens.yahoo_guid IS 'Yahoo user GUID for API calls';
COMMENT ON COLUMN rosters.yahoo_team_key IS 'Yahoo team key (e.g., nfl.l.12345.t.1)';
COMMENT ON COLUMN rosters.yahoo_league_key IS 'Yahoo league key (e.g., nfl.l.12345)';
COMMENT ON COLUMN rosters.last_synced_at IS 'Last time roster was synced from Yahoo';
COMMENT ON COLUMN rosters.import_source IS 'How roster was created: manual or yahoo';
