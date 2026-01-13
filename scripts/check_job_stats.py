
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
from collections import Counter

# Load env vars
load_dotenv()
load_dotenv(".env")
load_dotenv("backend/.env") # Try backend folder
load_dotenv("../.env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY not found in environment.")
    sys.exit(1)

try:
    supabase = create_client(url, key)
    
    # Calculate 24h ago
    yesterday = (datetime.utcnow() - timedelta(hours=24)).isoformat()
    
    print(f"📡 Fetching jobs created after {yesterday}...")
    
    # Fetch all jobs (pagination might be needed if > 1000, assuming < 1000 for now or handled default)
    # Supabase default limit is often 1000.
    res = supabase.table('jobs').select('status').gt('created_at', yesterday).execute()
    
    if not res.data:
        print("No jobs found in the last 24 hours.")
        sys.exit(0)
        
    jobs = res.data
    total_count = len(jobs)
    
    # Aggregate
    status_counts = Counter(j['status'] for j in jobs)
    
    print(f"\n📊 Job Statistics (Last 24h) | Total: {total_count}")
    print("-" * 50)
    print(f"{'STATUS':<15} | {'COUNT':<10} | {'PERCENTAGE':<10}")
    print("-" * 50)
    
    for status, count in status_counts.most_common():
        percentage = round((count / total_count) * 100, 2)
        print(f"{status:<15} | {count:<10} | {percentage}%")
        
except Exception as e:
    print(f"❌ Error: {e}")
