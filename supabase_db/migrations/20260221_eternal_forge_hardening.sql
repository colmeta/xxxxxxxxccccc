-- CLARITY PEARL: PHASE 12 - ETERNAL FORGE HARDENING
-- Ensuring intelligence propagation from Results to Data Vault.

-- 1. Extend Results with Autonomous Intelligence Columns
ALTER TABLE public.results 
ADD COLUMN IF NOT EXISTS velocity_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS displacement_data JSONB DEFAULT '{}';

-- 2. Update Vault Contribution Logic to include Autonomous Intelligence
CREATE OR REPLACE FUNCTION public.fn_vault_contribution()
RETURNS TRIGGER AS $$
DECLARE
    v_metadata JSONB;
BEGIN
    -- Merge payload with autonomous intelligence
    v_metadata := NEW.data_payload || jsonb_build_object(
        'velocity_data', NEW.velocity_data,
        'displacement_data', NEW.displacement_data,
        'intent_score', NEW.intent_score,
        'oracle_signal', NEW.oracle_signal
    );

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
        NEW.data_payload->>'source_platform',
        NEW.data_payload->>'platform_id',
        COALESCE((NEW.data_payload->>'category')::platform_category, 'social'),
        NEW.data_payload->>'product_name',
        NEW.data_payload->>'store_url',
        (NEW.data_payload->>'rating')::NUMERIC,
        (NEW.data_payload->>'reviews_count')::INTEGER,
        (NEW.data_payload->>'developer_support_email'),
        v_metadata,
        NOW()
    )
    ON CONFLICT (email) DO UPDATE SET
        last_verified_at = NOW(),
        metadata = public.data_vault.metadata || EXCLUDED.metadata;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON COLUMN public.results.velocity_data IS 'Kinetic Velocity: Temporal growth and scaling signals.';
COMMENT ON COLUMN public.results.displacement_data IS 'Sovereign Intelligence: AI-refined displacement scripts.';
