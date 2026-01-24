-- CLEANUP SCRIPT - FRESH START
-- This removes all old test data while keeping the rock solid infrastructure intact
-- Run this to start fresh with clean, contact-rich searches

-- ============================================
-- STEP 1: BACKUP FIRST (Optional but recommended)
-- ============================================
-- CREATE TABLE jobs_backup AS SELECT * FROM jobs;
-- CREATE TABLE results_backup AS SELECT * FROM results;

-- ============================================
-- STEP 2: CLEAR OLD DATA
-- ============================================

-- Clear provenance logs (cascades from results)
DELETE FROM provenance_logs;

-- Clear results (all old scraped data)
DELETE FROM results;

-- Clear jobs (all old search missions)
DELETE FROM jobs;

-- Clear delivered leads tracking (start fresh)
DELETE FROM delivered_leads;

-- ============================================
-- STEP 3: VERIFY CLEANUP
-- ============================================

SELECT 'jobs' as table_name, COUNT(*) as remaining_rows FROM jobs
UNION ALL
SELECT 'results', COUNT(*) FROM results
UNION ALL
SELECT 'provenance_logs', COUNT(*) FROM provenance_logs
UNION ALL
SELECT 'delivered_leads', COUNT(*) FROM delivered_leads;

-- Expected: All counts should be 0

-- ============================================
-- STEP 4: INFRASTRUCTURE CHECK
-- ============================================

-- Verify all new tables and functions still exist
SELECT 
    'delivered_leads table exists' as check_name,
    EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'delivered_leads') as status
UNION ALL
SELECT 
    'fn_normalize_company exists',
    EXISTS(SELECT 1 FROM information_schema.routines WHERE routine_name = 'fn_normalize_company')
UNION ALL
SELECT 
    'fn_check_duplicate exists',
    EXISTS(SELECT 1 FROM information_schema.routines WHERE routine_name = 'fn_check_duplicate')
UNION ALL
SELECT 
    'fn_mark_as_delivered exists',
    EXISTS(SELECT 1 FROM information_schema.routines WHERE routine_name = 'fn_mark_as_delivered');

-- All should show TRUE

-- ============================================
-- DONE! Database is clean and ready for fresh data
-- ============================================
