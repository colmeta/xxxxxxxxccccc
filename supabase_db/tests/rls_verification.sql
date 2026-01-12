-- RLS VERIFICATION SCRIPT
-- Run this in the Supabase SQL Editor to test security.

-- 1. Create a second malicious user 'evil@hacker.com'
INSERT INTO auth.users (id, email) 
VALUES ('99999999-9999-9999-9999-999999999999', 'evil@hacker.com')
ON CONFLICT DO NOTHING;

-- 2. Switch to 'evil' user context
SET ROLE authenticated;
SET request.jwt.claim.sub = '99999999-9999-9999-9999-999999999999';
SET request.jwt.claim.role = 'authenticated';

-- 3. Attempt to read Test User's jobs (Should be empty)
SELECT 'Testing Job Isolation for Evil User' as test_case;
SELECT * FROM public.jobs WHERE user_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';

-- 4. Switch to 'Test User' context
SET request.jwt.claim.sub = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';

-- 5. Attempt to read Test User's jobs (Should see 3 jobs)
SELECT 'Testing Job Access for Owner' as test_case;
SELECT count(*) as my_job_count FROM public.jobs;

-- 6. Claim Job Test (Function Logic)
-- As the authorized user, let's claim a job (this usually run by a worker service role, but let's test visibility)
SELECT * FROM public.fn_claim_job(); 
-- Note: If fn_claim_job is SECURITY DEFINER, it runs as database owner, so it bypasses RLS for the update, 
-- but we should check if we want workers to be a specific role. 
-- For now, the function is SECURITY DEFINER so it will work.

RESET ROLE;
