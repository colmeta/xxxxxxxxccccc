-- CLARITY PEARL DATABASE SCHEMA
-- AGENT: The Vault Keeper
-- DATE: December 2025

-- 1. ENUMS
create type job_status as enum ('queued', 'running', 'completed', 'failed');
create type compliance_level as enum ('standard', 'strict', 'gdpr');

-- 2. TABLES

-- USERS (Extends Supabase Auth)
create table public.profiles (
  id uuid references auth.users not null primary key,
  email text,
  full_name text,
  company_name text,
  plan_tier text default 'free', -- 'free', 'pro', 'enterprise'
  credits_remaining int default 100,
  created_at timestamptz default now()
);

-- JOBS (The Work Queue)
create table public.jobs (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) not null,
  status job_status default 'queued',
  target_query text not null, -- e.g. "SaaS CEOs in Austin"
  target_platform text not null, -- 'linkedin', 'google_maps'
  compliance_mode compliance_level default 'standard',
  result_count int default 0,
  error_log text,
  started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz default now()
);

-- RESULTS (The Raw Data)
create table public.results (
  id uuid default gen_random_uuid() primary key,
  job_id uuid references public.jobs(id) on delete cascade not null,
  data_payload jsonb not null, -- The scraped data
  verified boolean default false, -- The Arbiter's check
  created_at timestamptz default now()
);

-- PROVENANCE LOGS (The Compliance Receipt)
create table public.provenance_logs (
  id uuid default gen_random_uuid() primary key,
  result_id uuid references public.results(id) on delete cascade not null,
  source_url text,
  scraped_at timestamptz default now(),
  legal_basis text default 'Legitimate Interest (B2B)',
  proxy_ip_hash text, -- Anonymized IP of the scraper
  arbiter_verdict text, -- e.g. "Confirmed via Corp Site"
  created_at timestamptz default now()
);

-- OPT-OUT REGISTRY (The Blacklist)
create table public.opt_out_registry (
  id uuid default gen_random_uuid() primary key,
  identifier_hash text unique not null, -- SHA-256 of email or phone
  request_ip_hash text,
  requested_at timestamptz default now()
);

-- 3. ROW LEVEL SECURITY (RLS)

alter table public.profiles enable row level security;
alter table public.jobs enable row level security;
alter table public.results enable row level security;
alter table public.provenance_logs enable row level security;

-- PROFILES: Users can read/edit their own profile
create policy "Users can view own profile" on public.profiles
  for select using (auth.uid() = id);

create policy "Users can update own profile" on public.profiles
  for update using (auth.uid() = id);

-- JOBS: Users can see only their own jobs
create policy "Users can view own jobs" on public.jobs
  for select using (auth.uid() = user_id);

create policy "Users can insert own jobs" on public.jobs
  for insert with check (auth.uid() = user_id);

-- RESULTS: Users can see results for their own jobs
create policy "Users can view own results" on public.results
  for select using (
    exists ( select 1 from public.jobs where jobs.id = results.job_id and jobs.user_id = auth.uid() )
  );

-- PROVENANCE: Users can see provenance for their results
create policy "Users can view own provenance" on public.provenance_logs
  for select using (
    exists ( 
      select 1 from public.results 
      join public.jobs on jobs.id = results.job_id 
      where results.id = provenance_logs.result_id 
      and jobs.user_id = auth.uid() 
    )
  );

-- 4. FUNCTIONS

-- Auto-create profile on signup
create or replace function public.handle_new_user() 
returns trigger as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email);
  return new;
end;
$$ language plpgsql security definer;


-- 5. INDEXES (Performance Optimization)
create index idx_jobs_status on public.jobs(status);
create index idx_jobs_user_id on public.jobs(user_id);
create index idx_results_job_id on public.results(job_id);

-- 6. WORKER PROCEDURES

-- Function for a worker to atomicallly claim a queued job
create or replace function public.fn_claim_job(worker_id uuid default null)
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
    select id
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
    -- worker_id could be added to jobs table if we want to track which worker took it
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

-- Function to safely log provenance data (optional helper, but good for encapsulation)
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
