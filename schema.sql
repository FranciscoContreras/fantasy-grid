CREATE TABLE players (
    player_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(10) NOT NULL,
    team VARCHAR(10) NOT NULL,
    avg_points DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE player_stats (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(50) REFERENCES players(player_id),
    week INT NOT NULL,
    season INT NOT NULL,
    points DECIMAL(5,2),
    opponent VARCHAR(10),
    weather_conditions TEXT,
    passing_yards INT,
    passing_tds INT,
    rushing_yards INT,
    rushing_tds INT,
    receiving_yards INT,
    receiving_tds INT,
    receptions INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    scoring_type VARCHAR(20) DEFAULT 'PPR',
    roster_slots JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analysis_history (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(50),
    opponent VARCHAR(10),
    matchup_score DECIMAL(5,2),
    weather_impact DECIMAL(5,2),
    ai_grade VARCHAR(5),
    predicted_points DECIMAL(5,2),
    recommendation VARCHAR(20),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_player_stats_player ON player_stats(player_id);
CREATE INDEX idx_player_stats_week ON player_stats(week, season);
CREATE INDEX idx_analysis_history_player ON analysis_history(player_id);
CREATE INDEX idx_analysis_history_date ON analysis_history(analyzed_at);
