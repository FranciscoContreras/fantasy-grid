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

CREATE INDEX idx_player_stats_player ON player_stats(player_id);
CREATE INDEX idx_player_stats_week ON player_stats(week, season);
