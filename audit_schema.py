import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def audit_schema():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: Supabase credentials not found.")
        return

    supabase = create_client(url, key)
    
    try:
        # We can't directly list columns easily without raw SQL, 
        # but we can try to fetch a single row and see the keys.
        res = supabase.table('worker_status').select('*').limit(1).execute()
        if res.data:
            print("--- Columns in worker_status ---")
            for col in res.data[0].keys():
                print(f"- {col}")
        else:
            # If table is empty, we might need a different approach or just check if insert works
            print("⚠️ Table is empty, cannot infer columns from data.")
    except Exception as e:
        print(f"❌ Error auditing schema: {e}")

if __name__ == "__main__":
    audit_schema()
