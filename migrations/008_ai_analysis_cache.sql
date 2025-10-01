-- Migration: Add AI analysis caching table
-- Purpose: Store Grok-generated analyses to avoid duplicate API calls
-- Benefit: Save money + improve performance for repeat analyses

CREATE TABLE IF NOT EXISTS ai_analysis_cache (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(50),
    player_name VARCHAR(100) NOT NULL,
    position VARCHAR(10) NOT NULL,
    team VARCHAR(10) NOT NULL,
    opponent_team VARCHAR(10) NOT NULL,
    week INT NOT NULL,
    season INT NOT NULL,

    -- Analysis results
    matchup_score DECIMAL(5,2),
    projected_points DECIMAL(5,2),
    recommendation VARCHAR(20),  -- START, SIT, CONSIDER
    ai_grade VARCHAR(5),
    confidence_score DECIMAL(5,2),

    -- The AI-generated text
    reasoning TEXT NOT NULL,

    -- Context used (for debugging)
    injury_status VARCHAR(50),
    opponent_defense_rank INT,
    historical_performance JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),

    -- Unique constraint: one analysis per player+opponent+week+season
    UNIQUE(player_id, opponent_team, week, season)
);

-- Index for fast lookups
CREATE INDEX idx_ai_cache_lookup ON ai_analysis_cache(player_id, opponent_team, week, season);
CREATE INDEX idx_ai_cache_player_name ON ai_analysis_cache(player_name, week, season);
CREATE INDEX idx_ai_cache_created_at ON ai_analysis_cache(created_at);

-- Comments for documentation
COMMENT ON TABLE ai_analysis_cache IS 'Persistent cache of AI-generated player analyses';
COMMENT ON COLUMN ai_analysis_cache.reasoning IS 'Grok-generated analysis text';
COMMENT ON COLUMN ai_analysis_cache.historical_performance IS 'JSON of player stats vs this opponent';
