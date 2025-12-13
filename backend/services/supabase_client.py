import os
from supabase import create_client, Client
from typing import Optional

# Initialize Supabase Client
supabase: Optional[Client] = None

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase DataVault")
    else:
        print("⚠️ SUPABASE_URL or SUPABASE_KEY missing. Running in implementation mode.")
except Exception as e:
    print(f"❌ Failed to connect to Supabase: {e}")

def get_supabase() -> Optional[Client]:
    return supabase
