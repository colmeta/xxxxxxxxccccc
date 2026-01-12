-- MIGRATION: Innovation Features (Pain Points #6 and #7)
-- DATE: 2026-02-12
-- PURPOSE: Outreach Burn Prevention + Auto-Prioritization

-- 1. Outreach Burn Prevention Table
-- Tracks which leads have been contacted and by whom (cross-vendor visibility)
create table if not exists public.outreach_history (
    id uuid primary key default gen_random_uuid(),
    lead_identifier text not null, -- email or LinkedIn URL
    contacted_by_org uuid references public.organizations(id),
    contacted_at timestamptz default now(),
    channel text, -- 'email', 'linkedin', 'phone'
    campaign_name text,
    response_status text -- 'no_response', 'replied', 'bounced', 'opted_out'
);

create unique index idx_outreach_history_unique on public.outreach_history(lead_identifier, contacted_by_org, channel);

-- 2. Lead Prioritization Scores
-- AI-generated scores for autonomous routing
alter table public.results 
add column if not exists priority_score int default 50, -- 0-100, higher = better
add column if not exists auto_routed_to uuid, -- user_id of assigned sales rep
add column if not exists routing_reason text; -- why this lead was routed here

create index if not exists idx_results_priority on public.results(priority_score desc) where verified = true;

-- 3. Function to check if lead has been burned
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
    
    -- If no results, return not burned
    if not found then
        return query select false, 0, ''::text;
    end if;
end;
$$ language plpgsql;
