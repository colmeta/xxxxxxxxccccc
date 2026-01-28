# 🔧 How to Apply the Database Migration

## The Issue
You got the error `relation "leads" does not exist` because your table is actually called **`results`**, not `leads`.

I found this by checking your codebase - all database operations use `.table('results')`.

---

## ✅ The Solution

I've created the corrected migration file:
**`docs/database_migration_add_manual_enrichment_fields.sql`**

### Step 1: Open Your Supabase Dashboard
1. Go to [supabase.com](https://supabase.com)
2. Log in and select your project
3. Click **"SQL Editor"** in the left sidebar

### Step 2: Copy and Run the Migration
1. Open the file: `docs/database_migration_add_manual_enrichment_fields.sql`
2. Copy ALL the SQL code
3. Paste it into the Supabase SQL Editor
4. Click **"Run"** (or press Ctrl+Enter)

### Step 3: Verify the Migration Worked
Run this verification query:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'results' 
ORDER BY column_name;
```

You should see all the new columns listed:
- `email`
- `email_verification_status`
- `decision_maker_name`
- `decision_maker_title`
- `employee_count`
- `industry`
- `data_quality_score`
- etc.

---

## 📋 What Was Added

**23 new columns** to make your data client-ready:

| Column | Purpose | Example Value |
|--------|---------|---------------|
| `email` | Contact email | `hello@acme.com` |
| `email_verification_status` | Deliverability check | `verified`, `bounced` |
| `decision_maker_name` | CEO/Founder name | `Sarah Johnson` |
| `decision_maker_title` | Their job title | `Founder & CEO` |
| `decision_maker_email` | Direct email | `sarah@acme.com` |
| `employee_count` | Company size | `11-50` |
| `industry` | Standardized industry | `Marketing & Advertising` |
| `data_quality_score` | Quality rating | `85` (out of 100) |
| `revenue_estimate` | Company revenue | `$1M-$5M` |
| `technologies_used` | Tech stack | `WordPress, Shopify` |

---

## 🚀 After Migration

Once the columns exist, you can start manually enriching your data:

### Option 1: Edit Directly in Supabase
1. Go to **Table Editor** → `results`
2. Find a lead
3. Click to edit
4. Fill in the new fields manually

### Option 2: Bulk Update via CSV
1. Export your `results` table
2. Add the new columns in Excel/Google Sheets
3. Re-import using Supabase's CSV import

### Option 3: Build a Simple Admin UI
Create a quick internal tool where you (or your VA) can:
- See a lead
- Click "Enrich"
- Fill in email, decision maker, company size
- Save

---

## ⚠️ Important Notes

1. **IF NOT EXISTS:** The migration uses `IF NOT EXISTS` so it's safe to run multiple times. Won't error if columns already exist.

2. **No Data Loss:** This only ADDS columns. Your existing data in the `results` table is 100% safe.

3. **Nullable:** All new columns allow NULL values, so existing rows won't break.

---

## ✅ You're Ready!

After running the migration, your database will be ready to store the "premium" data that clients actually pay for.

Next step: Start manually enriching 50 leads for your first "Lead Magnet" offer!
