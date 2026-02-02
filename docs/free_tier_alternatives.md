# ⚡ Clarity Pearl: Free & Low-Cost API Alternatives

To achieve **10,000 leads/day** without breaking the bank, we will employ a **"Hydra Protocol"**: cycling through multiple free-tier APIS and falling back to open-source scrapers when necessary.

## 🔍 Google Search (SERP) APIs
*Replace slow browser scraping with instant API results.*

| Provider | Free Tier | Speed | Best For |
| :--- | :--- | :--- | :--- |
| **Serper.dev** | **2,500 queries** (No CC) | ⚡ <1s | **Primary Engine.** Fastest, Google-focused. |
| **SerpApi** | **250 queries/mo** | ⚡ <1s | **Reliable.** Gold standard for stability. |
| **ScraperAPI** | **5,000 credits** (7-day trial) + 1,000/mo | ⚡ 1-2s | **Backup.** Handles proxy rotation automatically. |
| **Apify** | **$5/mo credit** (~1,400 results) | 🚀 Variable | **Complex Tasks.** Excellent for Google Maps specifically. |
| **SearchAPI.io** | **100 searches** (Free) | ⚡ <1s | High-quality fallback. |
| **HasData** | **100 credits** | ⚡ <2s | AI-ready JSON output. |
| **DataForSEO** | **$1 Credit** (~1,000 queries) | ⚙️ Deep | Developing custom SEO tools. |
| **ScrapingDog** | **1,000 requests** | ⚡ 2s | Simple API for general scraping. |
| **Oxylabs** | **5,000 queries** (Trial) | 🛡️ Elite | Enterprise-grade residential proxies. |
| **ValueSERP** | **100 credits** | ⚡ Fast | Low-cost paid scaling. |

---

## 📍 Business Data & Maps (The Directory Layer)
*Get clean business details (Phone, Website, Address) without parsing HTML.*

| Provider | Free Tier | Value |
| :--- | :--- | :--- |
| **TomTom API** | **2,500 req/day** | **Excellent** maps/poi alternative to Google Maps. |
| **Mapbox** | **100,000 req/mo** | Great for geocoding and local search. |
| **Radar.com** | **100,000 req/mo** | Geocoding & Place Search. |
| **RapidAPI (Google Maps)** | Varies (Freemium) | Aggregators often offer cheaper tiers than official Google. |

---

## 💎 Lead Enrichment APIs (The "Clarity" Layer)
*Turn a domain/name into a contact (Email, Phone).*

| Provider | Free Tier | Best For |
| :--- | :--- | :--- |
| **Apollo.io** | Limited Basic | Enriched B2B database access. |
| **Kaspr** | 25 Credits | LinkedIn phone numbers. |
| **Hunter.io** | 25 Searches | verified CEO emails. |
| **PeopleDataLabs** | 100 Records | Deep person profiles. |
| **Clearbit (HubSpot)** | **Free** (Name-to-Domain) | Turning company names into domains. |
| **Proxycurl** | Trial usage | LinkedIn profile data via API. |

---

## 🛠️ Open Source / "Zero Cost" Options (Github)
*Free software, but requires your own proxies.*

1.  **`petey1337/google-review-scraper`**:
    *   **Focus:** Google Maps Reviews & Details.
    *   **Tech:** Puppeteer (Headless Chrome).
    *   **Cost:** $0 (Computing only).

2.  **`gosom/google-maps-scraper`**:
    *   **Focus:** High-scale Google Maps business data.
    *   **Tech:** Go (Golang) - Extremely fast.
    *   **Cost:** $0.

3.  **`searxng` instance**:
    *   **Focus:** Meta-search engine.
    *   **Strategy:** Host your own private search engine to query Google/Bing anonymously.

---

## 🚀 Recommendation: The "Hydra" Stack
To get 10,000/day:

1.  **Layer 1 (Speed):** Use **Serper.dev** for the first 2,500 queries/day.
2.  **Layer 2 (Reliability):** Use **SerpApi** (250 req) for critical or high-value lookups.
3.  **Layer 3 (Volume):** Switch to **ScraperAPI** (1,000 req) overlapping with **Apify** ($5 credit).
4.  **Layer 4 (Zero-Cost):** Deploy `google-maps-scraper` (Go version) efficiently on local hardware for bulk directory data.
