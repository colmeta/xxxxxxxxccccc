-- CLARITY PEARL: CONSOLIDATED SOVEREIGN VAULT MIGRATION
-- This script is idempotent: it can be run multiple times safely.
-- It fixes "relation does not exist" errors by ensuring base tables exist first.

-- 0. Ensure Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Ensure Platform Category Enum
DO $$ BEGIN
    CREATE TYPE platform_category AS ENUM (
        'social', 
        'marketplace', 
        'ecommerce', 
        'directory', 
        'community'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. Create Base Data Vault Table if missing
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

-- 3. Add Advanced Omni-Platform Columns (Adding one by one for robustness)
ALTER TABLE public.data_vault ADD COLUMN IF NOT EXISTS platform_id TEXT;
ALTER TABLE public.data_vault ADD COLUMN IF NOT EXISTS category platform_category DEFAULT 'social';
ALTER TABLE public.data_vault ADD COLUMN IF NOT EXISTS product_name TEXT;
ALTER TABLE public.data_vault ADD COLUMN IF NOT EXISTS store_url TEXT;
ALTER TABLE public.data_vault ADD COLUMN IF NOT EXISTS rating NUMERIC(3,2);
ALTER TABLE public.data_vault ADD COLUMN IF NOT EXISTS reviews_count INTEGER;
ALTER TABLE public.data_vault ADD COLUMN IF NOT EXISTS developer_support_email TEXT;

-- 4. Add Sovereign Identity Columns
ALTER TABLE public.data_vault ADD COLUMN IF NOT EXISTS sovereign_id UUID DEFAULT uuid_generate_v4();
ALTER TABLE public.data_vault ADD COLUMN IF NOT EXISTS twitter_handle TEXT;
ALTER TABLE public.data_vault ADD COLUMN IF NOT EXISTS tiktok_url TEXT;
ALTER TABLE public.data_vault ADD COLUMN IF NOT EXISTS ph_username TEXT;

-- 5. Establish Unified Indices
CREATE INDEX IF NOT EXISTS idx_vault_company ON public.data_vault(company);
CREATE INDEX IF NOT EXISTS idx_vault_email ON public.data_vault(email);
CREATE INDEX IF NOT EXISTS idx_vault_sovereign ON public.data_vault(sovereign_id);
CREATE INDEX IF NOT EXISTS idx_vault_platform_id ON public.data_vault(platform_id);
CREATE INDEX IF NOT EXISTS idx_vault_category ON public.data_vault(category);

-- 6. The Sovereign Merge Logic (Soft-Link)
CREATE OR REPLACE FUNCTION public.fn_sovereign_merge()
RETURNS TRIGGER AS $$
DECLARE
    v_existing_sovereign UUID;
BEGIN
    SELECT sovereign_id INTO v_existing_sovereign
    FROM public.data_vault
    WHERE (email = NEW.email AND NEW.email IS NOT NULL AND email <> '')
       OR (linkedin_url = NEW.linkedin_url AND NEW.linkedin_url IS NOT NULL AND linkedin_url <> '')
    LIMIT 1;

    IF v_existing_sovereign IS NOT NULL THEN
        NEW.sovereign_id := v_existing_sovereign;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 7. The Global Contribution Logic
CREATE OR REPLACE FUNCTION public.fn_vault_contribution()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.data_vault (
        full_name, 
        title, 
        company, 
        email, 
        phone, 
        linkedin_url, 
        source_platform,
        platform_id,
        category,
        product_name,
        store_url,
        rating,
        reviews_count,
        developer_support_email,
        metadata,
        last_verified_at
    ) 
    VALUES (
        COALESCE(NEW.data_payload->>'name', NEW.data_payload->>'full_name'),
        NEW.data_payload->>'title',
        NEW.data_payload->>'company',
        NEW.data_payload->>'email',
        NEW.data_payload->>'phone',
        NEW.data_payload->>'source_url',
        NEW.target_platform,
        NEW.data_payload->>'platform_id',
        COALESCE((NEW.data_payload->>'category')::platform_category, 'social'),
        NEW.data_payload->>'product_name',
        NEW.data_payload->>'store_url',
        (NEW.data_payload->>'rating')::NUMERIC,
        (NEW.data_payload->>'reviews_count')::INTEGER,
        NEW.data_payload->>'developer_support_email',
        NEW.data_payload,
        NOW()
    )
    ON CONFLICT (email) DO UPDATE SET
        last_verified_at = NOW(),
        metadata = public.data_vault.metadata || EXCLUDED.metadata;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 8. Finalize Triggers
DROP TRIGGER IF EXISTS tr_sovereign_soft_link ON public.data_vault;
CREATE TRIGGER tr_sovereign_soft_link
BEFORE INSERT ON public.data_vault
FOR EACH ROW
EXECUTE FUNCTION public.fn_sovereign_merge();

DROP TRIGGER IF EXISTS tr_vault_contribution ON public.results;
CREATE TRIGGER tr_vault_contribution
AFTER INSERT ON public.results
FOR EACH ROW
WHEN (NEW.verified = true AND NEW.data_payload->>'email' IS NOT NULL)
EXECUTE FUNCTION public.fn_vault_contribution();

COMMENT ON TABLE public.data_vault IS 'Clarity Pearl: Unified Sovereign Intelligence Archive.';
