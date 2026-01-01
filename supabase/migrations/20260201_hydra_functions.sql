-- MIGRATION: Hydra Worker Functions (Missing from Production)
-- DATE: 2026-02-01
-- REASON: Fixes "Could not find function public.fn_claim_job" error in Hydra Worker

-- 1. Job Claiming (Atomic Locking)
-- DROP first to remove the incorrect UUID version if it exists
drop function if exists public.fn_claim_job(uuid);

create or replace function public.fn_claim_job(worker_id text default null)
returns table (
  id uuid,
  target_query text,
  target_platform text,
  compliance_mode compliance_level
) as $$
declare
  claimed_job_id uuid;
begin
  -- Find a queued job, lock it, and update it to running
  -- recursive queries or external calls are not allowed inside the locking clause, so we keep it simple
  
  with subsequent_job as (
    select jobs.id
    from public.jobs
    where status = 'queued'
    order by created_at asc
    limit 1
    for update skip locked
  )
  update public.jobs
  set 
    status = 'running',
    started_at = now()
  from subsequent_job
  where jobs.id = subsequent_job.id
  returning jobs.id into claimed_job_id;

  -- Return the job details if one was claimed
  return query
  select j.id, j.target_query, j.target_platform, j.compliance_mode
  from public.jobs j
  where j.id = claimed_job_id;
end;
$$ language plpgsql security definer;

-- 2. Provenance Logging (Safe Encapsulation)
create or replace function public.fn_log_provenance(
  p_result_id uuid,
  p_source_url text,
  p_legal_basis text,
  p_arbiter_verdict text
)
returns void as $$
begin
  insert into public.provenance_logs (result_id, source_url, legal_basis, arbiter_verdict)
  values (p_result_id, p_source_url, p_legal_basis, p_arbiter_verdict);
end;
$$ language plpgsql security definer;
