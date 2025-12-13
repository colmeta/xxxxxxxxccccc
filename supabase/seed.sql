-- SEED DATA FOR CLARITY PEARL
-- User: test@claritypearl.io / password (managed by auth)
-- ID: a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11

INSERT INTO auth.users (id, email, encrypted_password, email_confirmed_at, raw_app_meta_data, raw_user_meta_data)
VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'test@claritypearl.io',
    extensions.crypt('password123', extensions.gen_salt('bf')),
    now(),
    '{"provider":"email","providers":["email"]}',
    '{"full_name":"Test User"}'
) ON CONFLICT (id) DO NOTHING;

-- Profile (Trigger automatically creates it, but we can update it)
-- We wait a sec or just update it if it exists, or insert if trigger didn't run (unlikely in seed transaction)
-- For seed, we can just insert if not exists to be safe, or update.
-- Since trigger runs AFTER insert on auth.users, row should be there.
UPDATE public.profiles
SET 
  full_name = 'Test User',
  company_name = 'Pearl Intelligence Ltd',
  plan_tier = 'pro',
  credits_remaining = 500
WHERE id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';

-- Jobs
INSERT INTO public.jobs (id, user_id, status, target_query, target_platform, result_count)
VALUES
  ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'completed', 'Software Engineers in San Francisco', 'linkedin', 2),
  ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'queued', 'Marketing Agencies in London', 'google_maps', 0),
  ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a44', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'running', 'CFOs in New York', 'linkedin', 0);

-- Results (for the completed job)
INSERT INTO public.results (id, job_id, data_payload, verified)
VALUES
  ('r1eebc99-9c0b-4ef8-bb6d-6bb9bd380a55', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', '{"name": "Alice Smith", "title": "Senior SWE", "company": "Tech Corp", "url": "linkedin.com/in/alice"}', true),
  ('r2eebc99-9c0b-4ef8-bb6d-6bb9bd380a66', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', '{"name": "Bob Jones", "title": "Staff Engineer", "company": "Data Inc", "url": "linkedin.com/in/bob"}', true);

-- Provenance Logs
INSERT INTO public.provenance_logs (result_id, source_url, legal_basis, arbiter_verdict)
VALUES
  ('r1eebc99-9c0b-4ef8-bb6d-6bb9bd380a55', 'https://linkedin.com/in/alice', 'Legitimate Interest', 'Verified Public Profile'),
  ('r2eebc99-9c0b-4ef8-bb6d-6bb9bd380a66', 'https://linkedin.com/in/bob', 'Legitimate Interest', 'Verified Public Profile');
