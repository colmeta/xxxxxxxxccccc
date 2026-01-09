from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.dependencies import get_current_user
from backend.services.supabase_client import get_supabase
import uuid

router = APIRouter(prefix="/api/organizations", tags=["Organizations"])

class CreateOrgRequest(BaseModel):
    name: str
    description: str = ""

@router.post("/create")
async def create_organization(req: CreateOrgRequest, user: dict = Depends(get_current_user)):
    """
    Create a new organization for the authenticated user.
    """
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    user_id = user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User identification failed")
    
    try:
        # Create organization
        org_data = {
            "id": str(uuid.uuid4()),
            "name": req.name,
            "owner_id": user_id,
            "credits_monthly": 1000,  # Default credits
            "credits_used": 0
        }
        
        org_res = supabase.table('organizations').insert(org_data).execute()
        if not org_res.data:
            raise HTTPException(status_code=500, detail="Failed to create organization")
        
        org_id = org_res.data[0]['id']
        
        # Create membership
        membership_data = {
            "org_id": org_id,
            "user_id": user_id,
            "role": "owner"
        }
        supabase.table('memberships').insert(membership_data).execute()
        
        # Update user's active org
        supabase.table('profiles').upsert({
            "id": user_id,
            "active_org_id": org_id
        }).execute()
        
        return {
            "success": True,
            "organization": org_res.data[0],
            "message": "Organization created successfully"
        }
        
    except Exception as e:
        print(f"Organization creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create organization")


@router.post("/auto-setup")
async def auto_setup_organization(user: dict = Depends(get_current_user)):
    """
    Automatically create a personal organization for users who don't have one.
    """
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    user_id = user.get("id")
    email = user.get("email", "user")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User identification failed")
    
    # Check if user already has an organization
    existing_org = user.get("org_id")
    if existing_org:
        return {
            "success": True,
            "message": "Organization already exists",
            "org_id": existing_org
        }
    
    try:
        # Create personal organization
        org_name = f"{email.split('@')[0]}'s Workspace"
        org_data = {
            "id": str(uuid.uuid4()),
            "name": org_name,
            "owner_id": user_id,
            "credits_monthly": 1000,
            "credits_used": 0
        }
        
        org_res = supabase.table('organizations').insert(org_data).execute()
        if not org_res.data:
            raise HTTPException(status_code=500, detail="Auto-setup failed")
        
        org_id = org_res.data[0]['id']
        
        # Create membership
        membership_data = {
            "org_id": org_id,
            "user_id": user_id,
            "role": "owner"
        }
        supabase.table('memberships').insert(membership_data).execute()
        
        # Update profile
        supabase.table('profiles').upsert({
            "id": user_id,
            "active_org_id": org_id
        }).execute()
        
        return {
            "success": True,
            "organization": org_res.data[0],
            "message": "Personal workspace created automatically",
            "org_id": org_id
        }
        
    except Exception as e:
        print(f"Auto-setup error: {e}")
        raise HTTPException(status_code=500, detail="Auto-setup failed")


@router.get("/my-orgs")
async def get_my_organizations(user: dict = Depends(get_current_user)):
    """
    Get all organizations the authenticated user belongs to.
    """
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    user_id = user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User identification failed")
    
    try:
        # Get all organizations via memberships
        memberships = supabase.table('memberships').select(
            'org_id, role, organizations(*)'
        ).eq('user_id', user_id).execute()
        
        return {
            "organizations": memberships.data if memberships.data else [],
            "active_org_id": user.get("org_id")
        }
        
    except Exception as e:
        print(f"Error fetching organizations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch organizations")
