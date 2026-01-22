from backend.services.supabase_client import get_supabase
from backend.dependencies import get_current_user
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional

router = APIRouter(prefix="/api/campaigns", tags=["Outreach Campaigns"])

@router.post("/")
async def create_campaign(
    name: str = Body(..., embed=True),
    description: Optional[str] = Body(None, embed=True),
    user: dict = Depends(get_current_user)
):
    """
    Creates a new Outreach Campaign.
    """
    supabase = get_supabase()
    org_id = user.get("org_id")
    
    res = supabase.table('outreach_campaigns').insert({
        "org_id": org_id,
        "name": name,
        "description": description,
        "status": "active"
    }).execute()
    
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to create campaign")
        
    return res.data[0]

@router.post("/{campaign_id}/sequences")
async def add_sequence_step(
    campaign_id: str,
    subject: str = Body(..., embed=True),
    body: str = Body(..., embed=True),
    step_order: int = Body(..., embed=True),
    delay_days: int = Body(2, embed=True),
    user: dict = Depends(get_current_user)
):
    """
    Adds a personalized step to an outreach sequence.
    """
    supabase = get_supabase()
    
    res = supabase.table('outreach_sequences').insert({
        "campaign_id": campaign_id,
        "step_order": step_order,
        "template_subject": subject,
        "template_body": body,
        "delay_days": delay_days
    }).execute()
    
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to add sequence step")
        
    return res.data[0]

@router.get("/")
async def list_campaigns(user: dict = Depends(get_current_user)):
    """
    Lists all campaigns for the user's organization.
    """
    supabase = get_supabase()
    org_id = user.get("org_id")
    
    res = supabase.table('outreach_campaigns').select("*, outreach_sequences(*)").eq('org_id', org_id).execute()
    return res.data

@router.post("/enroll/{campaign_id}/{lead_id}")
async def enroll_lead(campaign_id: str, lead_id: str, user: dict = Depends(get_current_user)):
    """
    Manually enrolls a lead into a campaign sequence.
    """
    supabase = get_supabase()
    
    # 1. Find the first step of the campaign
    first_step = supabase.table('outreach_sequences').select("*")\
        .eq('campaign_id', campaign_id)\
        .order('step_order')\
        .limit(1).execute()
        
    if not first_step.data:
        raise HTTPException(status_code=400, detail="Campaign has no sequences defined")
        
    # 2. Create the first log entry (scheduled for now)
    res = supabase.table('outreach_logs').insert({
        "lead_id": lead_id,
        "sequence_step_id": first_step.data[0]['id'],
        "status": "pending",
        "scheduled_at": "now()"
    }).execute()
    
    return {"status": "enrolled", "log_id": res.data[0]['id']}
