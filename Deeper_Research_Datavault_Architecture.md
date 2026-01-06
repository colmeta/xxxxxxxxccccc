# 🏗️ DEEPER RESEARCH: DATAVAULT ARCHITECTURE
**Classification:** TECHNICAL BLUEPRINT | PROJECT NEXUS
**Status:** REFERENCE SPECIFICATION

---

> [!TIP]
> This architecture is designed for "Zero-Budget Dominance." It leverages local compute for heavy lifting and cloud for orchestration, ensuring we can outscale competitors with minimal burn.

## 1. System Overview
DATAVAULT is a **Verification-First Data Pipeline**. Unlike traditional scrapers that dump raw HTML into a DB, DATAVAULT flows all data through an "Arbiter" layer that cryptographically signs it as "Trusted" or "Rejected."

### The "Trident" Core Stacks
We share a common brain (Orchestrator) but use specialized "Heads" for each vertical.

| Vertical | Primary Source | Secondary Source (Verification) | Extraction Tech | Trust Signal |
| :--- | :--- | :--- | :--- | :--- |
| **B2B Sales** | LinkedIn (Public) | Company Website, News API, DNS Records | Playwright (Stealth) | Data Consistency across 3 sources |
| **E-Commerce** | Marketplace Product Pages | Manufacturer Sites, Social Ads | Visual AI (OCR/Vision) | Vision-Text Match Score |
| **Real Estate** | County Clerk Records | Zillow (Comp), Court Filings (Probate) | PDF Parsing / headless | "Motivated Seller" Predictive Model |

---

## 2. Infrastructure Components

### A. The Orchestrator (Brain)
*   **Tech:** Python (FastAPI) + Celery (Task Queue).
*   **Role:** Receives API requests, checks `Redis Cache`, and dispatches jobs to Hydra.
*   **Smart Routing:**
    *   *If User = Enterprise:* Route to "High Speed" pool (Datacenter IPs).
    *   *If Target = LinkedIn:* Route to "Stealth" pool (Residential IPs).

### B. Hydra (The Hands)
A distributed network of scraping nodes.
*   **Level 1 (Light):** `httpx/requests` for APIs and static sites. (Cost: $0.001/req)
*   **Level 2 (Browser):** Playwright/Puppeteer for dynamic JS sites. (Cost: $0.005/req)
*   **Level 3 (AI Vision):** Sending screenshots to Gemini Flash/GPT-4o-mini for complex extraction. (Cost: $0.01/req)

### C. The Arbiter (The Judge)
The core differentiator. It runs *post-scrape*.
*   **Logic:**
    1.  **Ingest:** Raw profile says "John Doe, CEO of Acme".
    2.  **Cross-Check:**
        *   *Query 1:* DNS lookup `acme.com` (Does site exist?).
        *   *Query 2:* Google Search `site:acme.com "John Doe"` (Is he listed?).
    3.  **Score:**
        *   Matches found = +0.9
        *   Site dead = -1.0 (Flag as "Ghost Lead")
    4.  **Sign:** Generate a JWT signature verifying the check date and score.

### D. The Vault (Storage)
*   **Database:** PostgreSQL (Supabase).
*   **Schema:** Single `master_person` table with JSONB `attributes` for flexibility across verticals.
*   **Cold Storage:** S3 bucket for raw HTML/Screenshots (Evidence).

---

## 3. The "Unstoppable" Edge
### 1. Account Rotation Ring
We maintain a pool of 50+ "Viewer Accounts" (LinkedIn, Amazon, etc.) managed by 4G mobile proxies. High reputation, low ban rate.

### 2. Fingerprint Spoofing
Hydra injects fake:
*   GPU Vendors (NVIDIA vs Intel)
*   Screen Resolutions
*   Battery Levels
*   Mouse Movements (Bezier curves, not linear)

### 3. The "Human-in-the-Loop" Fallback
If `TrustScore` is between 0.4 and 0.7 (Ambiguous), the system alerts a Slack channel. A human click-worker (or founder) can verify it with one click, feeding the result back to train the Arbiter model.

---

## 4. Implementation Priorities (Phase 1)
1.  **`backend/hydra/stealth_browser.py`:** Implement the fingerprint spoofing class.
2.  **`backend/arbiter/scorer.py`:** Implement the B2B verification logic (DNS + Search).
3.  **`frontend/dashboard/B2BView.jsx`:** The UI to display "Verified" vs "Raw" states.
