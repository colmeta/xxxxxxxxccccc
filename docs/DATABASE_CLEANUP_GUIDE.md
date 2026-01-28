# 🧹 Database Cleanup & Dataset Organization Guide

## Problem Solved
1. **Too Many Confusing Columns:** Clients don't need to see 46 internal tracking columns.
2. **Mixed Data:** Roofers shouldn't be mixed with marketing agencies.

## ✅ The Solution

I've created a **Client-Facing View** that shows only the 18 columns clients actually care about.

---

## 📊 Column Breakdown

### What Clients SEE (Client-Facing View)
| Column | Purpose | Example |
|--------|---------|---------|
| `company_name` | Business name | "Austin Roofing Pro" |
| `website` | Company website | "austinroofing.com" |
| `phone` | Contact number | "+1-512-555-1234" |
| `email` | General email | "info@austinroofing.com" |
| `decision_maker_name` | Owner/CEO name | "John Smith" |
| `decision_maker_title` | Their role | "Owner" |
| `decision_maker_email` | Direct email | "john@austinroofing.com" |
| `employee_count` | Company size | "11-50" |
| `industry` | Business type | "Roofing Contractor" |
| `revenue_estimate` | Income range | "$1M-$5M" |
| `data_quality_score` | Quality rating | 85/100 |
| `dataset_name` | Which list they belong to | "Roofers - Austin TX" |

### What Clients DON'T See (Hidden)
All internal columns are hidden from client exports:
- `job_id`, `capture_source`, `data_payload` (internal tracking)
- `intent_score`, `clarity_score`, `truth_score` (AI scoring)
- `outreach_draft`, `outreach_status` (CRM features)
- `oracle_signal`, `reasoning`, `verdict` (AI internals)

---

## 🗂️ Dataset Organization

### Step 1: Add Dataset Names to Your Leads

After running a scraping job, tag your results:

```sql
-- Tag all leads from Job #123 as "Roofers - Austin TX"
UPDATE results 
SET dataset_name = 'Roofers - Austin TX',
    tags = ARRAY['roofers', 'texas', 'home-services']
WHERE job_id = 'your-job-id-here';
```

### Step 2: View Your Datasets

```sql
-- See all your organized datasets
SELECT dataset_name, COUNT(*) as lead_count 
FROM results 
WHERE dataset_name IS NOT NULL 
GROUP BY dataset_name 
ORDER BY lead_count DESC;
```

Example output:
```
dataset_name              | lead_count
--------------------------|-----------
Roofers - Austin TX       | 547
Digital Agencies - NYC    | 423
Dentists - California     | 891
```

---

## 📥 How to Export Clean Data for Clients

### Method 1: Quick Export (using the view)
```sql
SELECT * FROM client_data 
WHERE dataset_name = 'Roofers - Austin TX';
```

Then click **"Export to CSV"** in Supabase.

### Method 2: Advanced Export (using the function)
```sql
SELECT * FROM export_dataset('Roofers - Austin TX');
```

This gives you a perfectly formatted CSV ready to sell.

---

## 🛠️ Setup Instructions

### 1. Run the Cleanup Script
- Open **Supabase SQL Editor**
- Copy contents of `database_cleanup_and_segmentation.sql`
- Run it

This creates:
- ✅ `dataset_name` column (for organizing lists)
- ✅ `tags` column (for filtering)
- ✅ `client_data` view (clean export view)
- ✅ `export_dataset()` function (one-click exports)

### 2. Tag Your Existing Data

After migration, organize your current leads:

```sql
-- Example: Tag all jobs for "Roofing companies in Austin"
UPDATE results 
SET dataset_name = 'Roofers - Austin TX'
WHERE (data_payload->>'name') ILIKE '%roof%' 
  AND (data_payload->>'address') ILIKE '%Austin%';
```

### 3. Test the Export

```sql
SELECT * FROM client_data 
WHERE dataset_name = 'Roofers - Austin TX' 
LIMIT 10;
```

You should see ONLY the clean columns, no internal clutter.

---

## 📋 Naming Convention for Datasets

Use this format for consistency:
```
[Industry] - [Location]
```

Examples:
- ✅ `Roofers - Austin TX`
- ✅ `Digital Agencies - New York City`
- ✅ `Dentists - Los Angeles CA`
- ✅ `E-commerce Brands - USA`
- ❌ `list123` (too vague)
- ❌ `my data` (not specific)

---

## 🎯 Workflow for Clean Data Sales

### 1. Scrape a Specific List
Run your Pearl platform:
```bash
Search: "Roofing companies in Austin TX"
Platform: google_maps
```

### 2. Tag the Results
```sql
UPDATE results 
SET dataset_name = 'Roofers - Austin TX',
    tags = ARRAY['roofers', 'texas', 'construction']
WHERE job_id = 'abc-123-xyz';
```

### 3. Manually Enrich (Add Emails/Decision Makers)
Use the methods from `MANUAL_ENRICHMENT_GUIDE.md` to add:
- Emails
- Decision maker names
- Employee counts

### 4. Export for Client
```sql
SELECT * FROM export_dataset('Roofers - Austin TX');
```

Download CSV → Sell for $297 (547 leads × $0.54/lead).

---

## ✅ Benefits

**Before:**
- ❌ 46 confusing columns
- ❌ All data mixed together
- ❌ Clients see "job_id", "oracle_signal", "velocity_data" (confusing)

**After:**
- ✅ 12 clean, understandable columns
- ✅ Organized by dataset
- ✅ Professional CSV exports
- ✅ Easy to filter and search

---

## 🚀 Next Steps

1. Run `database_cleanup_and_segmentation.sql` in Supabase
2. Tag your existing data with dataset names
3. Test an export: `SELECT * FROM client_data LIMIT 10`
4. Start organizing new scrapes immediately with dataset names

Your data is now ready to sell as clean, segmented lists!
