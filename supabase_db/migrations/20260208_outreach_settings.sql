-- MIGRATION: Outreach Config & Enhanced Logging
-- DATE: 2026-02-08

-- 1. Add outreach_config to organizations
-- Stores { "provider": "resend|smtp", "api_key": "...", "smtp_host": "...", etc }
alter table public.organizations 
add column if not exists outreach_config jsonb default '{}';

-- 2. Enhance outreach_logs
alter table public.outreach_logs 
add column if not exists org_id uuid references public.organizations(id) on delete cascade,
add column if not exists result_id uuid references public.results(id) on delete cascade,
add column if not exists error_message text;

-- 3. RLS for outreach_logs
create policy "Users can view their org outreach logs" on public.outreach_logs
  for select using (
    exists (
      select 1 from public.memberships 
      where memberships.org_id = outreach_logs.org_id 
      and memberships.user_id = auth.uid()
    )
  );
