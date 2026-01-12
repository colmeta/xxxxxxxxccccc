-- ENHANCED ONBOARDING: Auto-create Profile, Organization, and Membership
CREATE OR REPLACE FUNCTION public.handle_new_user()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = public
AS $function$
declare
  new_org_id uuid;
  company_name text;
  full_name text;
begin
  -- 1. Extract metadata (passed from frontend signUp/signInWithOtp)
  full_name := coalesce(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1));
  company_name := coalesce(new.raw_user_meta_data->>'company_name', full_name || '''s Lab');

  -- 2. Create Profile
  -- Use ON CONFLICT do nothing in case profile already existed (though rare in this trigger)
  insert into public.profiles (id, email, full_name, credits_remaining)
  values (new.id, new.email, full_name, 100)
  on conflict (id) do update 
  set full_name = excluded.full_name, email = excluded.email;

  -- 3. Create Organization for the new user
  insert into public.organizations (name, owner_id, plan_tier, credits_monthly, credits_used)
  values (company_name, new.id, 'starter', 1000, 0)
  returning id into new_org_id;

  -- 4. Create Membership linking user as owner
  insert into public.memberships (org_id, user_id, role)
  values (new_org_id, new.id, 'owner');

  -- 5. Set active organization for the profile
  update public.profiles
  set active_org_id = new_org_id
  where id = new.id;

  return new;
end;
$function$;

-- Ensure the trigger is attached (it should be from previous migrations, but safe to re-assert)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
