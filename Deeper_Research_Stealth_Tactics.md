# 👻 DEEPER RESEARCH: THE STEALTH LAYER (Bypassing the "Zero Results" Block)
**Classification:** TECHNICAL RECON | PROJECT NEXUS
**Focus:** Solving Google, LinkedIn, and Instagram blocking.

---

> [!WARNING]
> **Why Hydra returns "Zero Results":** Currently, the scraper uses standard Playwright/Chromium. Sites like Google and LinkedIn detect the "AutomationControlled" flag and TLS fingerprint mismatches. They don't block you; they just serve an empty page or a CAPTCHA that the script isn't seeing.

## 1. The 2026 Stealth Stack: "Unmasking the Bot"
To be "Unstoppable," we must stop looking like a script. We will implement these 4 layers:

### Layer 1: TLS / JA3 Fingerprint Spoofing
*   **The Problem:** Anti-bot systems (Cloudflare/Datadome) look at the "TLS Handshake." Python/Playwright have a distinct signature.
*   **The Solution:** Use `curl_cffi` or specialized Playwright patches to mimic **Chrome 120+ JA3 signatures**. This makes the initial connection look like a real browser, before a single pixel is rendered.

### Layer 2: Behavioral Humanization
*   **The Problem:** Scripts move the mouse in straight lines and click at exactly the same speed.
*   **The Solution:** Implement **Bezier Curve mouse movements** and **Gaussian random delays**.
    *   *Linear Move:* From (0,0) to (100,100).
    *   *Human Move:* Slight curves, micro-tremors, and variable speed.

### Layer 3: Canvas & WebGL Noise
*   **The Problem:** Websites can "fingerprint" your graphics card. All Render instances or Headless servers return the exact same hash.
*   **The Solution:** Inject a small amount of "noise" into the Canvas/WebGL rendering. This makes every "Hydra Head" look like a unique device (Macbook vs. Dell vs. iPhone).

---

## 2. Multi-Platform Non-Login Strategy
You mentioned Instagram, Twitter, and Reddit. Here is how we scrape them WITHOUT login (zero risk to accounts):

| Platform | Strategy | 2026 Stealth Requirement |
| :--- | :--- | :--- |
| **Instagram** | **Guest GraphQL** | Must rotate `x-ig-app-id` and use 4G Mobile Proxies. |
| **Twitter (X)** | **Guest Tokens** | Intercept ephemeral query tokens; Mimic mobile app headers. |
| **Reddit** | **JSON Endpoints** | Append `.json` to URLs; Adhere to `robots.txt` rate limits. |
| **Google** | **Search Dorking** | Residential Proxies + JA3 Spoofing to prevent "Verify you're human" blocks. |

---

## 3. The "Zero-Cost" Pivot
Since we can't stop building, we will prioritize **Local Scrapers**. 
*   **Your PC** has a high-reputation IP (Residential/ISP). 
*   **Render** has a low-reputation IP (Datacenter).
*   **Strategy:** Hydra will prioritize your Local PC for the "Engage" phase (scraping) and use Render only for "Command & Control" (API).

---

**STATUS:** STEALTH ARCHITECTURE DEFINED
**NEXT ACTION:** Implement JA3 Spoofing in `worker/utils/stealth.py`.
