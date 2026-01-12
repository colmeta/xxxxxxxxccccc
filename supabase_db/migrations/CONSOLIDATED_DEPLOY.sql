-- CONSOLIDATED DEPLOYMENT SCRIPT (IDEMPOTENT)
-- Run this in Supabase > SQL Editor
-- It handles all outstanding migrations safely.

-- ==========================================
-- 1. OUTREACH SETTINGS & LOGGING
-- ==========================================

-- Add outreach_config if missing
alter table public.organizations 
add column if not exists outreach_config jsonb default '{}';

-- Enhance outreach_logs columns
alter table public.outreach_logs 
add column if not exists org_id uuid references public.organizations(id) on delete cascade,
add column if not exists result_id uuid references public.results(id) on delete cascade,
add column if not exists error_message text;

-- RLS for outreach_logs (Drop first to allow re-run)
drop policy if exists "Users can view their org outreach logs" on public.outreach_logs;
drop policy if exists "Orgs can view own outreach logs" on public.outreach_logs;
drop policy if exists "System can insert outreach logs" on public.outreach_logs;

alter table public.outreach_logs enable row level security;

create policy "Orgs can view own outreach logs" on public.outreach_logs
  for select using (
    org_id in (select org_id from public.profiles where id = auth.uid())
  );

create policy "System can insert outreach logs" on public.outreach_logs
  for insert with check (true);

-- Indexes
create index if not exists idx_outreach_logs_org on public.outreach_logs(org_id);
create index if not exists idx_outreach_logs_status on public.outreach_logs(status);


-- ==========================================
-- 2. PREDICTIVE SIGNALS (THE ORACLE)
-- ==========================================

alter table public.results 
add column if not exists predictive_growth_score int default 0,
add column if not exists reasoning text,
add column if not exists priority_score int default 50,
add column if not exists intent_score int default 0,
add column if not exists auto_routed_to uuid,
add column if not exists routing_reason text;

alter table public.jobs
add column if not exists priority int default 0;

create index if not exists idx_results_predictive_growth on public.results(predictive_growth_score desc);
create index if not exists idx_results_priority on public.results(priority_score desc) where verified = true;
create index if not exists idx_results_intent_score on public.results(intent_score desc) where verified = true;
create index if not exists idx_jobs_status_priority on public.jobs(status, priority desc);

-- ==========================================
-- 2a. JOBS & WORKER FOUNDATIONS
-- ==========================================

DO $$ begin
    create type public.compliance_level as enum ('strict', 'standard', 'loose');
exception
    when duplicate_object then null;
end $$;

create table if not exists public.jobs (
    id uuid primary key default gen_random_uuid(),
    created_at timestamptz default now(),
    status text default 'queued',
    priority int default 0
);

alter table public.jobs 
add column if not exists target_query text,
add column if not exists target_platform text,
add column if not exists compliance_mode public.compliance_level default 'standard',
add column if not exists search_metadata jsonb default '{}',
add column if not exists worker_id text,
add column if not exists started_at timestamptz;

create index if not exists idx_jobs_worker_id on public.jobs(worker_id);


-- ==========================================
-- 3. DIVINE MESH (WORKER COORDINATION)
-- ==========================================

create table if not exists public.worker_status (
    worker_id text primary key,
    last_pulse timestamptz default now(),
    stealth_health float default 100.0,
    current_ip text,
    burned_proxies text[],
    best_user_agent text,
    active_missions int default 0
);

alter table public.worker_status enable row level security;

-- Drop existng policies to allow updates
drop policy if exists "Workers can update own status" on public.worker_status;
drop policy if exists "Anyone can read worker status for mesh coordination" on public.worker_status;
drop policy if exists "Only system can update worker status" on public.worker_status;
drop policy if exists "Only system can modify worker status" on public.worker_status;

-- Re-create policies
create policy "Anyone can read worker status for mesh coordination"
    on public.worker_status for select using (true);

create policy "Only system can update worker status"
    on public.worker_status for insert with check (true);

create policy "Only system can modify worker status"
    on public.worker_status for update using (true);


-- ==========================================
-- 4. API KEYS (SECURITY HARDENING)
-- ==========================================

create table if not exists public.api_keys (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references public.organizations(id) on delete cascade,
    key_hash text not null unique,
    key_prefix text not null,
    name text,
    created_at timestamptz default now(),
    expires_at timestamptz,
    last_used_at timestamptz,
    is_active boolean default true,
    rate_limit_rpm int default 100,
    usage_count bigint default 0
);

create index if not exists idx_api_keys_org on public.api_keys(org_id);
create index if not exists idx_api_keys_hash on public.api_keys(key_hash) where is_active = true;

alter table public.api_keys enable row level security;

drop policy if exists "Orgs can manage own API keys" on public.api_keys;

create policy "Orgs can manage own API keys"
    on public.api_keys for all
    using (
        org_id in (select org_id from public.profiles where id = auth.uid())
    );

-- Validation Function
create or replace function public.fn_validate_api_key(p_key_hash text)
returns table(org_id uuid, rate_limit int) as $$
declare
    v_key record;
begin
    select k.org_id, k.rate_limit_rpm, k.expires_at, k.is_active
    into v_key
    from public.api_keys k
    where k.key_hash = p_key_hash;

    if not found then raise exception 'Invalid API key'; end if;
    if v_key.is_active = false then raise exception 'API key is disabled'; end if;
    if v_key.expires_at is not null and v_key.expires_at < now() then raise exception 'API key has expired'; end if;

    update public.api_keys set last_used_at = now(), usage_count = usage_count + 1 where key_hash = p_key_hash;
    return query select v_key.org_id, v_key.rate_limit_rpm;
end;
$$ language plpgsql security definer;


-- ==========================================
-- 5. INNOVATION FEATURES (BURN PREVENTION)
-- ==========================================

create table if not exists public.outreach_history (
    id uuid primary key default gen_random_uuid(),
    lead_identifier text not null,
    contacted_by_org uuid references public.organizations(id),
    contacted_at timestamptz default now(),
    channel text,
    campaign_name text,
    response_status text
);

create unique index if not exists idx_outreach_history_unique on public.outreach_history(lead_identifier, contacted_by_org, channel);

create or replace function public.fn_check_outreach_burn(p_identifier text, p_days_threshold int default 90)
returns table(is_burned boolean, last_contact_days_ago int, contacted_by text) as $$
begin
    return query
    select 
        true as is_burned,
        extract(day from now() - max(oh.contacted_at))::int as last_contact_days_ago,
        string_agg(o.name, ', ') as contacted_by
    from public.outreach_history oh
    left join public.organizations o on oh.contacted_by_org = o.id
    where oh.lead_identifier = p_identifier
      and oh.contacted_at > now() - (p_days_threshold || ' days')::interval
    group by oh.lead_identifier
    having count(*) > 0;
    
    if not found then return query select false, 0, ''::text; end if;
end;
$$ language plpgsql;
