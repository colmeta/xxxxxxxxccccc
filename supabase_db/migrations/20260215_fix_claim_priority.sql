
-- Migration: 20260215_fix_claim_priority.sql
-- Description: Ensures high priority jobs are claimed first.

CREATE OR REPLACE FUNCTION public.fn_claim_job(p_worker_id text DEFAULT NULL)
RETURNS TABLE (
  id UUID,
  target_query TEXT,
  target_platform TEXT,
  compliance_mode compliance_level
) AS $$
DECLARE
  claimed_job_id UUID;
BEGIN
  WITH subsequent_job AS (
    SELECT jobs.id
    FROM public.jobs
    WHERE status = 'queued'
    ORDER BY priority DESC, created_at ASC
    LIMIT 1
    FOR UPDATE SKIP LOCKED
  )
  UPDATE public.jobs
  SET 
    status = 'running',
    started_at = NOW(),
    worker_id = p_worker_id
  FROM subsequent_job
  WHERE jobs.id = subsequent_job.id
  RETURNING jobs.id INTO claimed_job_id;

  RETURN QUERY
  SELECT j.id, j.target_query, j.target_platform, j.compliance_mode
  FROM public.jobs j
  WHERE j.id = claimed_job_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
