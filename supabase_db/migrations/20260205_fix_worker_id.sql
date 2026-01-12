-- Add worker_id column to jobs table to track which worker is processing the job
ALTER TABLE public.jobs ADD COLUMN IF NOT EXISTS worker_id text;

-- Update fn_claim_job to use the new column instead of just logging in error_log
CREATE OR REPLACE FUNCTION public.fn_claim_job(p_worker_id text DEFAULT 'unknown_hydra')
 RETURNS TABLE(id uuid, target_query text, target_platform text, compliance_mode compliance_level, ab_test_group text)
 LANGUAGE plpgsql
 SECURITY DEFINER
AS $function$
declare
  claimed_job_id uuid;
begin
  with subsequent_job as (
    select j.id
    from public.jobs j
    where j.status = 'queued'
    order by j.priority desc, j.created_at asc
    limit 1
    for update skip locked
  )
  update public.jobs
  set 
    status = 'running',
    started_at = now(),
    worker_id = p_worker_id, -- Use the new column
    error_log = 'Claimed by ' || p_worker_id
  from subsequent_job
  where jobs.id = subsequent_job.id
  returning jobs.id into claimed_job_id;

  return query
  select j.id, j.target_query, j.target_platform, j.compliance_mode, j.ab_test_group
  from public.jobs j
  where j.id = claimed_job_id;
end;
$function$;
