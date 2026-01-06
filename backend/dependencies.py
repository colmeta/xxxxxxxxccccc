from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from typing import Optional
from backend.services.supabase_client import get_supabase

# --- AUTH MIDDLEWARE ---
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Decodes the JWT token from Supabase.
    Returns a standardized dict with 'id' key.
    """
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=403, detail="Invalid Auth")
    
    supabase: Optional[Client] = get_supabase()
    
    # Production Mode: Fail fast if Supabase is not configured
    if not supabase:
        raise HTTPException(
            status_code=503, 
            detail="Service temporarily unavailable. Database connection required."
        )

    try:
        # REAL AUTHENTICATION
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid Authentication Token")
        
        # Standardize response: always return dict with 'id' key
        user = user_response.user
        
        # 3. Fetch Organization Context
        profile_res = supabase.table('profiles').select('active_org_id').eq('id', user.id).execute()
        active_org_id = None
        if profile_res.data:
            active_org_id = profile_res.data[0].get('active_org_id')
        
        # If no active org, find the first one they belong to
        if not active_org_id:
            membership_res = supabase.table('memberships').select('org_id').eq('user_id', user.id).limit(1).execute()
            if membership_res.data:
                active_org_id = membership_res.data[0].get('org_id')
                # Update profile with this org
                supabase.table('profiles').upsert({"id": user.id, "active_org_id": active_org_id}).execute()

        return {
            "id": user.id,
            "email": getattr(user, 'email', None),
            "org_id": active_org_id,
            "raw": user
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication Failed: {str(e)}")
