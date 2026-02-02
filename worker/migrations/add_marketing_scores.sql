-- Migration: Add Missing Oracle/Marketing Scores to 'results' table
-- Fixes PGRST204 error: Could not find the 'marketing_need_score' column

ALTER TABLE results 
ADD COLUMN IF NOT EXISTS marketing_need_score INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS intent_score INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS predictive_growth_score INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS oracle_signal TEXT DEFAULT 'Baseline',
ADD COLUMN IF NOT EXISTS reasoning TEXT,
ADD COLUMN IF NOT EXISTS velocity_data JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTSdisplacement_data JSONB DEFAULT '{}'::jsonb;

-- Ensure indexes for performance
CREATE INDEX IF NOT EXISTS idx_results_intent_score ON results(intent_score);
CREATE INDEX IF NOT EXISTS idx_results_marketing_need_score ON results(marketing_need_score);
