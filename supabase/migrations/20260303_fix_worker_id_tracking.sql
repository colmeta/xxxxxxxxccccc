-- FIX WORKER ID TRACKING
-- Created: 2026-01-09
-- Purpose: Move worker ID from error_log to dedicated column for proper tracking

-- Add worker_id column to jobs table (if not exists)
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS worker_id TEXT;

-- Create index for worker performance tracking
CREATE INDEX IF NOT EXISTS idx_jobs_worker_id ON jobs(worker_id, completed_at DESC) WHERE worker_id IS NOT NULL;

-- Drop the old function to allow signature change
DROP FUNCTION IF EXISTS public.fn_claim_job(text);

-- Recreate fn_claim_job with search_metadata in return type
CREATE OR REPLACE FUNCTION public.fn_claim_job(p_worker_id text DEFAULT 'unknown_hydra')
RETURNS TABLE (
  id uuid,
  target_query text,
  target_platform text,
  compliance_mode compliance_level,
  ab_test_group text,
  search_metadata jsonb
) AS $$
DECLARE
  claimed_job_id uuid;
BEGIN
  -- Claim highest priority job atomically
  WITH next_job AS (
    SELECT j.id
    FROM public.jobs j
    WHERE j.status = 'queued'
    ORDER BY j.priority DESC, j.created_at ASC
    LIMIT 1
    FOR UPDATE SKIP LOCKED
  )
  UPDATE public.jobs
  SET 
    status = 'running',
    started_at = now(),
    worker_id = p_worker_id  -- Use dedicated column
  FROM next_job
  WHERE jobs.id = next_job.id
  RETURNING jobs.id INTO claimed_job_id;

  -- Return claimed job details with all needed fields
  RETURN QUERY
  SELECT j.id, j.target_query, j.target_platform, j.compliance_mode, j.ab_test_group, j.search_metadata
  FROM public.jobs j
  WHERE j.id = claimed_job_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Migrate existing error_log worker IDs to worker_id column (only if not already done)
DO $$
BEGIN
  UPDATE jobs 
  SET worker_id = SUBSTRING(error_log FROM 'Claimed by (.+)')
  WHERE error_log LIKE 'Claimed by %' 
    AND worker_id IS NULL;
END $$;

COMMENT ON COLUMN jobs.worker_id IS 'Hydra worker that claimed/executed this job (Phase 11 tracking)';
