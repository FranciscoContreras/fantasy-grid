-- Rosters table for user fantasy teams
CREATE TABLE IF NOT EXISTS rosters (
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
CREATE TABLE IF NOT EXISTS roster_players (
    id SERIAL PRIMARY KEY,
    roster_id INT REFERENCES rosters(id) ON DELETE CASCADE,
    player_id VARCHAR(50),
    player_name VARCHAR(100) NOT NULL,
    position VARCHAR(10) NOT NULL,
    team VARCHAR(10) NOT NULL,
    roster_slot VARCHAR(20) NOT NULL,
    is_starter BOOLEAN DEFAULT true,
    injury_status VARCHAR(20),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weekly matchups between two rosters
CREATE TABLE IF NOT EXISTS matchups (
    id SERIAL PRIMARY KEY,
    week INT NOT NULL,
    season INT NOT NULL,
    user_roster_id INT REFERENCES rosters(id) ON DELETE CASCADE,
    opponent_roster_id INT REFERENCES rosters(id) ON DELETE CASCADE,
    analyzed BOOLEAN DEFAULT false,
    analyzed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Matchup analysis results
CREATE TABLE IF NOT EXISTS matchup_analysis (
    id SERIAL PRIMARY KEY,
    matchup_id INT REFERENCES matchups(id) ON DELETE CASCADE,
    player_id VARCHAR(50),
    player_name VARCHAR(100) NOT NULL,
    position VARCHAR(10) NOT NULL,
    is_user_player BOOLEAN NOT NULL,
    opponent_team VARCHAR(10),
    matchup_score DECIMAL(5,2),
    projected_points DECIMAL(5,2),
    ai_grade VARCHAR(5),
    recommendation VARCHAR(20),
    injury_impact TEXT,
    confidence_score DECIMAL(5,2),
    reasoning TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_rosters_user ON rosters(user_id);
CREATE INDEX IF NOT EXISTS idx_roster_players_roster ON roster_players(roster_id);
CREATE INDEX IF NOT EXISTS idx_matchups_week ON matchups(week, season);
CREATE INDEX IF NOT EXISTS idx_matchup_analysis_matchup ON matchup_analysis(matchup_id);
