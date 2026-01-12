-- MIGRATION: Clarity Score & Verification Metadata
-- DATE: 2026-02-02

-- 1. Update results table
ALTER TABLE public.results 
ADD COLUMN IF NOT EXISTS clarity_score INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS verified_at TIMESTAMPTZ DEFAULT now();

-- 2. Add comment for documentation
COMMENT ON COLUMN public.results.clarity_score IS 'Score (0-100) assigned by the Arbiter Agent based on data quality and relevance.';
