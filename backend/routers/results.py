from fastapi import APIRouter, Depends, HTTPException
from backend.dependencies import get_current_user
from backend.services.supabase_client import get_supabase
from typing import List, Dict, Any

router = APIRouter(prefix="/api/results", tags=["Results"])

@router.get("/{job_id}/")
def get_job_results(job_id: str, user: dict = Depends(get_current_user)):
    """
    Fetch scraped data for a given job.
    """
    supabase = get_supabase()
    if not supabase:
        return {"message": "DB disconnected", "results": []}

    try:
        # Assuming a 'results' or 'leads' table linked by job_id
        # The Mvp spec mentions 'data' and 'provenance'.
        # We'll assume a table named 'results' for now as per the user prompt "api/results/{job_id}"
        
        res = supabase.table('results').select("*").eq('job_id', job_id).execute()
        
        return {
            "job_id": job_id,
            "count": len(res.data),
            "results": res.data
        }
    except Exception as e:
         print(f"DB Error: {e}")
         raise HTTPException(status_code=500, detail=f"Failed to fetch results: {str(e)}")
