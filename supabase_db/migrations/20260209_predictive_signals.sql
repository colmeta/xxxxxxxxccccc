-- MIGRATION: Predictive Dominance & Intelligence Signals
-- DATE: 2026-02-09

-- 1. Support for Oracle's Future Sight
alter table public.results 
add column if not exists predictive_growth_score int default 0,
add column if not exists reasoning text;

-- 2. Indexing for High-Growth Querying
create index if not exists idx_results_predictive_growth on public.results(predictive_growth_score desc);
