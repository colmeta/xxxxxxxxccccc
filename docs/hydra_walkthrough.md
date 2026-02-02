# 🐍 Hydra Protocol: 10,000 Leads/Day Configuration

The **Hydra Protocol** is now installed. It replaces slow browser scraping with a multi-layered API attack strategy to maximize free tier usage.

## 1. Quick Start
To unleash full speed, you need to feed the Hydra. 

### Step 1: Get Keys (Free Tiers)
Get these keys (most take < 60 seconds). You do **NOT** need all of them, but more keys = more speed.

| Service | Free Tier | URL | Priority |
| :--- | :--- | :--- | :--- |
| **Serper.dev** | 2,500 queries | [serper.dev](https://serper.dev) | ⭐️⭐️⭐️⭐️⭐️ (Essential) |
| **SearchAPI** | 100 queries | [searchapi.io](https://www.searchapi.io) | ⭐️⭐️⭐️⭐️ |
| **HasData** | 100 credits | [hasdata.com](https://hasdata.com) | ⭐️⭐️⭐️ |
| **ScrapingDog** | 1,000 requests | [scrapingdog.com](https://scrapingdog.com) | ⭐️⭐️⭐️ |

### Step 2: Configure Environment
1. Open your `.env` file in the project root.
2. Paste the keys you obtained into the `HYDRA PROTOCOL KEYS` section.

```env
SERPER_API_KEY=your_key_here
SEARCHAPI_API_KEY=your_key_here
# ...
```

## 2. Architecture Changes
- **Hydra Client (`hydra_client.py`)**: Automatically rotates between providers. If Serper runs out of credits, it switches to SearchAPI instantly.
- **Improved Base Engine**: The `BaseDorkEngine` now checks APIs first. Browser scraping is only used as a last resort "turtle mode".
- **Open Source Fallback**: If all APIs fail, the system launches a lightweight headless browser (`open_source_maps.py`) to keep getting data, albeit slower.

## 3. Usage
No code changes needed. Just run your normal scraper commands (e.g., via the frontend or `hydra_controller`). The system will auto-detect the keys and accelerate.

> **Verification:** You will see `🐍 Hydra: Engaging Serper.dev...` in your console logs when it's working.
