-- =====================================================
-- DATABASE CLEANUP: Client-Ready Schema
-- =====================================================
-- This script creates a clean VIEW that shows only what clients need,
-- and adds dataset organization columns.
-- =====================================================

-- Step 1: Add Dataset Organization Columns
-- =====================================================
ALTER TABLE results ADD COLUMN IF NOT EXISTS dataset_name VARCHAR(255);
ALTER TABLE results ADD COLUMN IF NOT EXISTS tags TEXT[]; -- Array for filtering

-- Example usage:
-- UPDATE results SET dataset_name = 'Roofers - Austin TX' WHERE job_id = 'xxx';
-- UPDATE results SET tags = ARRAY['roofers', 'texas', 'home-services'] WHERE job_id = 'xxx';


-- Step 2: Create Client-Facing View
-- =====================================================
-- This view shows ONLY the columns clients care about.
-- Internal tracking columns are hidden.

CREATE OR REPLACE VIEW client_data AS
SELECT 
    -- Identifiers
    id,
    dataset_name,
    tags,
    created_at,
    
    -- Company Info (from data_payload - adjust field names as needed)
    (data_payload->>'name') as company_name,
    (data_payload->>'website') as website,
    (data_payload->>'phone') as phone,
    (data_payload->>'address') as address,
    (data_payload->>'rating') as rating,
    (data_payload->>'review_count') as review_count,
    
    -- Contact Info (manually enriched)
    email,
    email_verification_status,
    decision_maker_name,
    decision_maker_title,
    decision_maker_email,
    decision_maker_linkedin_url,
    
    -- Company Details
    employee_count,
    industry,
    category_raw,
    company_description,
    revenue_estimate,
    technologies_used,
    
    -- Location
    geo_lat,
    geo_lng,
    
    -- Quality
    data_quality_score
    
FROM results
WHERE verified IS NOT FALSE  -- Only show verified/clean data
ORDER BY data_quality_score DESC NULLS LAST;


-- Step 3: Create Export Function
-- =====================================================
-- Function to export a specific dataset as CSV

CREATE OR REPLACE FUNCTION export_dataset(p_dataset_name TEXT)
RETURNS TABLE (
    company_name TEXT,
    website TEXT,
    phone TEXT,
    email TEXT,
    decision_maker_name TEXT,
    decision_maker_title TEXT,
    decision_maker_email TEXT,
    employee_count TEXT,
    industry TEXT,
    address TEXT,
    rating TEXT,
    data_quality_score INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (data_payload->>'name')::TEXT,
        (data_payload->>'website')::TEXT,
        (data_payload->>'phone')::TEXT,
        r.email::TEXT,
        r.decision_maker_name::TEXT,
        r.decision_maker_title::TEXT,
        r.decision_maker_email::TEXT,
        r.employee_count::TEXT,
        r.industry::TEXT,
        (data_payload->>'address')::TEXT,
        (data_payload->>'rating')::TEXT,
        r.data_quality_score
    FROM results r
    WHERE r.dataset_name = p_dataset_name
    ORDER BY r.data_quality_score DESC NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- Usage: SELECT * FROM export_dataset('Roofers - Austin TX');


-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- 1. See only client-facing data
-- SELECT * FROM client_data LIMIT 10;

-- 2. List all datasets
-- SELECT dataset_name, COUNT(*) as lead_count 
-- FROM results 
-- WHERE dataset_name IS NOT NULL 
-- GROUP BY dataset_name 
-- ORDER BY lead_count DESC;

-- 3. Export specific dataset
-- SELECT * FROM export_dataset('Roofers - Austin TX');
