
-- Migration: 20260215_data_vault_architecture.sql
-- Description: The "Imperial" Leverage table for B2B intelligence.

CREATE TABLE IF NOT EXISTS public.data_vault (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name TEXT,
    title TEXT,
    company TEXT,
    email TEXT UNIQUE,
    linkedin_url TEXT,
    phone TEXT,
    source_platform TEXT,
    last_verified_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for rapid lookup by company or title
CREATE INDEX IF NOT EXISTS idx_vault_company ON public.data_vault(company);
CREATE INDEX IF NOT EXISTS idx_vault_title ON public.data_vault(title);
CREATE INDEX IF NOT EXISTS idx_vault_email ON public.data_vault(email);

-- Function to contribute to the vault from results
CREATE OR REPLACE FUNCTION public.fn_contribute_to_vault()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.data_vault (full_name, title, company, email, linkedin_url, source_platform, metadata)
    VALUES (
        NEW.data_payload->>'name',
        NEW.data_payload->>'title',
        NEW.data_payload->>'company',
        NEW.data_payload->>'email',
        NEW.data_payload->>'source_url',
        NEW.target_platform,
        NEW.data_payload
    )
    ON CONFLICT (email) DO UPDATE 
    SET last_verified_at = NOW(),
        metadata = NEW.data_payload;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-populate vault from successful results
CREATE TRIGGER tr_vault_contribution
AFTER INSERT ON public.results
FOR EACH ROW
WHEN (NEW.verified = true AND NEW.data_payload->>'email' IS NOT NULL)
EXECUTE FUNCTION public.fn_contribute_to_vault();
