-- Temporary script to create profile for existing user
-- Run this in Supabase SQL Editor if your account already exists

-- Replace YOUR_USER_ID with your actual user ID from auth.users
-- You can find it by running: SELECT id, email FROM auth.users;

INSERT INTO public.profiles (id, email, credits_remaining)
SELECT id, email, 100
FROM auth.users
WHERE email = 'YOUR_EMAIL_HERE'
ON CONFLICT (id) DO NOTHING;
