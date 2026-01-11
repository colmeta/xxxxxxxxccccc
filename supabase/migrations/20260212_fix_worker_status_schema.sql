-- Migration to add ALL missing columns to worker_status for Phase 11 Swarm Swarm
DO $$
BEGIN
    -- best_user_agent
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'worker_status' AND column_name = 'best_user_agent') THEN
        ALTER TABLE public.worker_status ADD COLUMN best_user_agent TEXT;
    END IF;
    
    -- node_type
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'worker_status' AND column_name = 'node_type') THEN
        ALTER TABLE public.worker_status ADD COLUMN node_type TEXT DEFAULT 'residential';
    END IF;

    -- public_ip
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'worker_status' AND column_name = 'public_ip') THEN
        ALTER TABLE public.worker_status ADD COLUMN public_ip TEXT;
    END IF;

    -- geo_city
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'worker_status' AND column_name = 'geo_city') THEN
        ALTER TABLE public.worker_status ADD COLUMN geo_city TEXT;
    END IF;

    -- geo_country
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'worker_status' AND column_name = 'geo_country') THEN
        ALTER TABLE public.worker_status ADD COLUMN geo_country TEXT;
    END IF;

    -- ip_authority_score
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'worker_status' AND column_name = 'ip_authority_score') THEN
        ALTER TABLE public.worker_status ADD COLUMN ip_authority_score FLOAT DEFAULT 1.0;
    END IF;

    -- Notify PostgREST to reload schema (optional but helpful in some environments)
    NOTIFY pgrst, 'reload schema';
END $$;
