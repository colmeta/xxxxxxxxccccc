-- CLARITY PEARL: DIVINE EYE - OMNI-PLATFORM VAULT EXPANSION
-- This migration enhances the data_vault to handle SaaS, Social, and E-commerce data.

-- 1. Create enum for Omni-Platforms if not exists (extending beyond social)
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

-- 2. Modify data_vault table to support complex metadata
ALTER TABLE public.data_vault 
ADD COLUMN IF NOT EXISTS platform_id TEXT, -- ID from PH, Chrome Store, etc.
ADD COLUMN IF NOT EXISTS category platform_category DEFAULT 'social',
ADD COLUMN IF NOT EXISTS product_name TEXT, -- For SaaS/Chrome/PH
ADD COLUMN IF NOT EXISTS store_url TEXT, -- Shopify/Amazon/AppStore
ADD COLUMN IF NOT EXISTS rating NUMERIC(3,2),
ADD COLUMN IF NOT EXISTS reviews_count INTEGER,
ADD COLUMN IF NOT EXISTS developer_support_email TEXT;

-- 3. Create indices for faster unified search
CREATE INDEX IF NOT EXISTS idx_vault_platform_id ON public.data_vault(platform_id);
CREATE INDEX IF NOT EXISTS idx_vault_category ON public.data_vault(category);
CREATE INDEX IF NOT EXISTS idx_vault_product_name ON public.data_vault(product_name);

-- 4. Update the trigger function (tr_vault_contribution) to handle these fields
-- Assuming the 'results' table will now surface these fields for the trigger to pick up.
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
        twitter_url, 
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
        COALESCE(NEW.data->>'name', NEW.data->>'full_name'),
        NEW.data->>'title',
        NEW.data->>'company',
        NEW.data->>'email',
        NEW.data->>'phone',
        NEW.data->>'linkedin_url',
        NEW.data->>'twitter_url',
        NEW.data->>'source_platform',
        NEW.data->>'platform_id',
        COALESCE((NEW.data->>'category')::platform_category, 'social'),
        NEW.data->>'product_name',
        NEW.data->>'store_url',
        (NEW.data->>'rating')::NUMERIC,
        (NEW.data->>'reviews_count')::INTEGER,
        NEW.data->>'developer_support_email',
        NEW.data,
        NOW()
    )
    ON CONFLICT (email) DO UPDATE SET
        last_verified_at = NOW(),
        metadata = public.data_vault.metadata || EXCLUDED.metadata;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE public.data_vault IS 'Clarity Pearl: Global Intelligence Archive for SaaS, Social, E-comm, and Local Business.';
