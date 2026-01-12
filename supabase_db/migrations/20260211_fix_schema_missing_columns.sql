-- Fix missing columns detected during worker execution

-- 1. Add oracle_signal to results table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'results' AND column_name = 'oracle_signal') THEN
        ALTER TABLE results ADD COLUMN oracle_signal TEXT DEFAULT 'Baseline';
    END IF;
END $$;

-- 2. Add active_missions to worker_status table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'worker_status' AND column_name = 'active_missions') THEN
        ALTER TABLE worker_status ADD COLUMN active_missions JSONB DEFAULT '[]'::jsonb;
    END IF;
END $$;

-- 3. Ensure other potential missing AI columns exist in results
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'results' AND column_name = 'intent_score') THEN
        ALTER TABLE results ADD COLUMN intent_score INTEGER DEFAULT 0;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'results' AND column_name = 'predictive_growth_score') THEN
        ALTER TABLE results ADD COLUMN predictive_growth_score INTEGER DEFAULT 0;
    END IF;
END $$;
