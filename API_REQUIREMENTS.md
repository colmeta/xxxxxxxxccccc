# 🔌 CLARITY PEARL API REQUIREMENTS

To run the "Zero Vacuum" engines at full power, you need the following keys. 
**Most are FREE.**

## 🚨 MANDATORY (The Engine Won't Start Without These)

| Service | Purpose | Cost | Where to Get | Envar Name |
|---------|---------|------|--------------|------------|
| **OpenAI / Groq** | The "Brain" (Parsing vague results) | Usage | [OpenAI](https://platform.openai.com) | `OPENAI_API_KEY` |
| **Supabase** | The "Memory" (Database) | Free | [Supabase](https://supabase.com) | `SUPABASE_URL` / `SUPABASE_KEY` |
| **US Census** | Layer 8 Trade Data (USA Trade Online) | **FREE** | [Census.gov](https://api.census.gov/data/key_signup.html) | `CENSUS_API_KEY` |
| **Playwright** | The "Eyes" (Scraping) | **FREE** | Installed w/ app | N/A (Internal) |

---

## ⚠️ HIGHLY RECOMMENDED (Massive Quality Boost)

| Service | Purpose | Cost | Why You Want It | Envar Name |
|---------|---------|------|-----------------|------------|
| **SAM.gov** | Layer 11 Gov Contracts | **FREE** | Cleaner data than scraping | `SAM_API_KEY` |
| **Eventbrite** | Layer 9 Events | **FREE** | Hourly sync of new events | `EVENTBRITE_API_KEY` |
| **USPTO** | Layer 6 Patents | **FREE** | Faster patent lookups | `USPTO_API_KEY` |
| **Hunter.io** | Email Discovery | Free Tier | Finding CEO emails | `HUNTER_API_KEY` |
| **Bright Data / IPRoyal** | Residential Proxies | $10/mo | **Prevents Blocking** | `PROXY_URL` |

---

## 💎 OPTIONAL (The "God Mode" Paid Upgrades)

*Only get these if you have a paying enterprise client covering the cost.*

| Service | Layer | Cost | Value Add |
|---------|-------|------|-----------|
| **ImportGenius** | Trade (L8) | $299/mo | Individual Shipment Records (BOL) |
| **GovWin (Deltek)** | Gov (L11) | $3k/yr | Intelligence *before* bids go public |
| **ZoomInfo** | Contact (L12)| $15k/yr | Direct mobile numbers for Fortune 500 |
| **PitchBook** | Capital (L3) | $2k/mo | Private PE/VC deal flow |
| **Shodan** | Infra (L10) | $59/mo | Deep server vulnerability scanning |
| **BuiltWith** | Tech (L4) | $295/mo | Full historic tech stack changes |

---

## 🛠️ HOW TO CONFIGURE

1. Create a `.env` file in the root directory.
2. Paste the keys in this format:

```env
# --- CORE BRAIN ---
OPENAI_API_KEY=sk-proj-...
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_KEY=eyJ...

# --- ZERO VACUUM ENGINES ---
CENSUS_API_KEY=...       # Get this first (Instant)
SAM_API_KEY=...          # Optional but good
EVENTBRITE_KEY=...       # Optional

# --- PROXIES (Optional but Recommended) ---
PROXY_URL=http://user:pass@host:port
```
