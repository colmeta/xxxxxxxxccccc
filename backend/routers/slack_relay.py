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

async def send_oracle_alert(org_id, result_id, signal_text, intent_score, lead_data=None):
    """
    The Invisible Hand in action: Relays high-value Oracle signals to Slack with rich formatting.
    """
    supabase = get_supabase()
    org_res = supabase.table('organizations').select('slack_webhook', 'name').eq('id', org_id).execute()
    
    if not org_res.data or not org_res.data[0].get('slack_webhook'):
         return

    webhook_url = org_res.data[0]['slack_webhook']
    org_name = org_res.data[0].get('name', 'Your Lab')
    
    # Extract lead details
    name = lead_data.get('name') or lead_data.get('full_name') or "Unknown Lead"
    company = lead_data.get('company') or lead_data.get('organization') or "Unknown Entity"
    title = lead_data.get('title') or lead_data.get('position') or "N/A"
    
    # Progress bar for intent
    filled = int(intent_score / 10)
    bar = "🔵" * filled + "⚪" * (10 - filled)

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔮 ORACLE SIGNAL DETECTED",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Signal:* _{signal_text}_\n*Intent:* `{intent_score}%` {bar}\n*Entity:* *{name}* @ *{company}* ({title})"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View in DataVault",
                            "emoji": True
                        },
                        "url": f"https://datavault.app/results/{result_id}",
                        "style": "primary"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"🛡️ *Vault:* {org_name} | *Status:* Stealth Active"
                    }
                ]
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json=payload)
    except Exception as e:
        print(f"⚠️ Slack Relay Failed: {e}")
