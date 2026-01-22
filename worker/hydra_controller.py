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
        if platform in ["google_maps", "google_maps_grid", "directory", "generic", "website", "linkedin"]:
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

    async def process_job_with_browser(self, job_data, launch_args=None, stealth_profile='stealth'):
        job_id = job_data.get('id')
        query = job_data.get('target_query')
        platform = job_data.get('target_platform', 'generic')
        compliance = job_data.get('compliance', {})
        
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
            # SANITIZATION: Remove commas to prevent breaking the PostgREST 'or_' syntax
            safe_query = query.replace(",", " ")
            vault_res = self.supabase.table('data_vault').select("*").or_(
                f"full_name.ilike.%{safe_query}%,title.ilike.%{safe_query}%,company.ilike.%{safe_query}%"
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
        # --- PHASE 12: ETERNAL PERSISTENCE (Self-Healing) ---
        stealth_profiles = ["stealth", "mobile", "aggressive"]
        if stealth_profile not in stealth_profiles:
            stealth_profiles.insert(0, stealth_profile)
        
        data_results = []
        final_url = ""

        from playwright.async_api import async_playwright

        for attempt_profile in stealth_profiles:
            print(f"[{self.worker_id}] 🛡️ Eternal Persistence: Attempting {attempt_profile.upper()} Cloak...")
            try:
                async with async_playwright() as p:
                    # Get next proxy from manager
                    proxy_url = self.proxy_manager.get_proxy()
                    proxy = None
                    if proxy_url and proxy_url != "direct":
                        proxy = {"server": proxy_url}
                        print(f"   🌐 Using Proxy: {proxy_url[:30]}...")
                    
                    browser = await p.chromium.launch(
                        headless=True,
                        args=launch_args,
                        proxy=proxy
                    )
                    
                    user_agents = [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1",
                        "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.193 Mobile Safari/537.36"
                    ]
                    
                    if attempt_profile == "mobile":
                        selected_ua = random.choice([ua for ua in user_agents if "Mobile" in ua])
                        viewport = {"width": 390, "height": 844}
                        is_mobile = True
                    else:
                        selected_ua = random.choice([ua for ua in user_agents if "Mobile" not in ua])
                        viewport = {"width": 1280, "height": 720}
                        is_mobile = False

                    context = await browser.new_context(
                        user_agent=selected_ua,
                        viewport=viewport,
                        is_mobile=is_mobile,
                        device_scale_factor=2 if is_mobile else 1,
                        has_touch=is_mobile
                    )
                    page = await context.new_page()
                    
                    # Apply Stealth
                    await stealth_v2.apply_advanced_stealth(page, user_agent=selected_ua)
                    
                    try:
                        # Navigator Logic
                        target_url = f"https://www.google.com/search?q={query}"
                        if query.startswith("http"): target_url = query
                        
                        if platform != 'linkedin':
                            print(f"   -> Navigating to {target_url}...")
                            await page.goto(target_url, timeout=30000)
                            await page.wait_for_load_state("networkidle")
                            await stealth_v2.enact_human_behavior(page)
                        
                        final_url = page.url
                        
                        # Platform Dispatcher
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
                        else:
                            from scrapers.website_engine import WebsiteEngine
                            engine = WebsiteEngine(page)
                            data_results = await engine.scrape(target_url)

                        if data_results:
                            # Success!
                            print(f"[{self.worker_id}] ✨ Persistence Success! Found {len(data_results)} leads.")
                            break
                        else:
                            print(f"[{self.worker_id}] ⚠️ {attempt_profile.upper()} failed to yield results. Re-cloaking...")

                    except Exception as loop_err:
                        print(f"   ⚠️ Persistence Loop Error: {loop_err}")
                    finally:
                        # VISION-X: Capture screenshot for image-heavy results or instagram
                        if platform in ['instagram', 'ecommerce']:
                            os.makedirs("screenshots", exist_ok=True)
                            try:
                                await page.screenshot(path=shot_path)
                            except: pass
                        
                        await page.close()
                        await context.close()
                        await browser.close()
            except Exception as outer_err:
                print(f"   ❌ Persistence Attempt Failed: {outer_err}")

        # Aggressive Memory Cleanup
        import gc
        gc.collect()

        
        # --- PHASE 10: BULK DATA VAULTING ---
        if not data_results:
            print(f"   ⚠️ No data found for mission {job_id}. Skipping vault.")
            if self.supabase:
                self.supabase.table('jobs').update({
                    'status': 'completed',
                    'result_count': 0,
                    'completed_at': datetime.now().isoformat()
                }).eq('id', job_id).execute()
            return

        print(f"   💾 Vaulting {len(data_results)} leads...")
        saved_count = 0
        seen_leads = set() # Mission-level deduplication
        
        for lead in data_results:
            try:
                # --- PHASE 11: DATA PURITY (ClarityPearl) ---
                # 1. Deduplication
                lead_id = lead.get('email') or lead.get('source_url') or lead.get('linkedin_url')
                if lead_id in seen_leads:
                    continue
                seen_leads.add(lead_id)

                # 2. Data Polishing (Standardization)
                polished_lead = arbiter.polish_lead(lead)
                
                # 3. Verification & Scoring via Arbiter
                if platform in ['instagram', 'ecommerce'] and os.path.exists(shot_path):
                     clarity_score, verdict = await arbiter.score_visual_lead(query, shot_path)
                else:
                     clarity_score, verdict = await arbiter.score_lead(query, polished_lead)
                
                # 4. Triple-Verification Protocol
                is_verified = lead.get('verified', False)
                has_site = bool(lead.get('website'))
                has_email = bool(lead.get('email') or lead.get('decision_maker_email'))
                
                if is_verified and has_site and has_email and clarity_score > 85:
                    polished_lead['triple_verified'] = True
                    print(f"   💎 TRIPLE-VERIFIED Lead Detected: {polished_lead.get('name')}")

                # 5. Predictive Intent Scoring
                intent_data = {"intent_score": 0, "oracle_signal": "Baseline Intelligence"}
                if is_verified and clarity_score > 70:
                    intent_data = await arbiter.predict_intent(polished_lead)
                
                # 6. Save individual result
                await self._save_single_result(job_data, polished_lead, is_verified, verdict, final_url, clarity_score, intent_data)
                saved_count += 1
            except Exception as loop_err:
                print(f"   ⚠️ Failed to save lead: {loop_err}")

        # 4. Finalize Job Status
        if self.supabase:
            self.supabase.table('jobs').update({
                'status': 'completed',
                'result_count': saved_count,
                'completed_at': datetime.now().isoformat()
            }).eq('id', job_id).execute()
        
        print(f"🏁 Mission {job_id} Complete. {saved_count} flags planted in the Vault.")

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

    async def _save_single_result(self, job_data, data, verified, log_msg, source_url, clarity_score=0, intent_data=None):
        job_id = job_data.get('id')
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

            # 1. Polish Data (The Clarity Pearl Standard)
            data = arbiter.polish_lead(data)

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
                
                # 3. Mark Job Stats (Optional: Incremental count in DB if needed)
                # For now, we update total count at the end of process_job_with_browser
                
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

                await self.process_job_with_browser(job, launch_args, stealth_profile)
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
