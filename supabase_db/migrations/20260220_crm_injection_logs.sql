-- CLARITY PEARL: CRM INJECTION LOGS
-- Tracking the flow of intelligence into the user's stack.

CREATE TABLE IF NOT EXISTS public.crm_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vault_id UUID REFERENCES public.data_vault(id),
    job_id UUID, 
    crm_type TEXT, -- hubspot, salesforce, etc.
    sync_status TEXT DEFAULT 'success',
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.crm_logs ENABLE ROW LEVEL SECURITY;

-- Policy: Allow read for authenticated users
CREATE POLICY "Allow read for authenticated users" ON public.crm_logs FOR SELECT TO authenticated USING (true);

COMMENT ON TABLE public.crm_logs IS 'Clarity Pearl: Audit trail for Mega-Profile injections into external CRMs.';
