# Manual Enrichment Guide - Keeping Clients with Free Data

## 🎯 What You Have (Automated - Free)

From your zero-cost platform:
- ✅ **Company name** (Google Maps)
- ✅ **Phone number** (Google Maps - 40-60% coverage)
- ✅ **Address** (Google Maps)
- ✅ **Website** (discovered via search)
- ✅ **Rating & review count** (Google Maps)
- ✅ **Basic reputation signals** (BBB mentions, Glassdoor)

**This is good foundation data, but NOT enough to keep clients.**

---

## 💰 What Clients ACTUALLY Pay For (Must-Have)

### 1. **Verified Email Addresses** 👑 #1 Priority
**Why clients need it:** Can't do cold email outreach without it  
**Current coverage:** ~5-10% (from website HTML scraping)  
**Target coverage:** 40-60% minimum to be competitive

**Free Methods:**
```
Method 1: Email Pattern Guessing (10 min per 50 leads)
- Find decision maker name on LinkedIn
- Generate patterns: firstname.lastname@domain.com
- Verify with NeverBounce free tier (1000/month)
- Success rate: 30-40%

Method 2: Contact Page Extraction (5 min per website)
- Visit company website /contact page
- Look for "sales@", "info@", "contact@"
- These are valid but not decision-maker emails
- Success rate: 60-70%

Method 3: LinkedIn Profile Email (when visible)
- Some LinkedIn profiles show contact info
- Free LinkedIn allows 3-5 profile views per search
- Success rate: 5-10%

Tools:
- Hunter.io free tier: 25 searches/month
- RocketReach free tier: 5 lookups/month
- Apollo.io free tier: 60 emails/month
```

**Database Schema:**
```sql
ALTER TABLE leads ADD COLUMN email VARCHAR(255);
ALTER TABLE leads ADD COLUMN email_verification_status VARCHAR(50); -- 'verified', 'guessed', 'bounced'
ALTER TABLE leads ADD COLUMN email_confidence VARCHAR(20); -- 'high', 'medium', 'low'
ALTER TABLE leads ADD COLUMN email_source VARCHAR(100); -- 'hunter', 'website', 'pattern'
```

---

### 2. **Decision Maker Name + Title** 🎯 #2 Priority
**Why clients need it:** Personalization = 3x higher open rates  
**Current coverage:** ~0% (LinkedIn blocked)  
**Target coverage:** 30-50%

**Free Methods:**
```
Method 1: LinkedIn Manual Search (5-10 min per company)
- Free LinkedIn: Search "[Company Name] Founder"
- Look for CEO, Founder, VP Marketing, Head of Sales
- Copy name + title manually
- Success rate: 40-60% for small businesses

Method 2: Company Website "Team" Page
- Visit company website /about or /team
- Look for leadership section
- Usually shows Founder/CEO with photo
- Success rate: 30-40%

Method 3: Google Search "[Company] CEO"
- Often shows answer box with CEO name
- Check company press releases, news
- Success rate: 20-30%
```

**Database Schema:**
```sql
ALTER TABLE leads ADD COLUMN decision_maker_name VARCHAR(255);
ALTER TABLE leads ADD COLUMN decision_maker_title VARCHAR(255);
ALTER TABLE leads ADD COLUMN decision_maker_linkedin_url VARCHAR(500);
ALTER TABLE leads ADD COLUMN decision_maker_email VARCHAR(255);
```

---

### 3. **Company Size (Employees)** 📊 #3 Priority  
**Why clients need it:** Filter out too-small or too-large companies  
**Current coverage:** 0%  
**Target coverage:** 70-80% (easy to estimate)

**Free Methods:**
```
Method 1: LinkedIn Company Page
- Search "linkedin.com/company/[company-name]"
- Shows employee count (e.g., "11-50 employees")
- Success rate: 80-90%

Method 2: Estimate from Website
- 1-3 team members on /team page = 1-10 employees
- Office photos show 5+ desks = 10-50 employees  
- Multiple locations listed = 50+ employees
- Success rate: 60-70%

Method 3: Google "[Company Name] employees"
- Sometimes shows answer box
- Check Crunchbase snippet (no login needed)
- Success rate: 30-40%
```

**Database Schema:**
```sql
ALTER TABLE leads ADD COLUMN employee_count VARCHAR(50); -- '1-10', '11-50', '51-200', '201-500', '500+'
ALTER TABLE leads ADD COLUMN employee_count_source VARCHAR(50); -- 'linkedin', 'estimate', 'website'
```

---

### 4. **Industry/Category** 🏷️ #4 Priority
**Why clients need it:** Targeting and segmentation  
**Current coverage:** ~60% (from Google Maps category)  
**Target coverage:** 90%+

**Free Methods:**
```
Method 1: Already Have It!
- Google Maps provides category (e.g., "Marketing Agency")
- Just need to normalize/standardize
- Success rate: 60-70%

Method 2: Website Meta Description
- Read <meta name="description"> tag
- Usually contains industry keywords
- Success rate: 80-90%

Method 3: Classify from Company Name
- "XYZ Marketing" → Marketing Agency
- "ABC Law Firm" → Legal Services
- Success rate: 50-60%
```

**Database Schema:**
```sql
ALTER TABLE leads ADD COLUMN industry VARCHAR(100); -- standardized
ALTER TABLE leads ADD COLUMN category_raw VARCHAR(255); -- from Google Maps
ALTER TABLE leads ADD COLUMN industry_confidence VARCHAR(20); -- 'high', 'medium', 'low'
```

---

### 5. **Social Media Links** 📱 #5 Priority
**Why clients need it:** Multi-channel outreach, brand research  
**Current coverage:** ~30%  
**Target coverage:** 60-70%

**Free Methods:**
```
Method 1: Website Footer
- Visit company website
- Scroll to footer
- Copy LinkedIn, Facebook, Twitter, Instagram links
- Success rate: 70-80%

Method 2: Search "[Company Name] LinkedIn"
- Usually first result is company page
- Same for Facebook, Twitter
- Success rate: 60-70%
```

**Database Schema:**
```sql
-- You already have this in socials JSON column
-- Just need to populate it manually
```

---

## 📋 Complete Database Schema (Add These Columns)

```sql
-- Email fields (highest priority)
ALTER TABLE leads ADD COLUMN email VARCHAR(255);
ALTER TABLE leads ADD COLUMN email_verification_status VARCHAR(50);
ALTER TABLE leads ADD COLUMN email_confidence VARCHAR(20);
ALTER TABLE leads ADD COLUMN email_source VARCHAR(100);

-- Decision maker fields
ALTER TABLE leads ADD COLUMN decision_maker_name VARCHAR(255);
ALTER TABLE leads ADD COLUMN decision_maker_title VARCHAR(255);
ALTER TABLE leads ADD COLUMN decision_maker_linkedin_url VARCHAR(500);
ALTER TABLE leads ADD COLUMN decision_maker_email VARCHAR(255);

-- Company size
ALTER TABLE leads ADD COLUMN employee_count VARCHAR(50);
ALTER TABLE leads ADD COLUMN employee_count_source VARCHAR(50);

-- Industry
ALTER TABLE leads ADD COLUMN industry VARCHAR(100);
ALTER TABLE leads ADD COLUMN category_raw VARCHAR(255);
ALTER TABLE leads ADD COLUMN industry_confidence VARCHAR(20);

-- Quality scoring
ALTER TABLE leads ADD COLUMN data_quality_score INT; -- 0-100
ALTER TABLE leads ADD COLUMN last_manual_enrichment_date TIMESTAMP;
ALTER TABLE leads ADD COLUMN manual_enrichment_by VARCHAR(100); -- user who enriched

-- Client-facing fields
ALTER TABLE leads ADD COLUMN company_description TEXT;
ALTER TABLE leads ADD COLUMN revenue_estimate VARCHAR(50); -- '$1M-$5M', '$5M-$10M', etc
ALTER TABLE leads ADD COLUMN technologies_used TEXT; -- 'WordPress, Shopify, Stripe'
```

---

## ⏱️ Manual Enrichment Workflow (Realistic Time)

**For 50 leads (1 batch):**

| Task | Time | Method | Coverage |
|------|------|--------|----------|
| Find emails (patterns) | 30 min | Hunter.io free + patterns | 40% |
| Find decision makers | 45 min | LinkedIn manual + website | 50% |
| Estimate company size | 15 min | LinkedIn company pages | 80% |
| Copy social links | 20 min | Website footer | 70% |
| Add industry tags | 10 min | Standardize from Maps | 90% |
| **TOTAL** | **2 hours** | | **Average 60%** |

**Productivity:**
- 50 leads in 2 hours = 25 leads/hour
- Pay a VA $5-10/hour → **$0.20-0.40 per enriched lead**
- Sell to clients for **$0.50-1.00 per lead** = 100% profit margin

---

## 💡 What to Charge Clients

**Pricing Models:**

### Option 1: Pay Per Lead
- **Basic** (name, phone, website): $0.20/lead
- **Standard** (+ email, decision maker): $0.50/lead  
- **Premium** (+ verified email, social links): $1.00/lead

### Option 2: Monthly Subscription
- **Starter**: 500 leads/month = $199/month
- **Growth**: 2000 leads/month = $499/month
- **Scale**: 10,000 leads/month = $1,499/month

### Option 3: One-Time List
- 1000 leads = $300
- 5000 leads = $1,200
- 10,000 leads = $2,000

**Your costs:**
- Platform: $0/month (free tier)
- Manual enrichment: $0.20-0.40/lead (VA time)
- **Profit margin: 50-80%**

---

## 🎓 Training Your VA Team

**Hire 2-3 VAs on Upwork/Fiverr ($3-5/hour):**

**Week 1 Training:**
1. Show them how to find emails (Hunter.io, website contact pages)
2. Show them LinkedIn search for decision makers
3. Give them spreadsheet template with clear instructions
4. Start with 10 leads/day, ramp to 50/day

**Quality Control:**
- Randomly verify 10% of emails with NeverBounce
- Check decision maker names against LinkedIn yourself
- Fire VAs with <80% accuracy

**Tools to Give VAs:**
- Google Sheet with lead data
- Hunter.io free account (25/month each)
- LinkedIn free accounts
- NeverBounce free tier (for verification)

---

## 🚀 Client Retention Strategy

**What makes clients stay:**

1. **Email deliverability** (most important)
   - 90%+ valid emails = happy clients
   - Use NeverBounce to verify before delivery
   - Offer "replacement guarantee" for bounced emails

2. **Decision maker accuracy**
   - Verify titles are current (not outdated)
   - Include LinkedIn URL so client can verify
   - Offer to update if incorrect

3. **Fresh data**
   - Re-scrape lists every 90 days
   - Update emails/decision makers monthly
   - Charge small "refresh fee" ($0.10/lead)

4. **Easy export**
   - CSV download
   - HubSpot/Salesforce integration
   - API access for enterprise clients

5. **Support**
   - Reply to questions within 24h
   - Offer custom lists (specific geo/industry)
   - Provide targeting advice

---

## ✅ Complete Lead Record (What Clients Expect)

```json
{
  "company_name": "Acme Marketing Agency",
  "phone": "+1-617-555-1234",
  "website": "https://acmemarketing.com",
  "address": "123 Main St, Boston, MA 02110",
  "rating": "4.8",
  "review_count": 42,
  
  "email": "hello@acmemarketing.com",
  "email_verification": "verified",
  "email_confidence": "high",
  
  "decision_maker_name": "Sarah Johnson",
  "decision_maker_title": "Founder & CEO",
  "decision_maker_linkedin": "linkedin.com/in/sarahjohnson",
  "decision_maker_email": "sarah@acmemarketing.com",
  
  "employee_count": "11-50",
  "industry": "Marketing & Advertising",
  
  "linkedin_url": "linkedin.com/company/acme-marketing",
  "facebook_url": "facebook.com/acmemarketing",
  "twitter_url": "twitter.com/acmemarketing",
  
  "company_description": "Full-service digital marketing agency specializing in SEO and content marketing",
  
  "data_quality_score": 85,
  "last_enriched": "2026-01-28"
}
```

**This record has everything a client needs to start outreach.**

---

## 🎯 Summary: What You MUST Add Manually

**Top 3 (Non-Negotiable):**
1. ✅ **Verified emails** (40-60% coverage via free tools + VAs)
2. ✅ **Decision maker name/title** (30-50% coverage via LinkedIn)
3. ✅ **Company size estimate** (70-80% coverage via LinkedIn)

**Nice to Have:**
4. Social media links (60-70% from website footers)
5. Industry tags (90%+ from Google Maps + normalization)
6. Brief company description (from website/LinkedIn)

**With these 6 fields added manually, you can charge $0.50-1.00 per lead and keep clients long-term.**

The key is: **Your platform finds the companies (free), VAs add the contact info (cheap), you sell clean lists (profitable).**
