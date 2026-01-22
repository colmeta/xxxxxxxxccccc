from fastapi import APIRouter, HTTPException, Query, Body
from backend.services.supabase_client import get_supabase
from typing import Optional

router = APIRouter(prefix="/api/bridge", tags=["Extension Bridge"])

@router.get("/identify")
async def identify_profile(
    name: Optional[str] = None, 
    url: Optional[str] = None, 
    platform: str = "linkedin"
):
    """
    CLARITY PEARL: Extension Bridge
    Identifies if a profile matches any Mega-Profile in the Vault.
    """
    supabase = get_supabase()
    
    query = supabase.table('data_vault').select('*')
    
    if url:
        # Match by URL (LinkedIn, Twitter, etc)
        query = query.or_(f"linkedin_url.eq.{url},twitter_handle.ilike.%{url}%,tiktok_url.eq.{url}")
    elif name:
        # Match by Name (less precise)
        query = query.ilike('full_name', f"%{name}%")
    else:
        raise HTTPException(status_code=400, detail="Must provide name or url")

    res = query.limit(1).execute()
    
    if not res.data:
        return {"status": "not_found", "message": "No sovereign identity detected for this target."}

    lead = res.data[0]
    meta = lead.get('metadata', {})
    
    # Return redacted intelligence (for extension safety)
    return {
        "status": "found",
        "sovereign_id": lead.get('sovereign_id'),
        "full_name": lead.get('full_name'),
        "company": lead.get('company'),
        "velocity": meta.get('velocity_data', {}).get('scaling_signal', 'Stable'),
        "intent_score": lead.get('intent_score', 0),
        "displacement_script": meta.get('displacement_data', {}).get('sovereign_script', ''),
        "vault_id": lead.get('id')
    }
@router.post("/capture")
async def capture_profile(
    data: dict = Body(...)
):
    """
    CLARITY PEARL: Sovereign Capture
    Receives lead data from the browser extension and vaults it.
    """
    supabase = get_supabase()
    
    # 1. Standardize (Minimal Polish)
    profile = {
        "job_id": None, # Extension captures are direct
        "data_payload": data,
        "capture_source": "extension",
        "verified": True, # Extension captures are considered 'live' verified
        "clarity_score": 100 # Direct human capture
    }
    
    # 2. Insert into Results
    res = supabase.table('results').insert(profile).execute()
    
    if not res.data:
        raise HTTPException(status_code=500, detail="Vault Insertion Failed")
        
    return {"status": "success", "vault_id": res.data[0]['id']}
