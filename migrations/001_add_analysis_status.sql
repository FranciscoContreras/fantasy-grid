-- Migration: Add analysis_status column to matchup_analysis table
-- Date: 2025-10-01
-- Issue: P0-1 - Code references column that doesn't exist

-- Add analysis_status column
ALTER TABLE matchup_analysis
ADD COLUMN analysis_status VARCHAR(20) DEFAULT 'completed';

-- Add index for filtering by status
CREATE INDEX idx_matchup_analysis_status ON matchup_analysis(analysis_status);

-- Add user_roster_name column to matchups for better UX
ALTER TABLE matchups
ADD COLUMN user_roster_name VARCHAR(100);

-- Add opponent_roster_name column to matchups
ALTER TABLE matchups
ADD COLUMN opponent_roster_name VARCHAR(100);

-- Add unique constraint to prevent duplicate matchups
CREATE UNIQUE INDEX idx_matchups_unique ON matchups(user_roster_id, week, season);

-- Add composite index for better query performance
CREATE INDEX idx_roster_players_roster_position ON roster_players(roster_id, position);

-- Add unique constraint to prevent duplicate players in roster
CREATE UNIQUE INDEX idx_roster_players_unique ON roster_players(roster_id, player_id)
WHERE player_id IS NOT NULL;

-- Update existing matchups to have status
UPDATE matchup_analysis SET analysis_status = 'completed' WHERE analysis_status IS NULL;
