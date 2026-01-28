-- =====================================================
-- DATABASE MIGRATION: Add Manual Enrichment Fields
-- Table: results (NOT leads - that was the error!)
-- =====================================================

-- Email fields (highest priority)
ALTER TABLE results ADD COLUMN IF NOT EXISTS email VARCHAR(255);
ALTER TABLE results ADD COLUMN IF NOT EXISTS email_verification_status VARCHAR(50);
ALTER TABLE results ADD COLUMN IF NOT EXISTS email_confidence VARCHAR(20);
ALTER TABLE results ADD COLUMN IF NOT EXISTS email_source VARCHAR(100);

-- Decision maker fields
ALTER TABLE results ADD COLUMN IF NOT EXISTS decision_maker_name VARCHAR(255);
ALTER TABLE results ADD COLUMN IF NOT EXISTS decision_maker_title VARCHAR(255);
ALTER TABLE results ADD COLUMN IF NOT EXISTS decision_maker_linkedin_url VARCHAR(500);
ALTER TABLE results ADD COLUMN IF NOT EXISTS decision_maker_email VARCHAR(255);

-- Company size
ALTER TABLE results ADD COLUMN IF NOT EXISTS employee_count VARCHAR(50);
ALTER TABLE results ADD COLUMN IF NOT EXISTS employee_count_source VARCHAR(50);

-- Industry
ALTER TABLE results ADD COLUMN IF NOT EXISTS industry VARCHAR(100);
ALTER TABLE results ADD COLUMN IF NOT EXISTS category_raw VARCHAR(255);
ALTER TABLE results ADD COLUMN IF NOT EXISTS industry_confidence VARCHAR(20);

-- Quality scoring
ALTER TABLE results ADD COLUMN IF NOT EXISTS data_quality_score INT; -- 0-100
ALTER TABLE results ADD COLUMN IF NOT EXISTS last_manual_enrichment_date TIMESTAMP;
ALTER TABLE results ADD COLUMN IF NOT EXISTS manual_enrichment_by VARCHAR(100); -- user who enriched

-- Client-facing fields
ALTER TABLE results ADD COLUMN IF NOT EXISTS company_description TEXT;
ALTER TABLE results ADD COLUMN IF NOT EXISTS revenue_estimate VARCHAR(50); -- '$1M-$5M', '$5M-$10M', etc
ALTER TABLE results ADD COLUMN IF NOT EXISTS technologies_used TEXT; -- 'WordPress, Shopify, Stripe'

-- =====================================================
-- VERIFICATION QUERY
-- Run this after migration to confirm columns exist:
-- =====================================================
-- SELECT column_name, data_type 
-- FROM information_schema.columns 
-- WHERE table_name = 'results' 
-- ORDER BY column_name;
