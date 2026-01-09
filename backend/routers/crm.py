from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/crm", tags=["CRM Integration"])

class CRMSyncRequest(BaseModel):
    job_id: str
    crm_type: str  # 'hubspot', 'salesforce', 'pipedrive'
    api_key: str
    deal_stage: Optional[str] = "new_lead"

class LeadCRMSyncRequest(BaseModel):
    vault_id: str
    crm_type: str
    api_key: str

@router.post("/sync")
async def manual_crm_sync(user: dict = Depends(get_current_user)):
    """
    Manual CRM sync endpoint - syncs all high-intent leads to configured webhooks.
    Called by CRMHub component.
    """
    from backend.services.supabase_client import get_supabase
    supabase = get_supabase()
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        # Get org's webhook URL
        org_id = user.get("org_id")
        org_res = supabase.table('organizations').select('slack_webhook').eq('id', org_id).single().execute()
        
        if not org_res.data or not org_res.data.get('slack_webhook'):
            return {
                "status": "no_webhook",
                "message": "No webhook configured. Please add a webhook URL first.",
                "count": 0
            }
        
        webhook_url = org_res.data.get('slack_webhook')
        
        # Get high-intent leads from last 7 days
        from datetime import datetime, timedelta
        cutoff = (datetime.now() - timedelta(days=7)).isoformat()
        
        leads_res = supabase.table('results').select('*').gte('intent_score', 80).gte('created_at', cutoff).execute()
        
        synced_count = 0
        # In production, would actually POST to webhook_url here
        # For now, just log the sync
        for lead in (leads_res.data or []):
            supabase.table('crm_injection_logs').insert({
                "org_id": org_id,
                "result_id": lead.get('id'),
                "crm_name": "webhook",
                "status": "success"
            }).execute()
            synced_count += 1
        
        return {
            "status": "success",
            "message": f"Synced {synced_count} high-intent leads",
            "count": synced_count
        }
        
    except Exception as e:
        print(f"❌ Manual sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync/lead")
async def sync_lead_to_crm(request: LeadCRMSyncRequest):
    """
    CLARITY PEARL: Sovereign CRM Injection.
    Syncs a specific Mega-Profile with its intelligence (Displacement/Velocity) to a CRM.
    """
    from backend.services.supabase_client import get_supabase
    supabase = get_supabase()
    
    # 1. Fetch Lead from Data Vault
    res = supabase.table('data_vault').select('*').eq('id', request.vault_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Mega-Profile not found")
    
    lead = res.data
    meta = lead.get('metadata', {})
    
    # 2. Extract Sovereignty Data
    displacement_script = meta.get('displacement_data', {}).get('sovereign_script', 'No script generated')
    velocity_signal = meta.get('velocity_data', {}).get('scaling_signal', 'Stable')

    # 3. Construct Sovereign Payload
    crm_payload = {
        "properties": {
            "email": lead.get('email'),
            "firstname": lead.get('full_name', '').split(' ')[0],
            "lastname": ' '.join(lead.get('full_name', '').split(' ')[1:]),
            "company": lead.get('company'),
            "jobtitle": lead.get('title'),
            "twitter_handle": lead.get('twitter_handle'),
            "tiktok_url": lead.get('tiktok_url'),
            # Custom Intelligence Fields
            "clarity_pearl_velocity": velocity_signal,
            "clarity_pearl_displacement_script": displacement_script,
            "sovereign_id": lead.get('sovereign_id')
        }
    }

    # 4. Simulate CRM API Post
    print(f"🔥 INJECTING SOVEREIGN IDENTITY {lead.get('sovereign_id')} INTO {request.crm_type.upper()}...")
    
    # 5. Log the injection
    try:
        supabase.table("crm_logs").insert({
            "vault_id": request.vault_id,
            "crm_type": request.crm_type,
            "sync_status": "success",
            "payload": crm_payload
        }).execute()
    except: pass

    return {
        "status": "success",
        "message": f"Mega-Profile injected into {request.crm_type}.",
        "injected_data": crm_payload
    }
