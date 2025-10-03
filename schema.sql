-- Users table for authentication
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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

-- Rosters table for user fantasy teams
CREATE TABLE rosters (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    league_name VARCHAR(100),
    scoring_type VARCHAR(20) DEFAULT 'PPR',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Roster players mapping
CREATE TABLE roster_players (
    id SERIAL PRIMARY KEY,
    roster_id INT REFERENCES rosters(id) ON DELETE CASCADE,
    player_id VARCHAR(50),
    player_name VARCHAR(100) NOT NULL,
    position VARCHAR(10) NOT NULL,
    team VARCHAR(10) NOT NULL,
    roster_slot VARCHAR(20) NOT NULL, -- QB, RB1, RB2, WR1, WR2, WR3, TE, FLEX, K, DEF, BENCH
    is_starter BOOLEAN DEFAULT true,
    injury_status VARCHAR(20), -- OUT, DOUBTFUL, QUESTIONABLE, PROBABLE, HEALTHY
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weekly matchups between two rosters
CREATE TABLE matchups (
    id SERIAL PRIMARY KEY,
    week INT NOT NULL,
    season INT NOT NULL,
    user_roster_id INT REFERENCES rosters(id) ON DELETE CASCADE,
    opponent_roster_id INT REFERENCES rosters(id) ON DELETE CASCADE,
    user_roster_name VARCHAR(100),
    opponent_roster_name VARCHAR(100),
    analyzed BOOLEAN DEFAULT false,
    analyzed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Matchup analysis results
CREATE TABLE matchup_analysis (
    id SERIAL PRIMARY KEY,
    matchup_id INT REFERENCES matchups(id) ON DELETE CASCADE,
    player_id VARCHAR(50),
    player_name VARCHAR(100) NOT NULL,
    position VARCHAR(10) NOT NULL,
    is_user_player BOOLEAN NOT NULL, -- true for user, false for opponent
    opponent_team VARCHAR(10),
    matchup_score DECIMAL(5,2),
    projected_points DECIMAL(5,2),
    ai_grade VARCHAR(5),
    recommendation VARCHAR(20), -- START, SIT, CONSIDER
    injury_impact TEXT,
    confidence_score DECIMAL(5,2), -- 0-100
    reasoning TEXT,
    analysis_status VARCHAR(20) DEFAULT 'completed',
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_player_stats_player ON player_stats(player_id);
CREATE INDEX idx_player_stats_week ON player_stats(week, season);
CREATE INDEX idx_analysis_history_player ON analysis_history(player_id);
CREATE INDEX idx_analysis_history_date ON analysis_history(analyzed_at);
CREATE INDEX idx_rosters_user ON rosters(user_id);
CREATE INDEX idx_roster_players_roster ON roster_players(roster_id);
CREATE INDEX idx_roster_players_roster_position ON roster_players(roster_id, position);
CREATE INDEX idx_matchups_week ON matchups(week, season);
CREATE INDEX idx_matchup_analysis_matchup ON matchup_analysis(matchup_id);
CREATE INDEX idx_matchup_analysis_status ON matchup_analysis(analysis_status);
