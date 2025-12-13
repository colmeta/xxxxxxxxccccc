import time
import random
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load env from root if present (for local dev)
load_dotenv()

# We need the supabase client. 
# Attempt to import from backend if available, otherwise fallback (for standalone worker)
try:
    from supabase import create_client, Client
except ImportError:
    print("❌ 'supabase' library not found. Please install it: pip install supabase")
    exit(1)

class HydraController:
    def __init__(self, worker_id="local_hydra_01"):
        self.worker_id = worker_id
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            print("❌ Critical Error: SUPABASE_URL or SUPABASE_KEY not set.")
            exit(1)
            
        print(f"[{self.worker_id}] Connecting to DataVault at {self.url[:20]}...")
        self.supabase: Client = create_client(self.url, self.key)
        print(f"[{self.worker_id}] Online and hungry. 🐉")

    def poll_and_claim(self):
        """
        Atomically claims a job using the stored procedure 'fn_claim_job'.
        """
        try:
            # RPC call to the postgres function we created
            response = self.supabase.rpc('fn_claim_job', {'worker_id': self.worker_id}).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0] # The job dict
            else:
                return None
        except Exception as e:
            print(f"⚠️ Error polling for work: {e}")
            return None

    def execute_job(self, job):
        job_id = job['id']
        target = job['target_query']
        platform = job['target_platform']
        
        print(f"⚔️ Engaging Target: [{platform}] Job ID: {job_id}")
        
        start_time = time.time()
        
        # --- SIMULATION OF WORK ---
        # In a real version, this calls specific scraper classes based on 'platform'
        time.sleep(random.uniform(2, 5)) 
        
        # Dummy Result Data
        scraped_data = {
            "name": f" CEO of {target.split(' ')[-1]}",
            "company": target,
            "email": f"contact@{target.replace(' ', '').lower()}.com",
            "source": platform
        }
        
        # Dummy Verification
        is_verified = True 
        verification_log = "Verified against corporate registry."
        # --------------------------
        
        duration = round(time.time() - start_time, 2)
        print(f"✅ Mission Compleat. Duration: {duration}s")
        
        self.finalize_job(job_id, scraped_data, is_verified, verification_log, platform)

    def finalize_job(self, job_id, data, verified, log_msg, source_url):
        """
        Saves the result, logs provenance, and marks job as completed.
        All via Supabase.
        """
        try:
            # 1. Insert Result
            result_payload = {
                "job_id": job_id,
                "data_payload": data,
                "verified": verified
            }
            res_insert = self.supabase.table('results').insert(result_payload).execute()
            # Depending on supabase client version, data might be a list or dict. 
            # Usually data=[{...}]
            if res_insert.data:
                result_id = res_insert.data[0]['id']
                
                # 2. Log Provenance (using RPC for consistency)
                self.supabase.rpc('fn_log_provenance', {
                    'p_result_id': result_id,
                    'p_source_url': f"https://{source_url}.com/search?q=...",
                    'p_legal_basis': 'Legitimate Interest (B2B)',
                    'p_arbiter_verdict': log_msg
                }).execute()
                
                # 3. Mark Job Complete
                self.supabase.table('jobs').update({
                    'status': 'completed',
                    'result_count': 1,
                    'completed_at': datetime.now().isoformat()
                }).eq('id', job_id).execute()
                
                print(f"💾 Data vaulted. Result ID: {result_id}")
            else:
                 print("⚠️ Inserted result but got no data back.")

        except Exception as e:
            print(f"❌ Failed to save mission data: {e}")
            # Optional: Mark job as failed?

    def run_loop(self):
        print(f"[{self.worker_id}] Entering surveillance loop. Press Ctrl+C to abort.")
        while True:
            job = self.poll_and_claim()
            if job:
                self.execute_job(job)
            else:
                # Exponential backoff? For now just sleep.
                print("zzz...", end="\r")
                time.sleep(5)

if __name__ == "__main__":
    hydra = HydraController()
    hydra.run_loop()
