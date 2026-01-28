-- =====================================================
-- EMERGENCY DATABASE OPERATIONS
-- =====================================================
-- Use these queries to fix immediate issues

-- 1. CHECK WHERE YOUR DATA IS
-- =====================================================

-- Count leads in results table
SELECT COUNT(*) as total_leads FROM results;

-- Count by job status
SELECT 
    j.status,
    COUNT(r.id) as lead_count,
    j.target_query,
    j.created_at
FROM jobs j
LEFT JOIN results r ON j.id = r.job_id
GROUP BY j.id, j.status, j.target_query, j.created_at
ORDER BY j.created_at DESC
LIMIT 20;

-- See your most recent leads
SELECT 
    (data_payload->>'name') as company_name,
    (data_payload->>'phone') as phone,
    (data_payload->>'website') as website,
    created_at,
    job_id
FROM results
ORDER BY created_at DESC
LIMIT 50;


-- 2. CANCEL ALL STUCK/PENDING JOBS
-- =====================================================
-- WARNING: This cancels ALL non-completed jobs

UPDATE jobs 
SET status = 'cancelled', 
    completed_at = NOW()
WHERE status IN ('queued', 'processing', 'claimed')
  AND created_at < NOW() - INTERVAL '1 hour';

-- Check what will be cancelled first:
-- SELECT id, target_query, status, created_at 
-- FROM jobs 
-- WHERE status IN ('queued', 'processing', 'claimed')
--   AND created_at < NOW() - INTERVAL '1 hour';


-- 3. KILL SPECIFIC LONG-RUNNING JOB
-- =====================================================
-- Replace 'job-id-here' with the actual job ID

UPDATE jobs 
SET status = 'cancelled', 
    completed_at = NOW()
WHERE id = 'job-id-here';


-- 4. CLEAR THE ENTIRE QUEUE (NUCLEAR OPTION)
-- =====================================================
-- Use this ONLY if you want to start completely fresh

-- UPDATE jobs 
-- SET status = 'cancelled'
-- WHERE status IN ('queued', 'processing', 'claimed');


-- 5. CHECK WORKER STATUS
-- =====================================================
-- See which hydras are running and what they're doing

SELECT 
    worker_id,
    status,
    last_pulse,
    NOW() - last_pulse as time_since_pulse
FROM worker_status
ORDER BY last_pulse DESC;


-- 6. SEE JOBS BY RESULT COUNT
-- =====================================================
-- Find jobs that found leads vs those that didn't

SELECT 
    j.id,
    j.target_query,
    j.status,
    j.result_count,
    j.created_at,
    j.completed_at,
    EXTRACT(EPOCH FROM (j.completed_at - j.created_at))/60 as duration_minutes
FROM jobs j
WHERE j.created_at > NOW() - INTERVAL '24 hours'
ORDER BY j.created_at DESC;


-- 7. DEDUPLICATE RESULTS (IF NEEDED)
-- =====================================================
-- Remove duplicate leads based on email or company name

-- First, see duplicates:
SELECT 
    (data_payload->>'email') as email,
    COUNT(*) as duplicate_count
FROM results
WHERE (data_payload->>'email') IS NOT NULL
GROUP BY (data_payload->>'email')
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- Delete all but the first occurrence of each email:
-- DELETE FROM results
-- WHERE id NOT IN (
--     SELECT MIN(id)
--     FROM results
--     GROUP BY (data_payload->>'email')
-- );


-- 8. EXPORT CLEAN DATA RIGHT NOW
-- =====================================================
-- Get your current leads in a clean format

SELECT 
    (data_payload->>'name') as company_name,
    (data_payload->>'website') as website,
    (data_payload->>'phone') as phone,
    (data_payload->>'address') as address,
    (data_payload->>'rating') as rating,
    email,
    decision_maker_name,
    decision_maker_title,
    employee_count,
    industry,
    created_at
FROM results
WHERE verified = true
ORDER BY data_quality_score DESC NULLS LAST, created_at DESC
LIMIT 1000;
