-- MIGRATION: CRM and Outreach Tracking
-- DATE: 2026-01-01

-- 1. CRM LOGS
create table public.crm_logs (
  id uuid default gen_random_uuid() primary key,
  job_id uuid references public.jobs(id) on delete cascade,
  crm_type text not null, -- 'hubspot', 'salesforce'
  sync_status text not null, -- 'success', 'failed'
  external_id text, -- ID returned by CRM
  payload jsonb,
  synced_at timestamptz default now()
);

-- 2. OUTREACH LOGS
create table public.outreach_logs (
  id uuid default gen_random_uuid() primary key,
  target_email text not null,
  campaign_id text,
  provider text, -- 'sendgrid', 'mailgun'
  status text, -- 'sent', 'queued', 'failed'
  sent_at timestamptz default now()
);

-- 3. RLS
alter table public.crm_logs enable row level security;
alter table public.outreach_logs enable row level security;

-- (Simple policies for now - assume service role checks or inherit form jobs)
create policy "Users can view own crm logs" on public.crm_logs
  for select using (
    exists ( select 1 from public.jobs where jobs.id = crm_logs.job_id and jobs.user_id = auth.uid() )
  );
