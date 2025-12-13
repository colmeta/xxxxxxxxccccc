import os
from dotenv import load_dotenv

# Load env vars BEFORE importing backend
load_dotenv()

from backend.services.supabase_client import get_supabase
import sys

def test_connection():
    print("🔌 Testing Supabase Connection...")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Missing Environment Variables!")
        return

    print(f"   URL: {url}")
    print(f"   Key: {key[:10]}...") 

    supabase = get_supabase()
    
    if not supabase:
        print("❌ Failed to initialize Supabase client.")
        return

    try:
        # Try a lightweight call to verify connectivity
        # We can't query a table easily if we don't know permissions, but we can check health or auth
        # Let's try to just print the client status or make a dummy query to 'jobs' which might fail but shows network connectivity
        print("✅ Client initialized.")
        
        # Checking if we can actually reach the server
        # Often a select on a non-existent row is a safe test
        print("   Attempting to connect to 'jobs' table...")
        response = supabase.table("jobs").select("count", count="exact").execute()
        print(f"✅ Connection successful! found {response.count} jobs (or accessible rows).")
        
    except Exception as e:
        print(f"⚠️ Connection check encountered an error (this might be normal if tables don't exist yet): {e}")

if __name__ == "__main__":
    test_connection()
