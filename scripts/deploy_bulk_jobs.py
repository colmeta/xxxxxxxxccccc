
import os
import sys
import json
from dotenv import load_dotenv
from supabase import create_client

# Load Environment Variables
load_dotenv()
load_dotenv(".env")
load_dotenv("backend/.env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY not found in environment.")
    print("Please ensure .env is correctly set up.")
    sys.exit(1)

# Initialize Supabase Client
supabase = create_client(url, key)

def get_default_user():
    """Finds the first available user to run the jobs as."""
    try:
        # Try finding a profile
        res = supabase.table('profiles').select('*').limit(1).execute()
        if res.data:
            user = res.data[0]
            print(f"✅ Found User: {user.get('id')} (Org: {user.get('active_org_id')})")
            return user
        
        print("❌ No user profiles found. Please sign up in the frontend first.")
        return None
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return None

def deploy_jobs():
    user = get_default_user()
    if not user:
        return

    # --- DEFINE YOUR PROMPTS HERE ---
    queries = [
        "DevOps Engineers in San Francisco",
        "Product Managers in New York",
        "Data Scientists in Boston",
        "Generative AI Engineers in Austin",
        "Cybersecurity Specialists in London"
    ]
    platform = "linkedin"
    # --------------------------------
    
    user_id = user.get('id')
    org_id = user.get('active_org_id')
    
    jobs_to_insert = []
    
    print(f"\n🚀 Preparing {len(queries)} missions...")
    
    for q in queries:
        jobs_to_insert.append({
            "user_id": user_id,
            "org_id": org_id,
            "target_query": q,
            "target_platform": platform,
            "compliance_mode": "standard",
            "status": "queued",
            "ab_test_group": "A"
        })

    try:
        res = supabase.table('jobs').insert(jobs_to_insert).execute()
        print(f"✅ Successfully queued {len(jobs_to_insert)} jobs!")
        print("Check Mission Control or Database for status.")
    except Exception as e:
        print(f"❌ Failed to insert jobs: {e}")

if __name__ == "__main__":
    deploy_jobs()
