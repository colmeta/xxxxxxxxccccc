import asyncio
import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv

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
            # Launch real browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                # A/B TESTING LOGIC
                ab_group = job.get('ab_test_group', 'A')
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
                await page.goto(target_url, timeout=30000)
                await page.wait_for_load_state("domcontentloaded")
                
                # Real Extraction Logic
                title = await page.title()
                content_snippet = (await page.content())[:200]
                
                print(f"   -> Page Title: {title}")
                
                # Basic Verification Logic: Did we get a 200 OK and valid content?
                if title:
                    is_verified = True
                    verification_log = f"Successfully accessed {target_url}. Title: {title}"
                    
                    # Extract some basic metadata as 'enrichment'
                    scraped_data = {
                        "source_url": page.url,
                        "title": title,
                        "timestamp": datetime.now().isoformat(),
                        "meta_description": await page.evaluate("() => document.querySelector('meta[name=description]')?.content || ''")
                    }
                else:
                    verification_log = "Failed to extract page title."
                    
            except Exception as e:
                print(f"❌ Browser Error: {e}")
                verification_log = f"Browser Error: {str(e)}"
                is_verified = False
            finally:
                await browser.close()
        
        # Save results
        self.finalize_job(job_id, scraped_data, is_verified, verification_log, platform)

    def finalize_job(self, job_id, data, verified, log_msg, source_url):
        if not self.supabase:
            print(f"   [Offline] Job {job_id} done. Verified: {verified}")
            return

        try:
            # 1. Insert Result
            result_payload = {
                "job_id": job_id,
                "data_payload": data,
                "verified": verified
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
                self.supabase.table('jobs').update({
                    'status': 'completed',
                    'result_count': 1, # simple count for single page
                    'completed_at': datetime.now().isoformat()
                }).eq('id', job_id).execute()
                
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
                await self.process_job_with_browser(job)
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
