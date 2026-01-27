# Zero Budget Bible: The Pearl Data Intelligence Optimization Plan

## 1. Philosophy & Constraints
This document serves as the **SINGLE SOURCE OF TRUTH (The Bible)** for running the Pearl Data Intelligence system under strict constraints:
- **Budget:** $0.00 (No paid proxies, No paid AI tokens).
- **Infrastructure:** Render Free Tier (512 MB RAM, Shared CPU).
- **Goal:** Maximum resilience and data extraction capability without triggering bans or OOM (Out of Memory) kills.

## 2. Core Pillars of Optimization

### A. The "Heuristic Mind" (No-Token  AI)
**Problem:** We cannot rely on paid LLM tokens (Gemini/Groq) for every decision.
**Solution:** `GeminiClient` must seamlessly fall back to rule-based logic.
- **Verification:** Instead of asking AI "Is this a valid lead?", check for: `name` AND (`title` OR `email`) AND length > 5.
- **Intent Scoring:** Score based on keyword density in snippets (e.g., "hiring", "looking for", "growth") rather than semantic understanding.
- **Outreach:** Use high-quality Spintax templates instead of LLM generation.

### B. The "Iron Wall" (Browser Isolation)
**Problem:** Browser contexts "bleed" state. A Google block (redirect to captcha) can crash the subsequent Bing search if the page isn't reset.
**Solution:**
- **hard_reset()**: Before *every* search engine switch, force `await page.goto("about:blank")` and wait 2 seconds.
- **Context Rotation:** Re-create the `BrowserContext` every 5-10 missions to clear cookies/local storage completely.

### C. The "Lean Machine" (512MB RAM Survival)
**Problem:** A single Headless Chrome tab can consume 300MB+. Two tabs = Crash.
**Solution:**
- **Single-Threaded Dominance:** Enforce `MAX_CONCURRENT_MISSIONS = 1`. Do not attempt parallel browsing.
- **aggressive_gc**: Call `gc.collect()` after *every* mission.
- **No Screenshots:** Disable `page.screenshot` by default in Free Mode (saves ~50MB buffers).
- **Minimal DOM:** Block images and fonts at the network layer (`route.abort()`) to save bandwidth and RAM.

### D. The "Patience Protocol" (Stealth via Slowness)
**Problem:** Datacenter IPs (Render) are flagged easily.
**Solution:**
- **Human Delays:** Increase delays between actions by 200% (e.g., 3-7 seconds between searches).
- **Exponential Backoff:** If blocked, wait 5 mins, then 10, then 20. Do not hammer the server.

### E. The "Total Recall" Protocol (Multi-Source Aggregation)
**Problem:** Relying on just one engine leaves data "vacuums". Bing/DDG often index profiles Google misses.
**Solution:**
- **Sequential Aggregation:** Run `Google -> Bing -> DDG` for *every* mission.
- **Deduplication:** Merge results by URL/Name to avoid duplicate rows.
- **Resource Note:** This triples execution time but maximizes coverage. We accept this trade-off for "No Vacuum" results.
- **Additional Sources:** Yahoo (via DDG/Bing mix) is sufficient. For "Zero Budget", avoiding niche paid indexes is key.

## 3. Implementation Checklist

### Phase 1: AI Decoupling (The Brain)
- [ ] **[MODIFY] `worker/utils/gemini_client.py`**:
    - [ ] Add `FreeMode` flag (auto-detect if keys missing).
    - [ ] Implement `heuristic_verify()`: Regex-based validation.
    - [ ] Implement `heuristic_intent()`: Keyword-based scoring.
    - [ ] Ensure `generate_outreach` returns a template if AI fails.

### Phase 2: Scraper Hardening (The Eyes)
- [ ] **[MODIFY] `worker/scrapers/linkedin_engine.py`** & **`base_dork_engine.py`**:
    - [ ] **Logic Change:** Remove `if results: return results` early exits.
    - [ ] **Logic Change:** Append results from *all* engines (Google + Bing + DDG).
    - [ ] Insert `await page.goto("about:blank")` in `_search_google`, `_search_bing`, `_search_ddg` catch blocks.
    - [ ] Add explicit `try/except` around `page.goto` to catch "Navigation Interrupted" specifically.

### Phase 3: Resource Starvation (The Body)
- [ ] **[MODIFY] `worker/hydra_controller.py`**:
    - [ ] Enforce `SEMAPHORE = asyncio.Semaphore(1)` for browser tasks.
    - [ ] Add `gc.collect()` in `finally` block of `process_job`.
    - [ ] Implement `Network Blocking`:
      ```python
      await page.route("**/*.{png,jpg,jpeg,gif,webp,font,woff,woff2}", lambda route: route.abort())
      ```

### Phase 4: Verification
- [ ] Run `test_free_tier.py` (to be created) simulating 0-token environment.
- [ ] Verify memory usage stays < 400MB during a live mission.

## 4. Maintenance
- **Weekly:** Check if Google/LinkedIn DOM selectors have changed (Free Tier depends heavily on CSS selectors).
- **Logs:** Monitor for "Exit Code 137" (OOM Kill) - if seen, increase delay or restart worker.
