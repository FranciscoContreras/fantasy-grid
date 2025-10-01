-- Migration: Add analysis status tracking
-- Purpose: Track progress of AI analysis generation (pending -> analyzing -> completed)

ALTER TABLE matchup_analysis
ADD COLUMN IF NOT EXISTS analysis_status VARCHAR(20) DEFAULT 'completed';

-- Add index for efficient status queries
CREATE INDEX IF NOT EXISTS idx_matchup_analysis_status
ON matchup_analysis(matchup_id, analysis_status);

COMMENT ON COLUMN matchup_analysis.analysis_status IS 'Status of AI analysis: pending, analyzing, completed, failed';
