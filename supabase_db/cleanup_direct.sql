-- DIRECT CLEANUP - Paste this entire script into your SQL editor
-- This removes all old test data while keeping infrastructure

-- Clear provenance logs
DELETE FROM provenance_logs;

-- Clear results (all old scraped data)
DELETE FROM results;

-- Clear jobs (all old search missions)  
DELETE FROM jobs;

-- Clear delivered leads tracking (fresh start)
DELETE FROM delivered_leads;

-- Verify cleanup (all should show 0)
SELECT 'jobs' as table_name, COUNT(*) as remaining_rows FROM jobs
UNION ALL
SELECT 'results', COUNT(*) FROM results
UNION ALL
SELECT 'provenance_logs', COUNT(*) FROM provenance_logs
UNION ALL
SELECT 'delivered_leads', COUNT(*) FROM delivered_leads;
