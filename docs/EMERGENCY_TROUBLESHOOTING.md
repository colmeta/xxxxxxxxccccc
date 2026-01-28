# 🚨 Emergency Troubleshooting Guide

## Issue 1: Only 9 Rows Visible (But Interface Shows More)

### Possible Causes:
1. **Data is in `data_payload` JSON column** - Not extracted to top-level columns
2. **Jobs are stuck in "processing" status** - Leads collected but job never marked complete
3. **Frontend showing cached data** - Not the actual database

### Fix It Now:

**Step 1: Check actual lead count**
```sql
SELECT COUNT(*) FROM results;
```

If this shows more than 9, your data IS there, just not displayed correctly.

**Step 2: See your recent leads**
```sql
SELECT 
    (data_payload->>'name') as company_name,
    (data_payload->>'phone') as phone,
    created_at
FROM results
ORDER BY created_at DESC
LIMIT 50;
```

**Step 3: Check job statuses**
```sql
SELECT status, COUNT(*) 
FROM jobs 
GROUP BY status;
```

If you see many "processing" or "claimed" jobs → They're stuck!

---

## Issue 2: Cancel Old/Stuck Jobs

### Quick Fix (Cancel everything older than 1 hour):
```sql
UPDATE jobs 
SET status = 'cancelled', 
    completed_at = NOW()
WHERE status IN ('queued', 'processing', 'claimed')
  AND created_at < NOW() - INTERVAL '1 hour';
```

### Nuclear Option (Clear entire queue):
```sql
UPDATE jobs 
SET status = 'cancelled'
WHERE status IN ('queued', 'processing');
```

After canceling, restart your hydra worker.

---

## Issue 3: Hydras Running for 3+ Hours

### Why This Happens:
1. **Google blocking** - Endless CAPTCHA loop
2. **Infinite scroll bug** - Keeps scrolling forever
3. **Memory leak** - RAM fills up, slows down
4. **No timeout** - Worker never gives up

### Fix:

**Immediate:** Kill the stuck job
```sql
-- Find long-running jobs
SELECT id, target_query, status, 
    EXTRACT(EPOCH FROM (NOW() - created_at))/60 as minutes_running
FROM jobs
WHERE status IN ('processing', 'claimed')
AND created_at < NOW() - INTERVAL '30 minutes'
ORDER BY created_at;

-- Kill it
UPDATE jobs 
SET status = 'cancelled'
WHERE id = 'paste-job-id-here';
```

**Prevention:** I'll add a 15-minute timeout to the worker code.

---

## Issue 4: Real-Time Data Saving

### Current Problem:
Worker collects all leads first, THEN saves them all at once. If it crashes, you lose everything.

### Solution:
The code ALREADY saves leads one-by-one in `_save_single_result()`. 

**To verify leads are appearing:**
```sql
-- This query refreshes every 5 seconds
SELECT 
    COUNT(*) as total_leads,
    MAX(created_at) as last_lead_time,
    NOW() - MAX(created_at) as seconds_since_last_lead
FROM results;
```

If `last_lead_time` is recent (< 30 sec ago), leads ARE being saved in real-time!

**If not appearing:** Check worker logs for errors.

---

## Issue 5: Start Working NOW - Best Strategy

### I recommend this approach:

**Instead of "Roofers in Austin"**, target businesses that DESPERATELY need marketing and will convert fast:

### 🎯 TOP 3 HIGH-CONVERTING NICHES

| Business Type | Why They Need Marketing | Urgency | Avg Budget |
|---------------|-------------------------|---------|------------|
| **New Restaurants** | 80% fail in first year without marketing | CRITICAL | $2k-5k/mo |
| **Personal Injury Lawyers** | 1 client = $50k+ revenue, need constant leads | HIGH | $5k-15k/mo |
| **Home Services (Emergency)** | Plumbers, HVAC lose $1000s/day without leads | HIGH | $1k-3k/mo |

### 🔥 HOT CITIES (Better than Austin)

| City | Why | Digital Agency Count | Conversion Rate |
|------|-----|---------------------|-----------------|
| **Miami, FL** | Tourism boom, lots of new businesses | 400+ | High |
| **Phoenix, AZ** | Fast-growing population, construction boom | 300+ | High |
| **Nashville, TN** | Hospitality/entertainment growth | 250+ | Medium-High |
| **Austin, TX** | Tech hub, well-funded startups | 500+ | Medium (saturated) |

**Strategic Pick:** Target **Miami Restaurants** → Sell to **Miami Digital Agencies**

---

## 🚀 Your Action Plan (Start in 15 Minutes)

### Phase 1: Clean Up (5 min)
1. Run `EMERGENCY_DATABASE_FIXES.sql` query #2 (cancel stuck jobs)
2. Restart hydra worker
3. Run query #1 to see your current lead count

### Phase 2: Strategic Scrape (10 min)
Run this query in your platform:
```
Target: "new restaurants Miami FL"
Platform: google_maps
```

This will get you 50-100 restaurant leads.

### Phase 3: Quick Manual Enrichment (30 min)
1. Pick top 20 restaurants (highest ratings)
2. Find owner on LinkedIn
3. Add email using Hunter.io free tier (25/month)
4. Now you have 20 PERFECT leads

### Phase 4: Create Lead Magnet & Sell (1 hour)
1. Export those 20 as CSV
2. Find 10 Miami marketing agencies on LinkedIn
3. DM them: "Hey, I have 20 new restaurants in Miami that need marketing. Want the list for free?"
4. After they say yes: "I have 500 more. $150 for the full list."

**Expected outcome:** 2-3 agencies buy = $300-450 in your pocket TODAY.

---

## 📊 Database Health Check

Run these NOW to see your system status:

```sql
-- How many leads do you actually have?
SELECT COUNT(*) FROM results;

-- How many jobs are stuck?
SELECT COUNT(*) FROM jobs WHERE status IN ('processing', 'claimed');

-- What's your newest lead?
SELECT 
    (data_payload->>'name') as name,
    created_at
FROM results
ORDER BY created_at DESC
LIMIT 1;
```

---

## Next Steps

1. Open Supabase SQL Editor
2. Run the queries from `EMERGENCY_DATABASE_FIXES.sql`
3. Tell me the results and I'll help you fix any issues
4. Then we'll start your Miami Restaurants scrape!
