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
    
    # If Supabase is not configured (e.g. local dev without env vars), fallback to mock in dev
    if not supabase:
        print("⚠️ Supabase not connected. Allowing mock user for DEV only.")
        return {"id": "mock_user_id_from_token", "email": "dev@mock.com"} 

    try:
        # REAL AUTHENTICATION
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid Authentication Token")
        
        # Standardize response: always return dict with 'id' key
        user = user_response.user
        return {
            "id": user.id,
            "email": getattr(user, 'email', None),
            "raw": user  # Keep original for debugging if needed
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication Failed: {str(e)}")
