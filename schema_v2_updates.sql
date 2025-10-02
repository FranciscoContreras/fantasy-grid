-- ========================================
-- API V2 SCHEMA UPDATES
-- Advanced Stats, Next Gen Stats, Play-by-Play
-- ========================================

-- Player Advanced Stats (Next Gen Stats, EPA, CPOE)
CREATE TABLE IF NOT EXISTS player_advanced_stats (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(50) NOT NULL,
    player_name VARCHAR(100),
    position VARCHAR(10),
    season INT NOT NULL,
    week INT,

    -- Next Gen Stats (QB)
    time_to_throw DECIMAL(4,2),  -- Average time to throw (seconds)
    avg_air_yards DECIMAL(5,2),  -- Average air yards per attempt
    completion_above_expectation DECIMAL(5,2),  -- Completion % above expected
    avg_intended_air_yards DECIMAL(5,2),
    max_air_distance DECIMAL(5,2),

    -- Next Gen Stats (RB/WR/TE)
    avg_separation DECIMAL(4,2),  -- Yards of separation from defender
    avg_cushion DECIMAL(4,2),  -- Pre-snap cushion
    avg_yac DECIMAL(5,2),  -- Yards after catch
    avg_target_separation DECIMAL(4,2),
    percent_share_of_routes DECIMAL(5,2),

    -- Next Gen Stats (Rushing)
    rush_yards_over_expected DECIMAL(6,2),
    rush_yards_over_expected_per_att DECIMAL(5,2),
    avg_time_to_los DECIMAL(4,2),  -- Time to line of scrimmage
    efficiency_rating DECIMAL(5,2),
    percent_attempts_gte_eight_defenders DECIMAL(5,2),

    -- EPA (Expected Points Added)
    epa_per_play DECIMAL(5,3),
    epa_total DECIMAL(6,2),
    epa_pass DECIMAL(5,3),
    epa_rush DECIMAL(5,3),
    success_rate DECIMAL(5,2),  -- % of plays with positive EPA

    -- CPOE (Completion Percentage Over Expected) - QB only
    cpoe DECIMAL(5,2),
    expected_completion_pct DECIMAL(5,2),
    actual_completion_pct DECIMAL(5,2),

    -- General Advanced Metrics
    snap_count INT,
    snap_share DECIMAL(5,2),
    targets INT,
    target_share DECIMAL(5,2),
    air_yards_share DECIMAL(5,2),
    wopr DECIMAL(5,3),  -- Weighted Opportunity Rating
    racr DECIMAL(5,3),  -- Receiver Air Conversion Ratio

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(player_id, season, week)
);

-- Play-by-Play Data
CREATE TABLE IF NOT EXISTS play_by_play (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) NOT NULL,
    play_id VARCHAR(100) UNIQUE NOT NULL,
    season INT NOT NULL,
    week INT NOT NULL,

    -- Game State
    quarter INT,
    time_remaining VARCHAR(10),
    down INT,
    yards_to_go INT,
    yard_line INT,
    possession_team VARCHAR(10),

    -- Play Details
    play_type VARCHAR(50),  -- PASS, RUSH, PUNT, FIELD_GOAL, etc.
    play_description TEXT,
    yards_gained INT,
    is_touchdown BOOLEAN DEFAULT false,
    is_turnover BOOLEAN DEFAULT false,
    is_penalty BOOLEAN DEFAULT false,
    is_scoring_play BOOLEAN DEFAULT false,

    -- Players Involved
    passer_id VARCHAR(50),
    passer_name VARCHAR(100),
    rusher_id VARCHAR(50),
    rusher_name VARCHAR(100),
    receiver_id VARCHAR(50),
    receiver_name VARCHAR(100),

    -- Advanced Metrics
    epa DECIMAL(5,3),  -- Expected Points Added
    wpa DECIMAL(5,3),  -- Win Probability Added
    air_yards INT,
    yards_after_catch INT,

    -- Score
    home_score INT,
    away_score INT,
    score_differential INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scoring Plays (subset of play_by_play for quick access)
CREATE TABLE IF NOT EXISTS scoring_plays (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) NOT NULL,
    play_id VARCHAR(100) NOT NULL,
    season INT NOT NULL,
    week INT NOT NULL,

    quarter INT,
    time_remaining VARCHAR(10),
    scoring_team VARCHAR(10),
    scoring_type VARCHAR(20),  -- TD, FG, SAFETY, 2PT
    points INT,

    player_id VARCHAR(50),
    player_name VARCHAR(100),
    play_description TEXT,

    home_score INT,
    away_score INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (play_id) REFERENCES play_by_play(play_id) ON DELETE CASCADE
);

-- Enhanced Injury Reports
CREATE TABLE IF NOT EXISTS injury_reports (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(50) NOT NULL,
    player_name VARCHAR(100),
    team VARCHAR(10),
    position VARCHAR(10),

    -- Injury Details
    injury_status VARCHAR(20),  -- OUT, DOUBTFUL, QUESTIONABLE, PROBABLE, IR
    injury_type VARCHAR(50),  -- Ankle, Knee, Hamstring, etc.
    body_part VARCHAR(50),
    description TEXT,

    -- Timeline
    injury_date DATE,
    report_date DATE NOT NULL,
    expected_return_date DATE,
    weeks_out INT,

    -- Practice Participation
    wednesday_practice VARCHAR(20),  -- FULL, LIMITED, DNP
    thursday_practice VARCHAR(20),
    friday_practice VARCHAR(20),
    game_status VARCHAR(20),  -- OUT, DOUBTFUL, QUESTIONABLE, ACTIVE

    -- Metadata
    season INT NOT NULL,
    week INT NOT NULL,
    is_current BOOLEAN DEFAULT true,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Defense Advanced Stats
CREATE TABLE IF NOT EXISTS defense_advanced_stats (
    id SERIAL PRIMARY KEY,
    team_id VARCHAR(50) NOT NULL,
    team_abbr VARCHAR(10),
    season INT NOT NULL,
    week INT,

    -- Traditional Stats
    points_allowed INT,
    yards_allowed INT,
    pass_yards_allowed INT,
    rush_yards_allowed INT,
    sacks INT,
    interceptions INT,
    fumbles_recovered INT,
    forced_fumbles INT,

    -- Advanced Metrics
    epa_per_play_allowed DECIMAL(5,3),
    success_rate_allowed DECIMAL(5,2),
    explosive_play_rate_allowed DECIMAL(5,2),
    stuff_rate DECIMAL(5,2),  -- % of rushes stopped at or behind LOS

    -- Coverage Stats
    completion_pct_allowed DECIMAL(5,2),
    yards_per_attempt_allowed DECIMAL(4,2),
    passer_rating_allowed DECIMAL(5,2),
    pressure_rate DECIMAL(5,2),
    blitz_rate DECIMAL(5,2),

    -- Situational Stats
    third_down_conversion_pct_allowed DECIMAL(5,2),
    red_zone_td_pct_allowed DECIMAL(5,2),
    goal_to_go_stop_rate DECIMAL(5,2),

    -- Rankings
    overall_rank INT,
    pass_defense_rank INT,
    rush_defense_rank INT,
    scoring_defense_rank INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(team_id, season, week)
);

-- Game Weather (Enhanced from v2 stadium weather)
CREATE TABLE IF NOT EXISTS game_weather (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) UNIQUE NOT NULL,

    -- Location
    stadium_name VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    is_dome BOOLEAN DEFAULT false,
    surface_type VARCHAR(50),  -- Grass, Turf, etc.

    -- Weather Conditions
    temperature INT,  -- Fahrenheit
    feels_like INT,
    humidity INT,  -- Percentage
    wind_speed INT,  -- MPH
    wind_direction VARCHAR(10),
    precipitation_chance INT,  -- Percentage
    precipitation_amount DECIMAL(4,2),  -- Inches
    weather_condition VARCHAR(50),  -- Clear, Cloudy, Rain, Snow, etc.

    -- Game Impact
    weather_severity VARCHAR(20),  -- NONE, LOW, MODERATE, HIGH, EXTREME
    impact_on_passing DECIMAL(3,2),  -- 0.0 to 1.0 multiplier
    impact_on_kicking DECIMAL(3,2),

    forecast_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_advanced_stats_player ON player_advanced_stats(player_id, season, week);
CREATE INDEX IF NOT EXISTS idx_advanced_stats_season_week ON player_advanced_stats(season, week);
CREATE INDEX IF NOT EXISTS idx_play_by_play_game ON play_by_play(game_id);
CREATE INDEX IF NOT EXISTS idx_play_by_play_player_passer ON play_by_play(passer_id);
CREATE INDEX IF NOT EXISTS idx_play_by_play_player_rusher ON play_by_play(rusher_id);
CREATE INDEX IF NOT EXISTS idx_play_by_play_player_receiver ON play_by_play(receiver_id);
CREATE INDEX IF NOT EXISTS idx_scoring_plays_game ON scoring_plays(game_id);
CREATE INDEX IF NOT EXISTS idx_scoring_plays_player ON scoring_plays(player_id);
CREATE INDEX IF NOT EXISTS idx_injury_reports_player ON injury_reports(player_id);
CREATE INDEX IF NOT EXISTS idx_injury_reports_current ON injury_reports(is_current, season, week);
CREATE INDEX IF NOT EXISTS idx_injury_reports_team ON injury_reports(team, season, week);
CREATE INDEX IF NOT EXISTS idx_defense_advanced_team ON defense_advanced_stats(team_id, season, week);
CREATE INDEX IF NOT EXISTS idx_game_weather_game ON game_weather(game_id);
