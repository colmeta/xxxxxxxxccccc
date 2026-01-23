-- CLARITY PEARL - DATA SEPARATION & DEDUPLICATION SYSTEM
-- Purpose: Prevent duplicate lead delivery and enable category-based tracking
-- Date: 2026-01-23

-- ============================================
-- 1. ADD CATEGORY & DELIVERY TRACKING TO JOBS
-- ============================================

-- Add category field to jobs table
ALTER TABLE public.jobs 
ADD COLUMN IF NOT EXISTS category TEXT,
ADD COLUMN IF NOT EXISTS exclude_delivered BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS delivery_metadata JSONB DEFAULT '{}';

COMMENT ON COLUMN public.jobs.category IS 'Search category for grouping (e.g., "SaaS CEOs", "Marketing Agencies")';
COMMENT ON COLUMN public.jobs.exclude_delivered IS 'If true, exclude companies already delivered to this org in this category';
COMMENT ON COLUMN public.jobs.delivery_metadata IS 'Tracking info: delivered_at, delivered_to_client, delivery_id, etc.';

-- ============================================
-- 2. DELIVERED LEADS TRACKING TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS public.delivered_leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE NOT NULL,
  job_id UUID REFERENCES public.jobs(id) ON DELETE SET NULL,
  company_identifier TEXT NOT NULL, -- Normalized hash of company name + domain
  company_name TEXT, -- Original company name for display
  company_domain TEXT, -- Website domain
  category TEXT NOT NULL, -- e.g., "SaaS CEOs", "Marketing Agencies"
  result_id UUID REFERENCES public.results(id) ON DELETE SET NULL,
  delivered_at TIMESTAMPTZ DEFAULT NOW(),
  delivery_method TEXT DEFAULT 'csv_export', -- 'csv_export', 'api', 'email'
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.delivered_leads IS 'Tracks which companies were delivered to which clients to prevent duplicates';

-- Indexes for fast duplicate checking
CREATE INDEX IF NOT EXISTS idx_delivered_org_category ON public.delivered_leads(org_id, category);
CREATE INDEX IF NOT EXISTS idx_delivered_company_hash ON public.delivered_leads(company_identifier);
CREATE INDEX IF NOT EXISTS idx_delivered_org_company ON public.delivered_leads(org_id, company_identifier);

-- Unique constraint: same company can't be delivered twice to same org in same category
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_delivery 
ON public.delivered_leads(org_id, company_identifier, category);

-- ============================================
-- 3. COMPANY NORMALIZATION FUNCTION===
-- ============================================

CREATE OR REPLACE FUNCTION public.fn_normalize_company(
  p_company_name TEXT,
  p_company_domain TEXT
)
RETURNS TEXT AS $$
DECLARE
  normalized_name TEXT;
  normalized_domain TEXT;
  company_hash TEXT;
BEGIN
  -- Normalize company name: lowercase, remove punctuation, trim
  normalized_name := LOWER(TRIM(REGEXP_REPLACE(p_company_name, '[^a-zA-Z0-9\s]', '', 'g')));
  normalized_name := REGEXP_REPLACE(normalized_name, '\s+', ' ', 'g'); -- collapse multiple spaces
  
  -- Normalize domain: lowercase, remove www, protocols
  IF p_company_domain IS NOT NULL THEN
    normalized_domain := LOWER(p_company_domain);
    normalized_domain := REGEXP_REPLACE(normalized_domain, '^(https?://)?(www\.)?', '', 'i');
    normalized_domain := REGEXP_REPLACE(normalized_domain, '/.*$', ''); -- remove path
  ELSE
    normalized_domain := '';
  END IF;
  
  -- Create hash from name + domain
  company_hash := MD5(normalized_name || '|' || normalized_domain);
  
  RETURN company_hash;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION public.fn_normalize_company IS 'Creates consistent hash for company matching across different scrapes';

-- ============================================
-- 4. CHECK IF COMPANY ALREADY DELIVERED
-- ============================================

CREATE OR REPLACE FUNCTION public.fn_check_duplicate(
  p_org_id UUID,
  p_company_name TEXT,
  p_company_domain TEXT,
  p_category TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
  company_hash TEXT;
  is_duplicate BOOLEAN;
BEGIN
  -- Normalize company
  company_hash := public.fn_normalize_company(p_company_name, p_company_domain);
  
  -- Check if exists in delivered_leads
  SELECT EXISTS(
    SELECT 1 FROM public.delivered_leads
    WHERE org_id = p_org_id
      AND company_identifier = company_hash
      AND category = p_category
  ) INTO is_duplicate;
  
  RETURN is_duplicate;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.fn_check_duplicate IS 'Returns true if company was already delivered to this org in this category';

-- ============================================
-- 5. MARK RESULTS AS DELIVERED
-- ============================================

CREATE OR REPLACE FUNCTION public.fn_mark_as_delivered(
  p_org_id UUID,
  p_job_id UUID,
  p_category TEXT,
  p_delivery_method TEXT DEFAULT 'csv_export'
)
RETURNS INT AS $$
DECLARE
  inserted_count INT := 0;
  result_record RECORD;
  company_hash TEXT;
BEGIN
  -- Get all results for this job that aren't already marked as delivered
  FOR result_record IN 
    SELECT 
      r.id as result_id,
      r.data_payload->>'name' as company_name,
      r.data_payload->>'company' as alt_company_name,
      r.data_payload->>'website' as company_domain
    FROM public.results r
    WHERE r.job_id = p_job_id
  LOOP
    -- Use company name from data_payload (could be 'name' or 'company' field)
    DECLARE
      final_company_name TEXT;
    BEGIN
      final_company_name := COALESCE(result_record.company_name, result_record.alt_company_name, 'Unknown');
      
      -- Normalize
      company_hash := public.fn_normalize_company(final_company_name, result_record.company_domain);
      
      -- Insert (on conflict do nothing to avoid duplicates)
      INSERT INTO public.delivered_leads (
        org_id,
        job_id,
        company_identifier,
        company_name,
        company_domain,
        category,
        result_id,
        delivery_method
      )
      VALUES (
        p_org_id,
        p_job_id,
        company_hash,
        final_company_name,
        result_record.company_domain,
        p_category,
        result_record.result_id,
        p_delivery_method
      )
      ON CONFLICT ON CONSTRAINT idx_unique_delivery DO NOTHING;
      
      IF FOUND THEN
        inserted_count := inserted_count + 1;
      END IF;
    END;
  END LOOP;
  
  -- Update job metadata
  UPDATE public.jobs
  SET delivery_metadata = jsonb_set(
    COALESCE(delivery_metadata, '{}'::jsonb),
    '{delivered_at}',
    to_jsonb(NOW())
  )
  WHERE id = p_job_id;
  
  RETURN inserted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.fn_mark_as_delivered IS 'Marks all results from a job as delivered to prevent future duplicates';

-- ============================================
-- 6. GET CATEGORY DELIVERY STATS
-- ============================================

CREATE OR REPLACE FUNCTION public.fn_get_category_stats(
  p_org_id UUID,
  p_category TEXT DEFAULT NULL
)
RETURNS TABLE (
  category TEXT,
  total_delivered INT,
  last_delivery_date TIMESTAMPTZ,
  unique_companies INT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    dl.category,
    COUNT(*)::INT as total_delivered,
    MAX(dl.delivered_at) as last_delivery_date,
    COUNT(DISTINCT dl.company_identifier)::INT as unique_companies
  FROM public.delivered_leads dl
  WHERE dl.org_id = p_org_id
    AND (p_category IS NULL OR dl.category = p_category)
  GROUP BY dl.category
  ORDER BY last_delivery_date DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.fn_get_category_stats IS 'Shows delivery statistics per category for an organization';

-- ============================================
-- 7. RLS POLICIES FOR DELIVERED_LEADS
-- ============================================

ALTER TABLE public.delivered_leads ENABLE ROW LEVEL SECURITY;

-- Users can only see delivered leads for their own organization
CREATE POLICY "Users can view own org deliveries" ON public.delivered_leads
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.memberships m
      WHERE m.org_id = delivered_leads.org_id
        AND m.user_id = auth.uid()
    )
  );

-- ============================================
-- 8. HELPER VIEW FOR EASY QUERYING
-- ============================================

CREATE OR REPLACE VIEW public.v_delivery_history AS
SELECT 
  dl.id,
  dl.org_id,
  o.name as org_name,
  dl.category,
  dl.company_name,
  dl.company_domain,
  dl.delivered_at,
  dl.delivery_method,
  j.target_query,
  j.result_count as job_result_count
FROM public.delivered_leads dl
LEFT JOIN public.organizations o ON o.id = dl.org_id
LEFT JOIN public.jobs j ON j.id = dl.job_id
ORDER BY dl.delivered_at DESC;

COMMENT ON VIEW public.v_delivery_history IS 'Easy-to-query view of all delivery history with org and job details';

-- ============================================
-- 9. AUTO-CATEGORIZE EXISTING JOBS (OPTIONAL)
-- ============================================

-- This is a one-time migration to categorize existing jobs
-- Run this AFTER deploying the schema changes

DO $$
DECLARE
  job_record RECORD;
  detected_category TEXT;
BEGIN
  FOR job_record IN 
    SELECT id, target_query 
    FROM public.jobs 
    WHERE category IS NULL
  LOOP
    -- Simple keyword-based categorization
    detected_category := CASE
      WHEN job_record.target_query ILIKE '%saas%' OR job_record.target_query ILIKE '%software%' THEN 'SaaS Companies'
      WHEN job_record.target_query ILIKE '%ceo%' OR job_record.target_query ILIKE '%founder%' THEN 'C-Level Executives'
      WHEN job_record.target_query ILIKE '%marketing%' OR job_record.target_query ILIKE '%agency%' THEN 'Marketing Agencies'
      WHEN job_record.target_query ILIKE '%real estate%' OR job_record.target_query ILIKE '%realtor%' THEN 'Real Estate'
      WHEN job_record.target_query ILIKE '%restaurant%' OR job_record.target_query ILIKE '%food%' THEN 'Food & Beverage'
      ELSE 'Uncategorized'
    END;
    
    UPDATE public.jobs
    SET category = detected_category
    WHERE id = job_record.id;
  END LOOP;
  
  RAISE NOTICE 'Categorized % existing jobs', (SELECT COUNT(*) FROM public.jobs WHERE category IS NOT NULL);
END $$;

-- ============================================
-- DEPLOYMENT COMPLETE
-- ============================================

-- Verify deployment
SELECT 
  'delivered_leads table' as object,
  COUNT(*) as row_count
FROM public.delivered_leads
UNION ALL
SELECT 
  'jobs with categories' as object,
  COUNT(*) as row_count
FROM public.jobs
WHERE category IS NOT NULL;
