-- CLARITY PEARL: PHASE 10 - SOVEREIGN IDENTITY (MEGA-PROFILES)
-- Unifying fragmented digital footprints into single "Sovereign" profiles.

-- 1. Add Sovereign ID and Platform Linkage
ALTER TABLE public.data_vault 
ADD COLUMN IF NOT EXISTS sovereign_id UUID DEFAULT uuid_generate_v4(),
ADD COLUMN IF NOT EXISTS twitter_handle TEXT,
ADD COLUMN IF NOT EXISTS tiktok_url TEXT,
ADD COLUMN IF NOT EXISTS ph_username TEXT;

-- 2. Create indices for cross-pollination
CREATE INDEX IF NOT EXISTS idx_vault_sovereign ON public.data_vault(sovereign_id);
CREATE INDEX IF NOT EXISTS idx_vault_twitter ON public.data_vault(twitter_handle);
CREATE INDEX IF NOT EXISTS idx_vault_ph ON public.data_vault(ph_username);

-- 3. The "Soft-Link" Merge Logic
-- This function looks for overlapping identifiers (email, linkedin, twitter)
-- and merges them under the same sovereign_id.
CREATE OR REPLACE FUNCTION public.fn_sovereign_merge()
RETURNS TRIGGER AS $$
DECLARE
    v_existing_sovereign UUID;
BEGIN
    -- Check for identity overlaps in order of priority
    SELECT sovereign_id INTO v_existing_sovereign
    FROM public.data_vault
    WHERE (email = NEW.email AND NEW.email IS NOT NULL AND email <> '')
       OR (linkedin_url = NEW.linkedin_url AND NEW.linkedin_url IS NOT NULL AND linkedin_url <> '')
       OR (twitter_handle = NEW.twitter_handle AND NEW.twitter_handle IS NOT NULL AND twitter_handle <> '')
    LIMIT 1;

    -- If we found an existing identity, adopt their sovereign_id
    IF v_existing_sovereign IS NOT NULL THEN
        NEW.sovereign_id := v_existing_sovereign;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. Apply Merge Logic Before Contribution
CREATE TRIGGER tr_sovereign_soft_link
BEFORE INSERT ON public.data_vault
FOR EACH ROW
EXECUTE FUNCTION public.fn_sovereign_merge();

COMMENT ON COLUMN public.data_vault.sovereign_id IS 'The Universal Identity for Clarity Pearl. Links all platform personas to one human.';
