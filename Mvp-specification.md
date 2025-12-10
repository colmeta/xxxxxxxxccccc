# NEXUS DATA INTELLIGENCE - MVP SPECIFICATION

## Product Vision
Build the simplest possible version of our data intelligence platform that allows non-technical users to extract structured data from LinkedIn and Google Maps, proving that AI-powered data collection can be 10x faster than manual methods.

---

## MVP Goals

### Primary Goal:
Validate product-market fit by getting 5 design partners actively using the product and providing feedback.

### Success Criteria:
- 5 active users extracting data weekly
- Average 500+ records extracted per user
- 80%+ would recommend to colleagues
- 3+ feature requests documented
- 2+ users willing to pay (LOIs)

---

## MVP Scope (What's IN)

### 1. USER MANAGEMENT
**Features:**
- Email/password registration
- Email verification
- Login/logout
- Password reset
- Basic user profile (name, company, role)

**Tech:**
- Supabase Auth
- PostgreSQL for user data
- JWT tokens

---

### 2. DATA SOURCES (2 Initial Sources)

#### Source 1: LinkedIn (Profile Scraper)
**What It Extracts:**
- Full name
- Current job title
- Current company
- Location (city, country)
- Profile URL
- Connection count (if visible)
- Profile headline
- About section (first 200 chars)

**Inputs Required:**
- LinkedIn profile URLs (up to 100 per job)
- OR Search query (e.g., "Marketing Manager in San Francisco")

**Rate Limits:**
- 100 profiles per hour
- 1,000 profiles per day
- 10,000 profiles per month (free tier)

#### Source 2: Google Maps (Business Scraper)
**What It Extracts:**
- Business name
- Full address
- Phone number
- Website URL
- Business category
- Average rating
- Number of reviews
- Hours of operation
- Price level ($ to $$$$)
- Google Maps URL

**Inputs Required:**
- Search query (e.g., "coffee shops in Seattle")
- OR List of business URLs

**Rate Limits:**
- 200 businesses per hour
- 2,000 businesses per day
- 20,000 businesses per month (free tier)

---

### 3. JOB MANAGEMENT

#### Create Scraping Job
**UI Flow:**
1. User clicks "Create New Job"
2. Selects data source (LinkedIn or Google Maps)
3. Chooses input method:
   - Upload CSV of URLs
   - Paste URLs (one per line)
   - Enter search query
4. Previews what data will be extracted
5. Clicks "Start Scraping"

**API Endpoint:**
```
POST /api/jobs
{
  "source": "linkedin" | "google_maps",
  "input_type": "urls" | "search",
  "input_data": ["url1", "url2"] | "search query",
  "name": "My Job Name" (optional)
}
```

#### Job Status
**States:**
- `queued` - Waiting to start
- `running` - Currently scraping
- `completed` - Finished successfully
- `failed` - Encountered error
- `partial` - Some records failed

**Real-Time Updates:**
- WebSocket connection shows progress
- Progress bar (0-100%)
- Records extracted count
- Estimated time remaining

#### Job History
**View Past Jobs:**
- List of all jobs (most recent first)
- Filter by status, date, source
- Quick actions: View, Download, Delete

---

### 4. DATA VIEWING & EXPORT

#### Data Preview
**In-App Table View:**
- Paginated table (50 records per page)
- Sortable columns
- Search/filter functionality
- Column visibility toggle
- Responsive design (mobile-friendly)

#### Export Options
**Formats Supported:**
- CSV (comma-separated)
- JSON (structured data)
- Excel (XLSX)

**Export UI:**
- One-click download from job page
- Bulk export (multiple jobs)
- API endpoint for programmatic access

**API Endpoint:**
```
GET /api/jobs/{job_id}/export?format=csv|json|xlsx
```

---

### 5. USAGE LIMITS (Freemium Model)

#### Free Tier
- 1,000 records per month total
- 2 concurrent jobs
- 7-day data retention
- Email support (48-hour response)

#### Usage Tracking
- Dashboard shows:
  - Records used this month
  - Records remaining
  - Reset date
  - Upgrade CTA when approaching limit

#### Over-Limit Behavior
- Soft limit: Warning at 80% usage
- Hard limit: Jobs blocked at 100%
- Upgrade prompt with one-click checkout

---

### 6. CORE INFRASTRUCTURE

#### Technical Architecture

**Backend:**
```
FastAPI (Python 3.11)
├── /auth - Authentication endpoints
├── /jobs - Job management
├── /scrapers - Scraping logic
├── /export - Data export
└── /webhooks - Real-time updates
```

**Database Schema:**
```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  company VARCHAR(255),
  role VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Jobs table
CREATE TABLE jobs (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  source VARCHAR(50) NOT NULL, -- 'linkedin' or 'google_maps'
  status VARCHAR(50) NOT NULL, -- 'queued', 'running', 'completed', 'failed'
  input_type VARCHAR(50), -- 'urls' or 'search'
  input_data JSONB,
  name VARCHAR(255),
  total_records INTEGER DEFAULT 0,
  completed_records INTEGER DEFAULT 0,
  failed_records INTEGER DEFAULT 0,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Results table
CREATE TABLE results (
  id UUID PRIMARY KEY,
  job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
  data JSONB NOT NULL, -- Extracted data
  source_url VARCHAR(1000),
  extracted_at TIMESTAMP DEFAULT NOW()
);

-- Usage tracking table
CREATE TABLE usage (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  month VARCHAR(7), -- 'YYYY-MM'
  records_used INTEGER DEFAULT 0,
  jobs_created INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, month)
);
```

**Scraping Architecture:**
```
Job Queue (RabbitMQ)
├── Worker 1 (LinkedIn scraper)
├── Worker 2 (Google Maps scraper)
└── Worker 3 (Backup worker)

Each worker:
- Pulls job from queue
- Uses Playwright for browser automation
- Rotates proxies for each request
- Handles CAPTCHAs automatically
- Saves results to database
- Updates job status via WebSocket
```

**Infrastructure:**
- AWS EC2 (t3.medium) - Application server
- AWS RDS (PostgreSQL db.t3.micro) - Database
- AWS S3 - Export file storage
- ElastiCache (Redis) - Caching & sessions
- CloudFront - CDN for static assets

---

## MVP UI/UX Wireframes

### 1. Login/Register Page
```
┌─────────────────────────────────────┐
│  [Logo] Nexus Data Intelligence     │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Email: [            ]      │   │
│  │  Password: [         ]      │   │
│  │  [Login]   [Forgot?]        │   │
│  │  ────────── or ──────────   │   │
│  │  Don't have account? [Sign Up] │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### 2. Dashboard (Home)
```
┌────────────────────────────────────────────────┐
│ [Logo] Dashboard  Jobs  Docs  Settings  [User]│
├────────────────────────────────────────────────┤
│                                                │
│  Usage This Month: 342 / 1,000 records        │
│  [━━━━━━━━━━░░░░░░░░░░] 34%                 │
│  Resets in 18 days      [Upgrade to Pro →]   │
│                                                │
│  [+ New Scraping Job]                         │
│                                                │
│  Recent Jobs                                   │
│  ┌──────────────────────────────────────────┐│
│  │ LinkedIn SF Marketers    ✓ 247 records  ││
│  │ 2 hours ago              [View] [Export]││
│  ├──────────────────────────────────────────┤│
│  │ Coffee Shops Seattle     ✓ 89 records   ││
│  │ 1 day ago                [View] [Export]││
│  └──────────────────────────────────────────┘│
└────────────────────────────────────────────────┘
```

### 3. Create Job Page
```
┌────────────────────────────────────────────────┐
│ Create New Scraping Job                        │
├────────────────────────────────────────────────┤
│                                                │
│  Step 1: Choose Data Source                   │
│  ┌──────────────┐  ┌──────────────┐          │
│  │ 👤 LinkedIn  │  │ 📍 Google    │          │
│  │    Profiles  │  │    Maps      │          │
│  └──────────────┘  └──────────────┘          │
│                                                │
│  Step 2: Provide Input                        │
│  ○ Upload CSV file                            │
│  ● Paste URLs (one per line)                 │
│  ○ Enter search query                         │
│                                                │
│  ┌────────────────────────────────────────┐  │
│  │ https://linkedin.com/in/john-smith     │  │
│  │ https://linkedin.com/in/jane-doe       │  │
│  │                                        │  │
│  └────────────────────────────────────────┘  │
│                                                │
│  Step 3: Preview (Optional)                   │
│  This will extract: Name, Title, Company,     │
│  Location, Profile URL                        │
│                                                │
│  [Cancel]              [Start Scraping →]     │
└────────────────────────────────────────────────┘
```

### 4. Job Running Page
```
┌────────────────────────────────────────────────┐
│ Job: LinkedIn SF Marketers          [Running] │
├────────────────────────────────────────────────┤
│                                                │
│  Progress: 47 / 100 profiles                  │
│  [━━━━━━━━━━━━░░░░░░░░░░░] 47%             │
│  Estimated time: 8 minutes                    │
│                                                │
│  Recent Extractions:                          │
│  ✓ John Smith - Marketing Director @ Acme    │
│  ✓ Jane Doe - CMO @ TechCorp                 │
│  ✓ Bob Johnson - VP Marketing @ StartupCo    │
│  ... (live updating)                          │
│                                                │
│  [Pause Job]  [Cancel Job]                    │
└────────────────────────────────────────────────┘
```

### 5. Job Results Page
```
┌────────────────────────────────────────────────┐
│ Job: LinkedIn SF Marketers       ✓ Completed  │
│ 247 records extracted | 2 hours ago           │
├────────────────────────────────────────────────┤
│                                                │
│  [Export ▼]  [Delete Job]                     │
│  └─ CSV                                        │
│  └─ JSON                                       │
│  └─ Excel                                      │
│                                                │
│  [Search results...]                          │
│                                                │
│  Name         | Title          | Company      │
│  ──────────────────────────────────────────── │
│  John Smith   | Marketing Dir  | Acme Inc     │
│  Jane Doe     | CMO            | TechCorp     │
│  Bob Johnson  | VP Marketing   | StartupCo    │
│  ... (50 per page)                            │
│                                                │
│  [← Prev]  Page 1 of 5  [Next →]             │
└────────────────────────────────────────────────┘
```

---

## MVP Technical Requirements

### Performance Requirements
- API response time: <500ms (95th percentile)
- Scraping speed: 30-50 records per minute
- System uptime: 99% (acceptable for MVP)
- Page load time: <2 seconds

### Security Requirements
- HTTPS everywhere (SSL/TLS)
- Password hashing (bcrypt, 12 rounds)
- JWT expiration (7 days)
- Rate limiting (100 req/min per IP)
- Input sanitization (SQL injection prevention)
- XSS protection
- CSRF tokens

### Scalability Requirements
- Support 100 concurrent users
- Handle 10,000 scraping jobs per day
- Store up to 1M records
- Auto-scale workers based on queue size

---

## MVP Development Checklist

### Week 1: Foundation ✓
- [ ] AWS infrastructure setup
- [ ] PostgreSQL database
- [ ] Authentication system
- [ ] Basic API endpoints

### Week 2-3: Scrapers ✓
- [ ] LinkedIn scraper
- [ ] Google Maps scraper
- [ ] Job queue system
- [ ] Data validation

### Week 4: UI ✓
- [ ] Login/register pages
- [ ] Dashboard
- [ ] Create job flow
- [ ] Results viewer

### Week 5: Polish ✓
- [ ] Export functionality
- [ ] Usage tracking
- [ ] Error handling
- [ ] Loading states

### Week 6: Testing ✓
- [ ] Unit tests (80% coverage)
- [ ] Integration tests
- [ ] User acceptance testing
- [ ] Bug fixes

---

## What's NOT in MVP (Future Features)

### Deferred to v2.0:
- Additional data sources (Twitter, Instagram, etc.)
- Advanced scheduling (cron jobs)
- Team collaboration features
- API access for developers
- Webhooks for job completion
- Data enrichment (email finding, etc.)
- Custom scraper builder
- White-label options
- Advanced analytics dashboard
- Mobile apps (iOS, Android)

### Why Defer?
Focus on proving core value proposition first. These features add complexity without validating fundamental assumptions.

---

## MVP Success Metrics (After 30 Days)

### Product Metrics:
- [ ] 50+ registered users
- [ ] 20+ active users (used in last 7 days)
- [ ] 100+ jobs created
- [ ] 50,000+ records extracted
- [ ] 80%+ scraping success rate

### Business Metrics:
- [ ] 5 design partners giving feedback
- [ ] 3+ feature requests documented
- [ ] 2+ users willing to pay (LOIs)
- [ ] Net Promoter Score (NPS) >30

### Technical Metrics:
- [ ] 99%+ uptime
- [ ] <500ms API response time
- [ ] <5% error rate on scraping jobs
- [ ] Zero critical security issues

---

## MVP User Stories

### As a Sales Rep:
- I want to extract LinkedIn profiles of potential leads
- So that I can quickly build a targeted outreach list
- And save 10+ hours per week on manual research

### As a Marketing Manager:
- I want to scrape competitor reviews from Google Maps
- So that I can understand what customers value
- And improve our product positioning

### As a Small Business Owner:
- I want to find all restaurants in my area
- So that I can offer them my catering service
- And grow my customer base quickly

---

## MVP Risks & Mitigation

### Risk 1: Scrapers Break Frequently
**Mitigation:**
- Use Playwright (more stable than Selenium)
- Implement retry logic (3 attempts)
- Monitor success rates daily
- Have backup extraction methods

### Risk 2: Users Don't Understand How to Use It
**Mitigation:**
- Simple 3-step wizard
- Video tutorials on every page
- Tooltips for all features
- Live chat support (Intercom)

### Risk 3: Legal Concerns About Scraping
**Mitigation:**
- Only scrape public data
- Respect robots.txt
- Rate limit aggressively
- Clear Terms of Service
- Consult lawyer before launch

### Risk 4: Poor Data Quality
**Mitigation:**
- Validate all extracted data
- Show confidence scores
- Allow users to report issues
- Manual QA on 10% of jobs

---

## MVP Launch Checklist

### Pre-Launch:
- [ ] All features tested and working
- [ ] Documentation complete
- [ ] Video tutorials recorded
- [ ] Terms of Service and Privacy Policy
- [ ] Support system set up (Intercom)
- [ ] Analytics configured (Mixpanel)
- [ ] Landing page optimized
- [ ] Email sequences ready

### Launch Day:
- [ ] Product Hunt submission
- [ ] Social media posts
- [ ] Email to waitlist
- [ ] Monitor for bugs
- [ ] Respond to all feedback

### Post-Launch:
- [ ] Daily check-ins with users
- [ ] Weekly feature prioritization
- [ ] Monthly metrics review
- [ ] Continuous iteration

---

**Last Updated:** December 2025  
**Version:** 1.0  
**Next Review:** End of Month 1
