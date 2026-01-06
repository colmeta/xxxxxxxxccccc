import asyncio
import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv
import hashlib
from utils.arbiter import arbiter
from scrapers.linkedin_engine import LinkedInEngine
from scrapers.google_maps_engine import GoogleMapsEngine
from scrapers.social_radar import TwitterEngine, InstagramEngine
from scrapers.startup_radar import CrunchbaseEngine, ProductHuntEngine, RedditEngine, YCombinatorEngine
from scrapers.tiktok_engine import TikTokEngine
from scrapers.facebook_engine_v2 import FacebookEngineV2
from scrapers.google_maps_grid_engine import GoogleMapsGridEngine
from scrapers.news_pulse_engine import NewsPulseEngine
from scrapers.commerce_watch_engine import CommerceWatchEngine
from scrapers.real_estate_engine import RealEstateEngine
from scrapers.job_scout_engine import JobScoutEngine
from scrapers.reddit_pulse_engine import RedditPulseEngine
from utils.proxy_manager import ProxyManager
from utils.stealth_v2 import stealth_v2
from utils.humanizer import Humanizer
from backend.routers.slack_relay import send_oracle_alert

# Try to import Supabase, but don't fail immediately if missing (allows local dev setup)
try:
    from supabase import create_client, Client
except ImportError:
    print("❌ 'supabase' library not found. Please install it: pip install supabase")
    exit(1)

# Import Playwright
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ 'playwright' library not found. Please install it: pip install playwright && playwright install")
    exit(1)

load_dotenv()

class HydraController:
    def __init__(self, worker_id=None):
        # Honor WORKER_ID env var if provided, else use default
        self.worker_id = worker_id or os.getenv("WORKER_ID") or "production_hydra_01"
        self.proxy_manager = ProxyManager(os.getenv("PROXY_LIST_PATH"))
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            print("❌ Critical Error: SUPABASE_URL or SUPABASE_KEY not set.")
            # For robustness in testing environment without keys, we might want to warn instead of exit
            # but for production code, exit is correct.
            # exit(1) 

        print(f"[{self.worker_id}] Connecting to DataVault...")
        if self.url and self.key:
            self.supabase: Client = create_client(self.url, self.key)
        else:
            self.supabase = None
            print("⚠️ Running in OFFLINE mode (Simulated DB connection)")

        print(f"[{self.worker_id}] Online and Ready. 🐉")
        self.last_mesh_pulse = datetime.now()
        self._start_heartbeat()

    def _start_heartbeat(self):
        """Launches a background heartbeat task."""
        asyncio.create_task(self.heartbeat_loop())

    async def heartbeat_loop(self):
        while True:
            try:
                if self.supabase:
                    # Update a 'workers' table with our current status
                    self.supabase.table('worker_status').upsert({
                        "worker_id": self.worker_id,
                        "status": "active",
                        "last_pulse": datetime.now().isoformat()
                    }).execute()
            except Exception as e:
                print(f"[{self.worker_id}] Heartbeat Warning: {e}")
            await asyncio.sleep(30)

    async def poll_and_claim(self):
        """
        Atomically claims a job using the stored procedure 'fn_claim_job'.
        """
        if not self.supabase:
            await asyncio.sleep(5)
            return None

        try:
            # RPC call to the postgres function
            response = self.supabase.rpc('fn_claim_job', {'worker_id': self.worker_id}).execute()
            
            if response.data and len(response.data) > 0:
                print(f"⚡ Job Claimed: {response.data[0]['id']}")
                return response.data[0] # The job dict
            else:
                return None
        except Exception as e:
            print(f"⚠️ Error polling for work: {e}")
            return None

    async def process_job_with_browser(self, job):
        job_id = job.get('id')
        query = job.get('target_query')
        platform = job.get('target_platform', 'generic')
        
        print(f"⚔️ Engaging Target: {query} [{platform}]")
        
        scraped_data = {}
        verification_log = ""
        is_verified = False
        
        async with async_playwright() as p:
            # Get next proxy
            proxy_server = self.proxy_manager.get_proxy()
            # Add proxy support
            proxy = self.proxy_manager.get_residential() if platform == 'linkedin' else None
            
            # Launch real browser with Stealth Args
            browser = await p.chromium.launch(
                headless=True,
                args=launch_args,
                proxy=proxy
            )
            
            # Rotate User Agents
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.193 Mobile Safari/537.36"
            ]
            
            # Use Mobile UA for Swarm strategy
            if stealth_profile == "mobile":
                selected_ua = random.choice([ua for ua in user_agents if "Mobile" in ua])
                viewport = {"width": 390, "height": 844} # iPhone 14 style
                is_mobile = True
            else:
                selected_ua = random.choice([ua for ua in user_agents if "Mobile" not in ua])
                viewport = {"width": 1280, "height": 720}
                is_mobile = False

            print(f"   🎭 Stealth Mode: {stealth_profile.upper()} | UA: {selected_ua[:30]}...")

            context = await browser.new_context(
                user_agent=selected_ua,
                viewport=viewport,
                is_mobile=is_mobile,
                device_scale_factor=2 if is_mobile else 1,
                has_touch=is_mobile
            )
            page = await context.new_page()
            
            # Anti-detect script injection V2
            if stealth_profile == "stealth":
                await stealth_v2.apply_advanced_stealth(page)
            
            try:
                # A/B TESTING LOGIC
                ab_group = compliance.get('ab_test_group', 'A') # Assuming compliance dict might contain ab_test_group
                target_url = ""
                
                if query.startswith("http"):
                    target_url = query
                elif ab_group == 'B':
                    # Strategy B: Direct Domain Guessing (Experimental)
                    # "Apple" -> "https://www.apple.com"
                    safe_query = query.replace(" ", "").lower()
                    target_url = f"https://www.{safe_query}.com"
                    print(f"   [A/B Test] Group B selected. Trying direct access: {target_url}")
                else:
                    # Strategy A: Standard Google Search (Control)
                    target_url = f"https://www.google.com/search?q={query}"
                    print(f"   [A/B Test] Group A selected. Doing Search: {target_url}")
                
                print(f"   -> Navigating to {target_url}...")
                
                # Human-like Navigation with Retry Hardening
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        if platform != 'linkedin': # LinkedIn engine has its own nav
                             await page.goto(target_url, timeout=30000)
                             await page.wait_for_load_state("networkidle")
                             await stealth_v2.enact_human_behavior(page)
                             await Humanizer.random_sleep(1, 2)
                             await Humanizer.natural_scroll(page)
                        break # Success
                    except Exception as nav_err:
                        print(f"   ⚠️ Nav Attempt {attempt+1} failed: {nav_err}")
                        if attempt == max_retries - 1: raise nav_err
                        await asyncio.sleep(2 ** attempt)

                if platform == 'linkedin':
                    engine = LinkedInEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'google_maps':
                    engine = GoogleMapsGridEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'twitter':
                    engine = TwitterEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'instagram':
                    engine = InstagramEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'crunchbase':
                    engine = CrunchbaseEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'producthunt':
                    engine = ProductHuntEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'reddit':
                    engine = RedditEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'ycombinator':
                    engine = YCombinatorEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'website':
                    # Assuming WebsiteEngine exists and is imported
                    # from scrapers.website_engine import WebsiteEngine
                    # engine = WebsiteEngine(page)
                    # data_results = await engine.scrape(target_url)
                    # For now, fallback to generic if WebsiteEngine is not defined
                    await page.goto(target_url, timeout=30000)
                    await page.wait_for_load_state("domcontentloaded")
                    title = await page.title()
                    data_results = [{
                        "source_url": page.url,
                        "title": title,
                        "timestamp": datetime.now().isoformat(),
                        "meta_description": await page.evaluate("() => document.querySelector('meta[name=description]')?.content || ''"),
                        "verified": True if title else False
                    }]
                elif platform == 'tiktok':
                    engine = TikTokEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'reddit':
                    engine = RedditPulseEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'facebook':
                    engine = FacebookEngineV2(page)
                    data_results = await engine.scrape(query)
                elif platform == 'google_news':
                    engine = NewsPulseEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'real_estate':
                    engine = RealEstateEngine(page)
                    data_results = await engine.scrape(query)
                elif platform in ['job_scout', 'hiring']:
                    engine = JobScoutEngine(page)
                    data_results = await engine.scrape(query)
                elif platform in ['amazon', 'shopify', 'ecommerce']:
                    engine = CommerceWatchEngine(page)
                    data_results = await engine.scrape(query)
                else:
                    # Default / Fallback generic scraping
                    await page.goto(target_url, timeout=30000)
                    await page.wait_for_load_state("domcontentloaded")
                    title = await page.title()
                    data_results = [{
                        "source_url": page.url,
                        "title": title,
                        "timestamp": datetime.now().isoformat(),
                        "meta_description": await page.evaluate("() => document.querySelector('meta[name=description]')?.content || ''"),
                        "verified": True if title else False
                    }]

                if data_results:
                    # For V1 we just take the first or list
                    scraped_data = data_results[0] if isinstance(data_results, list) and len(data_results) > 0 else {}
                    if isinstance(data_results, list) and len(data_results) > 1:
                         # Store extra results logic if needed, for now just taking first is fine matching existing logic
                         pass
                    
                    title = scraped_data.get('title', 'Extracted Data')
                    is_verified = scraped_data.get('verified', False)
                else:
                    title = "No results found"
                    is_verified = False
                    
            except Exception as e:
                print(f"❌ Browser Error: {e}")
                verification_log = f"Browser Error: {str(e)}"
                is_verified = False
            finally:
                final_url = page.url if 'page' in locals() else "about:blank"
                # VISION-X: Capture screenshot for image-heavy results or instagram
                shot_path = f"screenshots/{job_id}.png"
                if platform in ['instagram', 'ecommerce'] and 'page' in locals():
                    os.makedirs("screenshots", exist_ok=True)
                    await page.screenshot(path=shot_path)
                
                # Aggressive Memory Cleanup (Phase 7 Hardening)
                await page.close()
                await context.close()
                await browser.close()
                
                # Force Python GC after browser close to free RAM for Render
                import gc
                gc.collect()
        
        # 1. Verification & Scoring via Arbiter
        if platform in ['instagram', 'ecommerce'] and os.path.exists(shot_path):
             clarity_score, verdict = await arbiter.score_visual_lead(query, shot_path)
        else:
             clarity_score, verdict = await arbiter.score_lead(query, scraped_data)
        
        print(f"   ⚖️  Arbiter Verdict: {verdict}")
        
        # 2. Predictive Intent Scoring (Phase 6)
        intent_data = {"intent_score": 0, "oracle_signal": "Baseline Intelligence"}
        if is_verified and clarity_score > 70:
            print(f"   🧠 Oracle: Analyzing Predictive Intent...")
            intent_data = await arbiter.predict_intent(scraped_data)
        
        # 3. Save results (Async)
        await self.finalize_job(job_id, scraped_data, is_verified, verdict, final_url, clarity_score, intent_data)

    async def check_opt_out(self, identifier):
        """
        Checks if the given identifier (email/phone) is in the global opt-out registry.
        """
        if not self.supabase or not identifier:
            return False
            
        try:
            # Hash the identifier to match the DB
            identifier_hash = hashlib.sha256(identifier.lower().strip().encode('utf-8')).hexdigest()
            
            res = self.supabase.table('opt_out_registry').select('id').eq('identifier_hash', identifier_hash).execute()
            return len(res.data) > 0
        except Exception as e:
            print(f"⚠️ Compliance check failed: {e}")
            return False

    async def finalize_job(self, job_id, data, verified, log_msg, source_url, clarity_score=0, intent_data=None):
        if not self.supabase:
            print(f"   [Offline] Job {job_id} done. Verified: {verified}")
            return

        try:
            # 0. COMPLIANCE CHECK (The Fortress of Truth)
            # Find any identifiers in the data and check them
            potential_identifiers = []
            if data.get('email'): potential_identifiers.append(data['email'])
            
            for ident in potential_identifiers:
                if await self.check_opt_out(ident):
                    print(f"   🛡️ Compliance Alert: Lead {ident} has opted out. Scrubbing data.")
                    data = {"status": "scrubbed", "reason": "User opted out via Compliance Portal"}
                    verified = False
                    clarity_score = 0
                    break

            # 1. Insert Result
            result_payload = {
                "job_id": job_id,
                "data_payload": data,
                "verified": verified,
                "clarity_score": clarity_score,
                "intent_score": intent_data.get('intent_score', 0) if intent_data else 0,
                "oracle_signal": intent_data.get('oracle_signal', 'Baseline') if intent_data else 'Baseline'
            }
            res_insert = self.supabase.table('results').insert(result_payload).execute()
            
            if res_insert.data:
                result_id = res_insert.data[0]['id']
                
                # 2. Log Provenance
                self.supabase.rpc('fn_log_provenance', {
                    'p_result_id': result_id,
                    'p_source_url': source_url,
                    'p_legal_basis': 'Legitimate Interest (B2B Public Data)',
                    'p_arbiter_verdict': log_msg
                }).execute()
                
                # 3. Mark Job Complete
                job_res = self.supabase.table('jobs').update({
                    'status': 'completed',
                    'result_count': 1, # simple count for single page
                    'completed_at': datetime.now().isoformat()
                }).eq('id', job_id).execute()
                
                job_data = job_res.data[0] if job_res.data else {}
                
                # 4. ONE-CLICK AGENCY: Autonomous Flow
                search_metadata = job_data.get('search_metadata', {})
                if search_metadata.get('one_click_agency') and verified and clarity_score > 80:
                    print(f"   🤖 One-Click Agency: Triggering Ghostwriter Flow for {result_id}...")
                    
                    # Generate Draft
                    draft = await arbiter.gemini_client.generate_outreach(data)
                    
                    # Save Draft
                    self.supabase.table('results').update({"outreach_draft": draft}).eq('id', result_id).execute()
                    
                    # Automatically send if email is present
                    target_email = data.get('email')
                    if target_email:
                        print(f"   📧 Engaging Target: {target_email}...")
                        # In a real setup, we'd trigger a task queue. 
                        # For Phase 5, we'll mark as 'outreach_queued'.
                        self.supabase.table('results').update({"outreach_status": "queued"}).eq('id', result_id).execute()

                # 5. THE INVISIBLE HAND: Slack Alerts (Phase 7)
                if intent_data.get('intent_score', 0) > 85:
                    print(f"   🕊️ The Invisible Hand: Sending Slack Alert for {result_id}...")
                    asyncio.create_task(send_oracle_alert(
                        org_id=job_data.get('org_id'),
                        result_id=result_id,
                        signal_text=intent_data.get('oracle_signal'),
                        intent_score=intent_data.get('intent_score')
                    ))

                print(f"💾 Data vaulted. Result ID: {result_id}")
            else:
                 print("⚠️ Inserted result but got no data back.")

        except Exception as e:
            print(f"❌ Failed to save mission data: {e}")

    async def run_loop(self):
        print(f"[{self.worker_id}] Entering continuous surveillance loop...")
        while True:
            job = await self.poll_and_claim()
            if job:
                job_id = job.get('id')
                query = job.get('target_query')
                platform = job.get('target_platform', 'generic')
                compliance = job.get('compliance', {}) # Assuming compliance is a dict in job
                ab_test_group = compliance.get('ab_test_group', 'A') # Default to A if not specified
                
                print(f"[{self.worker_id}] ⚡ Mission Start: {query} ({platform}) [Group {ab_test_group}]")
                
                # --- PHASE 7: MESH PULSE (P2P Coordination) ---
                if (datetime.now() - self.last_mesh_pulse).total_seconds() > 300:
                    await self.mesh_pulse()
                    self.last_mesh_pulse = datetime.now()

                # --- LAB: A/B/C STRATEGY SWITCHER ---
                if ab_test_group == 'C':
                    # Strategy C: The Swarm (Mobile Logic)
                    print(f"[{self.worker_id}] 🧪 Lab Mode: Engaging STRATEGY C (The Swarm - Mobile)")
                    launch_args = [
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox"
                    ]
                    stealth_profile = "mobile"
                elif ab_test_group == 'B':
                    # Strategy B: High Speed / Low Delay (Aggressive)
                    print(f"[{self.worker_id}] 🧪 Lab Mode: Engaging STRATEGY B (Aggressive)")
                    launch_args = ["--disable-blink-features=AutomationControlled"]
                    stealth_profile = "aggressive"
                else:
                    # Strategy A: High Stealth / High Delay (Control)
                    print(f"[{self.worker_id}] 🧪 Lab Mode: Engaging STRATEGY A (Stealth)")
                    launch_args = [
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-setuid-sandbox"
                    ] # stealth_v2 will add specific args
                    stealth_profile = "stealth"

                await self.process_job_with_browser(job_id, query, platform, compliance, launch_args, stealth_profile)
            else:
                await asyncio.sleep(5)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, help="Run for N seconds then exit", default=0)
    args = parser.parse_args()

    hydra = HydraController()
    
    if args.timeout > 0:
        # Run safely with timeout
        print(f"[{hydra.worker_id}] Running with timeout: {args.timeout}s")
        try:
             asyncio.run(asyncio.wait_for(hydra.run_loop(), timeout=args.timeout))
        except asyncio.TimeoutError:
             print(f"[{hydra.worker_id}] Timeout reached ({args.timeout}s). Exiting gracefully.")
    else:
        # Run forever
        asyncio.run(hydra.run_loop())

    async def mesh_pulse(self):
        """
        THE DIVINE MESH: Peer-to-Peer stealth coordination.
        Workers share which proxies are 'burned' and which User-Agents are currently 100% undetected.
        """
        if not self.supabase: return
        print("🛰️ Divine Mesh: Pulsing coordination data...")
        
        # Share some mock 'stealth data' to the worker_status table
        pulse_data = {
            "worker_id": self.worker_id,
            "stealth_health": 98.5,
            "best_user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X)",
            "last_pulse": datetime.now().isoformat()
        }
        try:
             self.supabase.table('worker_status').upsert(pulse_data).execute()
        except Exception as e:
             print(f"⚠️ Mesh Pulse Failure: {e}")
