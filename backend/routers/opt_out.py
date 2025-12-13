from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from backend.services.supabase_client import get_supabase
import hashlib

router = APIRouter(prefix="/api/opt-out", tags=["Compliance"])

class OptOutRequest(BaseModel):
    hash: str
    type: str = "email"  # Keep for client compatibility (not stored in DB)

@router.post("/")
async def opt_out(fastapi_request: Request, request: OptOutRequest):
    """
    Receives a hashed email/phone from the Opt-Out Portal.
    Inserts it into the 'opt_out_registry' table with IP tracking.
    Existing schema: id (uuid), identifier_hash, request_ip_hash, requested_at
    """
    supabase = get_supabase()
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    if not request.hash or len(request.hash) != 64:
        raise HTTPException(status_code=400, detail="Invalid hash format")
    
    # Hash the client IP for privacy (abuse prevention)
    client_ip = fastapi_request.client.host if fastapi_request.client else "unknown"
    ip_hash = hashlib.sha256(client_ip.encode('utf-8')).hexdigest()
    
    try:
        # Insert into opt_out_registry table (matches existing Supabase schema)
        response = supabase.table('opt_out_registry').insert({
            'identifier_hash': request.hash,
            'request_ip_hash': ip_hash
            # requested_at auto-populates via database DEFAULT
        }).execute()
        
        return {
            "status": "success",
            "message": "Your request has been processed. The hash is now in the global blocklist.",
            "hash_preview": request.hash[:8] + "..."
        }
    except Exception as e:
        # Don't leak the full error (could contain sensitive info)
        print(f"⚠️ Opt-out error: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Failed to process request")
