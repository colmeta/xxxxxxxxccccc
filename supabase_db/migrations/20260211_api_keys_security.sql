-- MIGRATION: API Keys Infrastructure (Critical Fix)
-- DATE: 2026-02-11
-- PURPOSE: Enable secure V1 API access with key rotation and expiration

-- 1. API Keys Table
create table if not exists public.api_keys (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references public.organizations(id) on delete cascade,
    key_hash text not null unique, -- SHA-256 hash of the actual key
    key_prefix text not null, -- First 8 chars for identification (e.g., "cp_live_abc12345...")
    name text, -- User-friendly name (e.g., "Production API Key")
    created_at timestamptz default now(),
    expires_at timestamptz, -- NULL = never expires
    last_used_at timestamptz,
    is_active boolean default true,
    rate_limit_rpm int default 100, -- Requests per minute
    usage_count bigint default 0
);

-- 2. Indexes for performance
create index idx_api_keys_org on public.api_keys(org_id);
create index idx_api_keys_hash on public.api_keys(key_hash) where is_active = true;

-- 3. RLS Policies
alter table public.api_keys enable row level security;

create policy "Orgs can manage own API keys"
    on public.api_keys for all
    using (
        org_id in (
            select org_id from public.profiles where id = auth.uid()
        )
    );

-- 4. Function to validate and track API key usage
create or replace function public.fn_validate_api_key(p_key_hash text)
returns table(org_id uuid, rate_limit int) as $$
declare
    v_key record;
begin
    select k.org_id, k.rate_limit_rpm, k.expires_at, k.is_active
    into v_key
    from public.api_keys k
    where k.key_hash = p_key_hash;

    if not found then
        raise exception 'Invalid API key';
    end if;

    if v_key.is_active = false then
        raise exception 'API key is disabled';
    end if;

    if v_key.expires_at is not null and v_key.expires_at < now() then
        raise exception 'API key has expired';
    end if;

    -- Update usage stats
    update public.api_keys
    set last_used_at = now(), usage_count = usage_count + 1
    where key_hash = p_key_hash;

    return query select v_key.org_id, v_key.rate_limit_rpm;
end;
$$ language plpgsql security definer;
