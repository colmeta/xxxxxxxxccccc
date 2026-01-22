from fastapi import APIRouter, Body, Depends, HTTPException
import httpx
import os
from backend.dependencies import get_current_user
from backend.services.supabase_client import get_supabase

router = APIRouter(prefix="/api/relay", tags=["The Invisible Hand v2"])

@router.post("/webhook/setup")
async def setup_webhook(
    webhook_url: str = Body(..., embed=True), 
    user: dict = Depends(get_current_user)
):
    """
    Setup a generic Outbound Webhook (Zapier/Make.com) for an organization.
    """
    supabase = get_supabase()
    org_id = user.get("org_id")
    
    if not org_id:
        raise HTTPException(status_code=400, detail="Org context required.")

    # Save to organizations table
    supabase.table('organizations').update({"outbound_webhook": webhook_url}).eq('id', org_id).execute()
    
    return {"status": "success", "message": "Outbound Webhook (The Invisible Hand v2) Activated."}

async def send_webhook_alert(org_id, result_id, event_type, lead_data):
    """
    Relays a lead event to the generic outbound webhook (The Invisible Hand v2).
    """
    supabase = get_supabase()
    org_res = supabase.table('organizations').select('outbound_webhook').eq('id', org_id).execute()
    
    if not org_res.data or not org_res.data[0].get('outbound_webhook'):
         return

    webhook_url = org_res.data[0]['outbound_webhook']
    
    payload = {
        "event": event_type,
        "result_id": result_id,
        "lead": lead_data,
        "timestamp": os.getenv("CURRENT_TIME", "2026-01-22T15:00:00Z")
    }
    
    try:
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json=payload)
    except Exception as e:
        print(f"   ⚠️ Outbound Webhook Failed: {e}")
