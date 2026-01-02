import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def seed_real_job():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Supabase credentials missing.")
        return

    supabase: Client = create_client(url, key)
    
    # Target Query for Real Data
    job_data = {
        "target_query": "SaaS Founders NYC",
        "target_platform": "linkedin",
        "status": "queued",
        "compliance_mode": "strict"
    }
    
    try:
        # Check for existing user profiles to assign a real user_id if possible
        profiles = supabase.table('profiles').select('id').limit(1).execute()
        if profiles.data:
            job_data["user_id"] = profiles.data[0]['id']
            print(f"✅ Assigning job to user: {job_data['user_id']}")
        
        res = supabase.table('jobs').insert(job_data).execute()
        if res.data:
            print(f"🚀 Real Mission Seeded: '{job_data['target_query']}'")
            print(f"Mission ID: {res.data[0]['id']}")
        else:
            print("⚠️ Inserted but no data back.")
    except Exception as e:
        print(f"❌ Seeding failed: {e}")

if __name__ == "__main__":
    seed_real_job()
