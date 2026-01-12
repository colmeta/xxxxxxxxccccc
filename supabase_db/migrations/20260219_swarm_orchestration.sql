-- CLARITY PEARL: PHASE 11 - DIVINE SWARM ORCHESTRATION
-- Enhancing worker monitoring for global residential node management.

-- 1. Extend Worker Status with Geo & Node Metadata
ALTER TABLE public.worker_status 
ADD COLUMN IF NOT EXISTS node_type TEXT DEFAULT 'residential', -- residential, mobile, cloud
ADD COLUMN IF NOT EXISTS public_ip TEXT,
ADD COLUMN IF NOT EXISTS geo_city TEXT,
ADD COLUMN IF NOT EXISTS geo_country TEXT,
ADD COLUMN IF NOT EXISTS ip_authority_score NUMERIC(3,2) DEFAULT 9.0; -- 0-10 based on trust

-- 2. Create Index for Swarm Location Searches
CREATE INDEX IF NOT EXISTS idx_worker_geo ON public.worker_status(geo_country, geo_city);

-- 3. Function to update worker pulse with metadata
CREATE OR REPLACE FUNCTION public.fn_pulse_worker_v2(
    p_worker_id TEXT,
    p_stealth_health FLOAT,
    p_node_type TEXT,
    p_public_ip TEXT,
    p_geo_city TEXT,
    p_geo_country TEXT,
    p_ip_authority NUMERIC
)
RETURNS void AS $$
BEGIN
    INSERT INTO public.worker_status (
        worker_id, status, last_pulse, stealth_health, node_type, public_ip, geo_city, geo_country, ip_authority_score
    )
    VALUES (
        p_worker_id, 'active', NOW(), p_stealth_health, p_node_type, p_public_ip, p_geo_city, p_geo_country, p_ip_authority
    )
    ON CONFLICT (worker_id) DO UPDATE SET
        status = 'active',
        last_pulse = NOW(),
        stealth_health = EXCLUDED.stealth_health,
        public_ip = EXCLUDED.public_ip,
        geo_city = EXCLUDED.geo_city,
        geo_country = EXCLUDED.geo_country,
        ip_authority_score = EXCLUDED.ip_authority_score;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON TABLE public.worker_status IS 'Divine Swarm: Global health and location of residential scraping nodes.';
