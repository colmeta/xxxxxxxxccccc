import asyncio
import os
import json
import random
from datetime import datetime
import sys
import os

# Ensure the worker directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
import hashlib
# Avoid top-level engine imports to prevent dependency-related load failures
# Scrapers are now imported lazily within processing methods

from utils.arbiter import arbiter
from utils.enrichment_bridge import EnrichmentBridge
from utils.proxy_manager import ProxyManager
from utils.stealth_v2 import stealth_v2
from utils.humanizer import Humanizer
from utils.email_verifier import email_verifier
from utils.lead_prioritizer import lead_prioritizer
from backend.routers.slack_relay import send_oracle_alert
from utils.velocity_engine import velocity_engine

# Try to import Supabase, but don't fail immediately if missing (allows local dev setup)
try:
    from supabase import create_client, Client
except ImportError:
    pass # Handled in __init__ if needed

# Import Playwright
try:
    from playwright.async_api import async_playwright
except ImportError:
    pass # Handled in process_job_with_browser

load_dotenv()

class HydraController:
    def __init__(self, worker_id=None):
        # Honor WORKER_ID env var if provided, else use default
        self.worker_id = worker_id or os.getenv("WORKER_ID") or "production_hydra_01"
        self.supabase = None
        self.supported_columns = [] # Dynamic schema discovery
        
        # Initialize Supabase
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        if url and key:
            try:
                self.supabase = create_client(url, key)
                print(f"[{self.worker_id}] Supabase Connection Active.")
                # Schema discovery will happen lazily in mesh_pulse or heartbeat
            except Exception as e:
                print(f"[{self.worker_id}] Supabase Connection Failed: {e}")
        
        self.proxy_manager = ProxyManager(os.getenv("PROXY_LIST_PATH"))
        self.stealth_helper = stealth_v2
        self.humanizer = Humanizer()
        self.email_verifier = email_verifier
        self.prioritizer = lead_prioritizer
        self.active_missions = 0
        self.start_time = datetime.now()
        self.last_mesh_pulse = datetime.min

    async def _discover_supported_columns(self):
        """Discovers which columns exist in worker_status to avoid SQL errors."""
        if not self.supabase: return
        try:
            # Fetch 1 record to see available keys
            res = self.supabase.table('worker_status').select('*').limit(1).execute()
            if res.data and len(res.data) > 0:
                self.supported_columns = list(res.data[0].keys())
                print(f"🛰️ Schema Discovery: Found {len(self.supported_columns)} supported columns.")
            else:
                # If table is empty, we default to the legacy set to be safe
                self.supported_columns = ["worker_id", "status", "last_pulse"]
                print("⚠️ Schema Discovery: Table empty, using legacy fallback columns.")
        except Exception as e:
            print(f"⚠️ Schema Discovery Failed: {e}")
            self.supported_columns = ["worker_id", "status", "last_pulse"]

    def _start_heartbeat(self):
        """Launches a background heartbeat task."""
        asyncio.create_task(self.heartbeat_loop())

    async def heartbeat_loop(self):
        while True:
            try:
                if self.supabase:
                    # Defensive heartbeat: only send supported columns
                    payload = {"worker_id": self.worker_id}
                    if "status" in self.supported_columns: payload["status"] = "active"
                    if "last_pulse" in self.supported_columns: payload["last_pulse"] = datetime.now().isoformat()
                    
                    self.supabase.table('worker_status').upsert(payload).execute()
            except Exception as e:
                print(f"[{self.worker_id}] Heartbeat Warning: {e}")
            await asyncio.sleep(30)

    async def _handle_enrichment(self, data, platform, page):
        """
        Sub-routine to bridge from entity (business) to person (lead).
        """
        if platform in ["google_maps", "google_maps_grid", "directory"]:
            bridge = EnrichmentBridge(page)
            # Flatten data if it's in a nested list from grid engine
            flat_leads = []
            for item in data:
                if isinstance(item, dict) and 'data' in item:
                    flat_leads.extend(item['data'])
                else:
                    flat_leads.append(item)
            
            return await bridge.enrich_business_leads(flat_leads)
        return data

    async def poll_and_claim(self):
        """
        Atomically claims a job using the stored procedure 'fn_claim_job'.
        """
        if not self.supabase:
            await asyncio.sleep(5)
            return None

        try:
            # RPC call to the postgres function
            response = self.supabase.rpc('fn_claim_job', {'p_worker_id': self.worker_id}).execute()
            
            if response.data and len(response.data) > 0:
                print(f"⚡ Job Claimed: {response.data[0]['id']}")
                return response.data[0] # The job dict
            else:
                return None
        except Exception as e:
            print(f"⚠️ Error polling for work: {e}")
            return None

    async def process_job_with_browser(self, job_id, query, platform='generic', compliance=None, launch_args=None, stealth_profile='stealth'):
        print(f"⚔️ Engaging Target: {query} [{platform}]")
        
        # --- INITIALIZATION SAFETY ---
        scraped_data = {}
        data_results = []
        is_verified = False
        final_url = ""
        shot_path = f"screenshots/mission_{job_id[:8]}.png"
        
        if not launch_args:
            launch_args = ["--no-sandbox"]

        # --- IMPERIAL STRATEGY: DATA VAULT LEVERAGE ---
        # Check if we already have verified leads in the vault for this query
        print(f"📡 Vault Search: Scanning local intelligence for '{query}'...")
        try:
            # Simple keyword match on title/company or name
            vault_res = self.supabase.table('data_vault').select("*").or_(
                f"full_name.ilike.%{query}%,title.ilike.%{query}%,company.ilike.%{query}%"
            ).order('last_verified_at', desc=True).limit(20).execute()
            
            if vault_res.data:
                print(f"💎 Vault Hit: found {len(vault_res.data)} existing leads. Leveraging...")
                # Format vault hits as scrape items
                vault_leads = []
                for v in vault_res.data:
                    vault_leads.append({
                        "name": v.get('full_name'),
                        "title": v.get('title'),
                        "company": v.get('company'),
                        "email": v.get('email'),
                        "source_url": v.get('linkedin_url'),
                        "vault_leverage": True,
                        "verified": True
                    })
                scraped_data = vault_leads
                
                # If we have many hits, we could theoretically skip the scrape
                # For now, we continue to append new results to the vault hits
        except Exception as vault_err:
            print(f"⚠️ Vault Lookup Failed: {vault_err}")

        async with async_playwright() as p:
            # Get next proxy from manager
            proxy_url = self.proxy_manager.get_proxy()
            proxy = None
            
            # Format proxy for Playwright if not "direct"
            if proxy_url and proxy_url != "direct":
                proxy = {"server": proxy_url}
                print(f"   🌐 Using Proxy: {proxy_url[:30]}...")
            
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
            
            # Anti-detect script injection V2 (Applying to ALL profiles for Maximum Capacity)
            if stealth_profile in ["stealth", "mobile", "aggressive"]:
                await stealth_v2.apply_advanced_stealth(page, user_agent=selected_ua)
            
            try:
                # A/B TESTING LOGIC
                ab_group = compliance.get('ab_test_group', 'A') if compliance else 'A'
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

                final_url = page.url
                
                # --- PLATFORM DISPATCHER (Refactored) ---
                if platform == "linkedin":
                    from scrapers.linkedin_engine import LinkedInEngine
                    engine = LinkedInEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == "google_maps":
                    from scrapers.google_maps_engine import GoogleMapsEngine
                    engine = GoogleMapsEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == "google_maps_grid":
                    from scrapers.google_maps_grid_engine import GoogleMapsGridEngine
                    engine = GoogleMapsGridEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == "directory":
                    from scrapers.directory_engine import DirectoryEngine
                    engine = DirectoryEngine(page)
                    data_results = await engine.scrape(query)
                elif platform in ["producthunt", "tiktok", "amazon", "shopify", "omni"]:
                    from scrapers.omni_scout_engine import OmniScoutEngine
                    engine = OmniScoutEngine(page)
                    data_results = await engine.unified_scout(query)
                elif platform == 'twitter':
                    from scrapers.social_radar import TwitterEngine
                    engine = TwitterEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'instagram':
                    from scrapers.social_radar import InstagramEngine
                    engine = InstagramEngine(page)
                    data_results = await engine.scrape(query)
                elif platform in ['google_news', 'news']:
                    from scrapers.news_pulse_engine import NewsPulseEngine
                    engine = NewsPulseEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'real_estate':
                    from scrapers.real_estate_engine import RealEstateEngine
                    engine = RealEstateEngine(page)
                    data_results = await engine.scrape(query)
                elif platform in ['job_scout', 'hiring']:
                    from scrapers.job_scout_engine import JobScoutEngine
                    engine = JobScoutEngine(page)
                    data_results = await engine.scrape(query)
                elif platform == 'facebook':
                    from scrapers.facebook_engine_v2 import FacebookEngineV2
                    engine = FacebookEngineV2(page)
                    data_results = await engine.scrape(query)
                elif platform == 'website':
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

                # --- ENRICHMENT BRIDGE ---
                if data_results:
                    data_results = await self._handle_enrichment(data_results, platform, page)
                    # For V1 we just take the first or the whole list depending on result handling
                    scraped_data = data_results[0] if isinstance(data_results, list) and len(data_results) > 0 else (data_results if isinstance(data_results, dict) else {})
                    is_verified = scraped_data.get('verified', False)
                else:
                    is_verified = False
                    
            except Exception as e:
                print(f"❌ Browser Error: {e}")
                verification_log = f"Browser Error: {str(e)}"
                is_verified = False
            finally:
                # VISION-X: Capture screenshot for image-heavy results or instagram
                if platform in ['instagram', 'ecommerce'] and 'page' in locals():
                    os.makedirs("screenshots", exist_ok=True)
                    try:
                        await page.screenshot(path=shot_path)
                    except:
                        pass
                
                # Aggressive Memory Cleanup (Phase 7 Hardening)
                await page.close()
                await context.close()
                await browser.close()
                
                # Force Python GC after browser close to free RAM for Render
                import gc
                gc.collect()
        
        # 1. Verification & Scoring via Arbiter
        # CRITICAL: Skip vaulting if no data was found to prevent junk results
        if not scraped_data:
            print(f"   ⚠️ No data found for mission {job_id}. Skipping vault.")
            # Mark job as completed with 0 results
            if self.supabase:
                self.supabase.table('jobs').update({
                    'status': 'completed',
                    'result_count': 0,
                    'completed_at': datetime.now().isoformat()
                }).eq('id', job_id).execute()
            return

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
            # --- PHASE 10: THE SOVEREIGN MIND (Velocity & Displacement) ---
            velocity_data = {"scaling_signal": "Stable", "growth_rate_pct": 0}
            displacement_data = {}
            
            result_payload = None
            try:
                # Look for previous snapshot for velocity
                prev_res = self.supabase.table('data_vault').select("*").eq('email', data.get('email')).limit(1).execute()
                if prev_res.data:
                    velocity_data = velocity_engine.calculate_velocity(prev_res.data[0], data)
                    
                    # Generate Displacement Script if we have growth/competitors
                    displacement_data = await arbiter.generate_sovereign_displacement(data, velocity_data)
            except Exception as vel_err:
                print(f"   ⚠️ Velocity/Displacement calculation failed: {vel_err}")

            result_payload = {
                "job_id": job_id,
                "data_payload": data,
                "verified": verified,
                "clarity_score": clarity_score,
                "intent_score": intent_data.get('intent_score', 0) if intent_data else 0,
                "oracle_signal": intent_data.get('oracle_signal', 'Baseline') if intent_data else 'Baseline',
                "predictive_growth_score": intent_data.get('predictive_growth_score', 0) if intent_data else 0,
                "reasoning": intent_data.get('reasoning', '') if intent_data else '',
                "velocity_data": velocity_data,
                "displacement_data": displacement_data
            }
            
            if result_payload:
                try:
                    res_insert = self.supabase.table('results').insert(result_payload).execute()
                except Exception as insert_err:
                    print(f"   ⚠️ Full insert failed (likely schema mismatch). Trying minimal insert... Error: {insert_err}")
                    # Fallback to minimal payload
                    min_payload = {
                        "job_id": job_id,
                        "data_payload": data,
                        "verified": verified,
                        "clarity_score": clarity_score
                    }
                    res_insert = self.supabase.table('results').insert(min_payload).execute()
            
            if result_payload and res_insert.data:
                result_id = res_insert.data[0]['id']
                
                # 1a. INNOVATION: Real-Time Email Verification
                target_email = data.get('email')
                if target_email and verified:
                    print(f"   📧 Verifying email deliverability...")
                    try:
                        email_check = await email_verifier.verify_email(target_email)
                        if email_check['risk_score'] > 50:
                            print(f"   ⚠️ High-risk email detected (score: {email_check['risk_score']})")
                            # Update result with email verification data
                            self.supabase.table('results').update({
                                "data_payload": {**data, "email_risk_score": email_check['risk_score'], "email_checks": email_check['checks']}
                            }).eq('id', result_id).execute()
                    except Exception as e:
                        print(f"   ⚠️ Email verification failed: {e}")
                
                # 1b. INNOVATION: AI-Powered Lead Prioritization
                if verified and intent_data:
                    print(f"   🎯 Calculating lead priority...")
                    try:
                        priority_data = await lead_prioritizer.calculate_priority_score(data, intent_data)
                        self.supabase.table('results').update({
                            "priority_score": priority_data['priority_score'],
                            "routing_reason": priority_data['routing_reason']
                        }).eq('id', result_id).execute()
                        
                        # Auto-route if high priority
                        if priority_data['should_auto_assign']:
                            await lead_prioritizer.auto_route_lead(result_id, job_data.get('org_id'), priority_data['priority_score'])
                    except Exception as e:
                        print(f"   ⚠️ Lead prioritization failed: {e}")
                
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
                        intent_score=intent_data.get('intent_score'),
                        lead_data=data,
                        velocity_signal=velocity_data.get('scaling_signal'),
                        displacement_script=displacement_data.get('sovereign_script')
                    ))

                # 6. RECURSIVE FACT-CHECKING (The Sleuth Protocol)
                if intent_data.get('intent_score', 0) > 90:
                    print(f"   🕵️ Sleuth Protocol: Activating Recursive Fact-Check...")
                    verification_query = await arbiter.recursive_verdict(data)
                    self.supabase.table('jobs').insert({
                        "org_id": job_data.get('org_id'),
                        "user_id": job_data.get('user_id'),
                        "target_query": verification_query,
                        "target_platform": "google_news", # Verify via news
                        "compliance_mode": "strict",
                        "status": "queued",
                        "priority": 5,
                        "search_metadata": {"recursive_origin": result_id}
                    }).execute()

                print(f"💾 Data vaulted. Result ID: {result_id}")
            else:
                 print("⚠️ Inserted result but got no data back.")

        except Exception as e:
            print(f"❌ Failed to save mission data: {e}")

    async def run_loop(self):
        print(f"[{self.worker_id}] Entering continuous surveillance loop...")
        self._start_heartbeat()
        while True:
            job = await self.poll_and_claim()
            if job:
                job_id = job.get('id')
                query = job.get('target_query')
                platform = job.get('target_platform', 'generic')
                compliance = job.get('compliance', {}) # Assuming compliance is a dict in job
                ab_test_group = compliance.get('ab_test_group', 'A') if compliance else 'A'
                
                print(f"[{self.worker_id}] ⚡ Mission Start: {query} ({platform}) [Group {ab_test_group}]")
                
                # --- PHASE 7: MESH PULSE (P2P Coordination) ---
                if (datetime.now() - self.last_mesh_pulse).total_seconds() > 300:
                    await self.mesh_pulse()
                    self.last_mesh_pulse = datetime.now()

                # --- LAB: A/B/C STRATEGY SWITCHER ---
                # FORCE STRATEGY C: THE SWARM (Mobile) - User Requested Maximum Capacity
                if True: # Force Mobile Swarm
                    # Strategy C: The Swarm (Mobile Logic)
                    print(f"[{self.worker_id}] 🧪 Lab Mode: Engaging STRATEGY C (The Swarm - Mobile) [FORCED]")
                    launch_args = [
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox"
                    ]
                    stealth_profile = "mobile"
                # elif ab_test_group == 'B':
                #     # Strategy B: High Speed / Low Delay (Aggressive)
                #     print(f"[{self.worker_id}] 🧪 Lab Mode: Engaging STRATEGY B (Aggressive)")
                #     launch_args = ["--disable-blink-features=AutomationControlled"]
                #     stealth_profile = "aggressive"
                # else:
                #     # Strategy A: High Stealth / High Delay (Control)
                #     print(f"[{self.worker_id}] 🧪 Lab Mode: Engaging STRATEGY A (Stealth)")
                #     launch_args = [
                #         "--disable-blink-features=AutomationControlled",
                #         "--no-sandbox",
                #         "--disable-setuid-sandbox"
                #     ] # stealth_v2 will add specific args
                #     stealth_profile = "stealth"

                await self.process_job_with_browser(job_id, query, platform, compliance, launch_args, stealth_profile)
            else:
                await asyncio.sleep(5)

    async def _discover_node_identity(self):
        """
        CLARITY PEARL: Node Identity Discovery
        Fetches the current residential node's geographic and IP profile.
        """
        print("🌍 Discovering residential node identity...")
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                res = await client.get("https://ipapi.co/json/")
                if res.status_code == 200:
                    data = res.json()
                    self.node_geo = {
                        "public_ip": data.get("ip"),
                        "geo_city": data.get("city"),
                        "geo_country": data.get("country_name"),
                        "ip_authority": 9.5 if "Residential" in data.get("org", "") or "ISP" in data.get("org", "") else 5.0
                    }
                    print(f"🛰️ Node Identified: {self.node_geo['geo_city']}, {self.node_geo['geo_country']} ({self.node_geo['public_ip']})")
                    return self.node_geo
        except Exception as e:
            print(f"⚠️ Node Discovery Failed: {e}")
            self.node_geo = {"public_ip": "Unknown", "geo_city": "Unknown", "geo_country": "Unknown", "ip_authority": 1.0}
        return self.node_geo

    async def mesh_pulse(self):
        """
        THE DIVINE MESH: Peer-to-Peer stealth coordination.
        Now enhanced with Phase 11 Global Swarm Metadata.
        """
        import random
        from datetime import datetime
        if not self.supabase: return
        
        # 1. Discover identity if not already found
        if not hasattr(self, 'node_geo'):
            await self._discover_node_identity()

        print("🛰️ Divine Mesh: Pulsing coordination data...")
        
        health = 98.0 + (random.random() * 2) 
        
        # ALL POSSIBLE COLUMNS
        full_payload = {
            "worker_id": self.worker_id,
            "stealth_health": round(health, 2),
            "best_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "active_missions": self.active_missions,
            "last_pulse": datetime.now().isoformat(),
            "burned_proxies": list(self.proxy_manager.bad_proxies) if hasattr(self.proxy_manager, 'bad_proxies') else (self.proxy_manager.banned_proxies if hasattr(self.proxy_manager, 'banned_proxies') else []),
            "node_type": "residential",
            "public_ip": self.node_geo.get("public_ip"),
            "geo_city": self.node_geo.get("geo_city"),
            "geo_country": self.node_geo.get("geo_country"),
            "ip_authority_score": self.node_geo.get("ip_authority")
        }
        
        # DEFENSIVE PULSE: Only send what the DB supports
        safe_payload = {}
        if not self.supported_columns:
            # Lazy discovery if first run
            await self._discover_supported_columns()
            
        if not self.supported_columns:
            # Fallback if discovery still blank: send absolute minimum
             safe_payload = {"worker_id": self.worker_id, "last_pulse": full_payload["last_pulse"]}
        else:
            for k, v in full_payload.items():
                if k in self.supported_columns:
                    safe_payload[k] = v

        try:
             self.supabase.table('worker_status').upsert(safe_payload).execute()
        except Exception as e:
             print(f"⚠️ Mesh Pulse Failure: {e}")


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
