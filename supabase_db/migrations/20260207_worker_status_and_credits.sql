-- MIGRATION: Worker Status & Credit Management
-- DATE: 2026-02-07
-- REASON: Adds health monitoring for Hydra workers and automated credit resets.

-- 1. Create Worker Status Table
CREATE TABLE IF NOT EXISTS public.worker_status (
    worker_id TEXT PRIMARY KEY,
    status TEXT DEFAULT 'active',
    last_pulse TIMESTAMPTZ DEFAULT now(),
    stealth_health FLOAT DEFAULT 100.0,
    best_user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.worker_status ENABLE ROW LEVEL SECURITY;

-- Policy: Allow read access to authenticated users (admin dashboard)
CREATE POLICY "Allow read access for authenticated users" 
ON public.worker_status FOR SELECT 
TO authenticated 
USING (true);

-- Policy: Allow upsert for service role (Workers)
-- Note: In Supabase, service_role usually bypasses RLS, 
-- but we define this for clarity if workers use authenticated keys.
CREATE POLICY "Allow upsert for workers" 
ON public.worker_status FOR ALL 
TO service_role 
USING (true) 
WITH CHECK (true);

-- 2. Monthly Credit Reset Function
-- This function resets 'credits_used' to 0 for all organizations.
CREATE OR REPLACE FUNCTION public.fn_reset_monthly_credits()
RETURNS void AS $$
BEGIN
    UPDATE public.organizations
    SET credits_used = 0;
    
    -- Optional: Log the reset
    RAISE NOTICE 'Monthly credits have been reset for all organizations.';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Admin Command: Add Credits to Org
-- Usage: select public.fn_add_credits('ORG_UUID', 500);
CREATE OR REPLACE FUNCTION public.fn_add_credits(p_org_id UUID, p_amount INT)
RETURNS void AS $$
BEGIN
    UPDATE public.organizations
    SET credits_monthly = credits_monthly + p_amount
    WHERE id = p_org_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
