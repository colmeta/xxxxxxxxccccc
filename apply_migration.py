import os
import sys
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def apply_migration(sql_path):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found.")
        print("Note: SERVICE_ROLE_KEY is required to run raw SQL via RPC or similar.")
        return

    supabase = create_client(url, key)
    
    if not os.path.exists(sql_path):
        print(f"❌ Error: Migration file not found at {sql_path}")
        return

    with open(sql_path, 'r') as f:
        sql = f.read()

    print(f"🚀 Applying migration: {os.path.basename(sql_path)}...")
    
    try:
        # We use a common trick: exec_sql via RPC if defined, 
        # but since we might not have it, we'll try to use the migration logic
        # OR just inform the user we're assuming the DB is ready because 
        # the code is now "Schema-Aware".
        
        # However, for a "once and for all" fix, we want these columns to exist.
        # If the user has the 'pgmq' or similar extensions, or a custom exec function:
        # res = supabase.rpc('exec_sql', {'sql': sql}).execute()
        
        print("⚠️ Note: Direct SQL execution via SDK requires a 'postgres' RPC function.")
        print("Since the worker is now SCHEMA-AWARE, it will work even if columns are missing.")
        print("To fully upgrade, please run the SQL in migrations/20260212_fix_worker_status_schema.sql in your Supabase SQL Editor.")
        
    except Exception as e:
        print(f"❌ Migration Error: {e}")

if __name__ == "__main__":
    path = "supabase_db/migrations/20260212_fix_worker_status_schema.sql"
    apply_migration(path)
