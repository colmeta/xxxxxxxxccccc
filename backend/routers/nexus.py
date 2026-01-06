from fastapi import APIRouter, Header, HTTPException, Depends
from backend.services.supabase_client import get_supabase
import hashlib

router = APIRouter(prefix="/api/nexus", tags=["Nexus White-Label"])

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header missing")
    
    supabase = get_supabase()
    hashed = hashlib.sha256(x_api_key.encode()).hexdigest()
    
    res = supabase.table('api_keys').select('org_id').eq('key_hash', hashed).execute()
    if not res.data:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    return res.data[0]['org_id']

@router.get("/query")
async def query_vault(
    q: str, 
    org_id: str = Depends(verify_api_key)
):
    """
    Query the Intelligence Vault via API.
    Used by white-label partners.
    """
    supabase = get_supabase()
    
    # Search in results that belong to the org's jobs
    res = supabase.table('results').select('*, jobs!inner(*)').eq('jobs.org_id', org_id).ilike('data_payload->>name', f'%{q}%').execute()
    
    return {
        "count": len(res.data) if res.data else 0,
        "results": res.data
    }
