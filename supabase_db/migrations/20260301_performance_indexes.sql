-- PERFORMANCE INDEXES FOR PRODUCTION READINESS
-- Created: 2026-01-09
-- Purpose: Optimize high-frequency queries identified in audit

-- Results table indexes (most queried)
CREATE INDEX IF NOT EXISTS idx_results_intent_score ON results(intent_score DESC) WHERE intent_score > 0;
CREATE INDEX IF NOT EXISTS idx_results_verified_intent ON results(verified, intent_score DESC) WHERE verified = true;
CREATE INDEX IF NOT EXISTS idx_results_job_verified ON results(job_id, verified);

-- Data Vault indexes (Phase 10 Sovereign queries) - Only if table exists
DO $$
BEGIN
  IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'data_vault') THEN
    CREATE INDEX IF NOT EXISTS idx_data_vault_email ON data_vault(email) WHERE email IS NOT NULL;
    CREATE INDEX IF NOT EXISTS idx_data_vault_linkedin_url ON data_vault(linkedin_url) WHERE linkedin_url IS NOT NULL;
    CREATE INDEX IF NOT EXISTS idx_data_vault_last_verified ON data_vault(last_verified_at DESC);
  END IF;
END $$;

-- Worker status indexes (Phase 11 Swarm monitoring) - Only if columns exist
DO $$
BEGIN
  IF EXISTS (SELECT FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'worker_status' AND column_name = 'stealth_health') THEN
    CREATE INDEX IF NOT EXISTS idx_worker_status_health ON worker_status(stealth_health DESC);
    CREATE INDEX IF NOT EXISTS idx_worker_status_pulse ON worker_status(last_pulse DESC);
  END IF;
 
  IF EXISTS (SELECT FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'worker_status' AND column_name = 'geo_country') THEN
    CREATE INDEX IF NOT EXISTS idx_worker_status_geo ON worker_status(geo_country, geo_city);
  END IF;
END $$;

-- CRM injection logs - Only if table exists
DO $$
BEGIN
  IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'crm_injection_logs') THEN
    CREATE INDEX IF NOT EXISTS idx_crm_injection_status ON crm_injection_logs(status, created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_crm_injection_org ON crm_injection_logs(org_id, created_at DESC);
  END IF;
END $$;

-- Jobs composite indexes
CREATE INDEX IF NOT EXISTS idx_jobs_org_status ON jobs(org_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_priority ON jobs(priority DESC, created_at ASC) WHERE status = 'queued';

-- Provenance logs performance
CREATE INDEX IF NOT EXISTS idx_provenance_result ON provenance_logs(result_id, created_at DESC);

-- Results priority score - Only if column exists
DO $$
BEGIN
  IF EXISTS (SELECT FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'results' AND column_name = 'priority_score') THEN
    CREATE INDEX IF NOT EXISTS idx_results_priority_score ON results(priority_score DESC) WHERE priority_score > 0;
  END IF;
END $$;
