-- MIGRATION: The Divine Mesh (Worker Coordination)
-- DATE: 2026-02-10

-- 1. Worker Status & Stealth Coordination
create table if not exists public.worker_status (
    worker_id text primary key,
    last_pulse timestamptz default now(),
    stealth_health float default 100.0,
    current_ip text,
    burned_proxies text[], -- List of proxies this worker has marked as dead
    best_user_agent text,  -- The UA currently getting the best results
    active_missions int default 0
);

-- 2. RLS: Workers can update their own status, everyone can read
alter table public.worker_status enable row level security;

create policy "Workers can update own status"
    on public.worker_status for all
    using (true) -- For now, trust the worker ID (in prod we'd verify signatures)
    with check (true);
