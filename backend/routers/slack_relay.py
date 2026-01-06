from fastapi import APIRouter, Body, Depends, HTTPException
import httpx
import os
from backend.dependencies import get_current_user
from backend.services.supabase_client import get_supabase

router = APIRouter(prefix="/api/relay", tags=["The Invisible Hand"])

@router.post("/slack/setup")
async def setup_slack(
    webhook_url: str = Body(..., embed=True), 
    user: dict = Depends(get_current_user)
):
    """
    Setup the Invisible Hand (Slack Integration) for an organization.
    """
    supabase = get_supabase()
    org_id = user.get("org_id")
    
    if not org_id:
        raise HTTPException(status_code=400, detail="Org context required.")

    # Save to organizations table (adding a field for slack_webhook)
    supabase.table('organizations').update({"slack_webhook": webhook_url}).eq('id', org_id).execute()
    
    return {"status": "success", "message": "Slack Relay Activated."}

async def send_oracle_alert(org_id, result_id, signal_text, intent_score):
    """
    The Invisible Hand in action: Relays high-value Oracle signals to Slack.
    """
    supabase = get_supabase()
    org_res = supabase.table('organizations').select('slack_webhook').eq('id', org_id).execute()
    
    if not org_res.data or not org_res.data[0].get('slack_webhook'):
         return

    webhook_url = org_res.data[0]['slack_webhook']
    
    payload = {
        "text": f"🔮 *ORACLE SIGNAL DETECTED*\n*Signal:* {signal_text}\n*Intent:* {intent_score}%\n*Lead:* <https://datavault.app/results/{result_id}|View in Vault>"
    }
    
    async with httpx.AsyncClient() as client:
        await client.post(webhook_url, json=payload)
