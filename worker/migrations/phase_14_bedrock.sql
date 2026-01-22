-- PHASE 14: THE BEDROCK - DATABASE MIGRATIONS

-- 1. Extend RESULTS table for Geographic Intelligence & Extension Sync
ALTER TABLE results 
ADD COLUMN IF NOT EXISTS capture_source TEXT DEFAULT 'swarm',
ADD COLUMN IF NOT EXISTS geo_lat DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS geo_lng DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS last_contacted_at TIMESTAMP WITH TIME ZONE;

-- 1a. Extend ORGANIZATIONS table for Integrations (The Invisible Hand v2)
ALTER TABLE organizations
ADD COLUMN IF NOT EXISTS slack_webhook TEXT,
ADD COLUMN IF NOT EXISTS outbound_webhook TEXT;

-- 2. Create GEOCODING_CACHE for high-performance Map Intelligence
CREATE TABLE IF NOT EXISTS geocoding_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    address_string TEXT UNIQUE NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create OUTREACH_CAMPAIGNS (Ghostwriter v2 Foundations)
CREATE TABLE IF NOT EXISTS outreach_campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create OUTREACH_SEQUENCES (Multi-step Drip Campaigns)
CREATE TABLE IF NOT EXISTS outreach_sequences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID REFERENCES outreach_campaigns(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    template_id TEXT,
    delay_hours INTEGER DEFAULT 24,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Create OUTREACH_LOGS (Engagement Analytics)
CREATE TABLE IF NOT EXISTS outreach_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES results(id) ON DELETE SET NULL,
    campaign_id UUID REFERENCES outreach_campaigns(id) ON DELETE SET NULL,
    status TEXT DEFAULT 'sent' CHECK (status IN ('sent', 'opened', 'replied', 'bounced')),
    provider_message_id TEXT,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Add Indexing for Performance
CREATE INDEX IF NOT EXISTS idx_results_geo ON results(geo_lat, geo_lng);
CREATE INDEX IF NOT EXISTS idx_outreach_logs_lead ON outreach_logs(lead_id);
CREATE INDEX IF NOT EXISTS idx_outreach_logs_campaign ON outreach_logs(campaign_id);
