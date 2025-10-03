CREATE TABLE players (
    player_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(10) NOT NULL,
    team VARCHAR(10) NOT NULL,
    avg_points DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE player_stats (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(50) REFERENCES players(player_id),
    week INT NOT NULL,
    season INT NOT NULL,
    points DECIMAL(5,2),
    opponent VARCHAR(10),
    weather_conditions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    scoring_type VARCHAR(20),
    roster_slots JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes for common query patterns
CREATE INDEX idx_player_stats_player ON player_stats(player_id);
CREATE INDEX idx_player_stats_week ON player_stats(week, season);
CREATE INDEX idx_players_position ON players(position);  -- For position-based filtering
CREATE INDEX idx_players_team ON players(team);  -- For team-based queries
CREATE INDEX idx_player_stats_opponent ON player_stats(opponent);  -- For opponent-based analysis
CREATE INDEX idx_player_stats_composite ON player_stats(player_id, week, season);  -- Composite for player weekly stats
CREATE INDEX idx_user_preferences_user ON user_preferences(user_id);  -- For user lookups
