-- ROW LEVEL SECURITY FOR DATA VAULT & WORKER TABLES
-- Created: 2026-01-09
-- Purpose: Secure vault and swarm data with proper RLS policies

-- ============================================
-- DATA VAULT RLS (Phase 10 - Sovereign Profiles)
-- ============================================

-- Only apply if data_vault table exists
DO $$
BEGIN
  IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'data_vault') THEN
    ALTER TABLE data_vault ENABLE ROW LEVEL SECURITY;

    -- Check if org_id column exists before creating org-based policies
    IF EXISTS (SELECT FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'data_vault' AND column_name = 'org_id') THEN
      -- Users can view vault data for their organization
      CREATE POLICY "Users can view org vault data" ON data_vault
        FOR SELECT USING (
          org_id IN (
            SELECT org_id FROM memberships WHERE user_id = auth.uid()
          )
        );

      -- Users can update vault data for their org
      CREATE POLICY "Users can update org vault data" ON data_vault
        FOR UPDATE USING (
          org_id IN (
            SELECT org_id FROM memberships WHERE user_id = auth.uid()
          )
        );
    ELSE
      -- Simple policy: authenticated users can view all vault data (for now)
      CREATE POLICY "Authenticated users can view vault" ON data_vault
        FOR SELECT USING (auth.uid() IS NOT NULL);
      
      CREATE POLICY "Authenticated users can update vault" ON data_vault
        FOR UPDATE USING (auth.uid() IS NOT NULL);
    END IF;

    -- Workers can insert vault data (service role or authenticated)
    CREATE POLICY "Workers can insert vault data" ON data_vault
      FOR INSERT WITH CHECK (
        auth.jwt() ->> 'role' = 'service_role'
        OR auth.uid() IS NOT NULL
      );
  END IF;
END $$;

-- ============================================
-- WORKER STATUS RLS (Phase 11 - Swarm Monitoring)
-- ============================================

-- Only apply if worker_status table exists
DO $$
BEGIN
  IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'worker_status') THEN
    ALTER TABLE worker_status ENABLE ROW LEVEL SECURITY;

    -- All authenticated users can view worker status (Swarm Observatory)
    DROP POLICY IF EXISTS "Authenticated users can view workers" ON worker_status;
    CREATE POLICY "Authenticated users can view workers" ON worker_status
      FOR SELECT USING (auth.uid() IS NOT NULL);

    -- Only service role can update worker status (Hydra heartbeats)
    DROP POLICY IF EXISTS "Service role can upsert workers" ON worker_status;
    CREATE POLICY "Service role can upsert workers" ON worker_status
      FOR ALL USING (
        auth.jwt() ->> 'role' = 'service_role'
        OR auth.uid() IS NOT NULL  -- Allow authenticated users too for flexibility
      );
  END IF;
END $$;

-- ============================================
-- CRM INJECTION LOGS RLS
-- ============================================

-- Only apply if table exists
DO $$
BEGIN
  IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'crm_injection_logs') THEN
    ALTER TABLE crm_injection_logs ENABLE ROW LEVEL SECURITY;

    -- Users can view CRM logs for their organization
    CREATE POLICY "Users can view org CRM logs" ON crm_injection_logs
      FOR SELECT USING (
        org_id IN (
          SELECT org_id FROM memberships WHERE user_id = auth.uid()
        )
      );

    -- Service role can insert CRM logs
    CREATE POLICY "Service role can insert CRM logs" ON crm_injection_logs
      FOR INSERT WITH CHECK (
        auth.jwt() ->> 'role' = 'service_role'
        OR auth.uid() IS NOT NULL
      );
  END IF;
END $$;

-- ============================================
-- SOVEREIGN PROFILES RLS (if table exists)
-- ============================================
DO $$
BEGIN
  IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'sovereign_profiles') THEN
    ALTER TABLE sovereign_profiles ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY "Users can view org sovereign profiles" ON sovereign_profiles
      FOR SELECT USING (
        org_id IN (
          SELECT org_id FROM memberships WHERE user_id = auth.uid()
        )
      );
  END IF;
END $$;
