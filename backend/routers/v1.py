from fastapi import APIRouter, HTTPException, Depends, Header
from backend.services.supabase_client import get_supabase
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1", tags=["Clarity Pearl API (White-Label)"])

# Dependency to validate API Key
async def verify_api_key(x_api_key: str = Header(...)):
    import hashlib
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    
    # Hash the provided key (keys are stored as SHA-256 hashes)
    key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
    
    try:
        # Use database function to validate and track usage
        result = supabase.rpc('fn_validate_api_key', {'p_key_hash': key_hash}).execute()
        if not result.data:
            raise HTTPException(status_code=401, detail="Invalid API Key")
        return result.data[0]['org_id']
    except Exception as e:
        print(f"API Key Validation Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or Expired API Key")

class ScoutRequest(BaseModel):
    query: str
    platform: str = "generic"
    webhook_url: Optional[str] = None

@router.post("/scout")
async def create_scout_job(job: ScoutRequest, org_id: str = Depends(verify_api_key)):
    """
    Launch a Scout Mission via API.
    """
    supabase = get_supabase()
    
    # Create Job targeted to the API Org
    new_job = {
        "org_id": org_id,
        "user_id": org_id, # Linking to Org Owner technically, but using Org ID for now as system user
        "target_query": job.query,
        "target_platform": job.platform,
        "status": "queued",
        "search_metadata": {"source": "api_v1", "webhook": job.webhook_url}
    }
    
    # We need a user_id. For V1 we'll look up the owner of the Org.
    org_res = supabase.table('organizations').select('owner_id').eq('id', org_id).execute()
    if org_res.data:
        new_job['user_id'] = org_res.data[0]['owner_id']
    else:
        raise HTTPException(status_code=500, detail="Organization Owner Invalid")

    res = supabase.table('jobs').insert(new_job).execute()
    return {"status": "dispatched", "job_id": res.data[0]['id']}

@router.get("/vault/{job_id}")
async def get_vault_data(job_id: str, org_id: str = Depends(verify_api_key)):
    """
    Retrieve Intelligence from the Vault.
    """
    supabase = get_supabase()
    
    # Verify ownership
    job_check = supabase.table('jobs').select('org_id').eq('id', job_id).execute()
    if not job_check.data or job_check.data[0]['org_id'] != org_id:
        raise HTTPException(status_code=404, detail="Mission not found or unauthorized")
        
    results = supabase.table('results').select('*').eq('job_id', job_id).execute()
    return {"mission_id": job_id, "intelligence": results.data}
