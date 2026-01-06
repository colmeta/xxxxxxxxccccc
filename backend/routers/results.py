from fastapi import APIRouter, Depends, HTTPException
from backend.dependencies import get_current_user
from backend.services.supabase_client import get_supabase
from typing import List, Dict, Any
import csv
import io
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/results", tags=["Results"])

@router.get("/stats")
def get_global_stats(user: dict = Depends(get_current_user)):
    """
    Returns global scraping statistics for the dashboard.
    """
    supabase = get_supabase()
    if not supabase:
        return {"total_leads": 0, "verified_leads": 0, "success_rate": 0, "avg_clarity": 0}

    try:
        # 1. Total Count
        # Using exact=True to get count without fetching all rows
        res_total = supabase.table('results').select("id", count="exact").execute()
        total = res_total.count if res_total.count else 0
        
        # 2. Verified Count
        res_verified = supabase.table('results').select("id", count="exact").eq('verified', True).execute()
        verified = res_verified.count if res_verified.count else 0
        
        # 3. Clarity Score Avg (Simple approach: fetch last 1000 and avg)
        # Supabase doesn't support aggregate avg via API easily without RPC, so we'll do a sample approximation
        res_sample = supabase.table('results').select("clarity_score").order('created_at', desc=True).limit(500).execute()
        scores = [r['clarity_score'] for r in res_sample.data if r['clarity_score'] is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        success_rate = (verified / total * 100) if total > 0 else 0
        
        return {
            "total_leads": total,
            "verified_leads": verified,
            "success_rate": round(success_rate, 1),
            "avg_clarity": round(avg_score, 1)
        }
    except Exception as e:
        print(f"Stats Error: {e}")
        return {"total_leads": 0, "verified_leads": 0, "success_rate": 0, "avg_clarity": 0}

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
@router.get("/export/{job_id}/")
async def export_job_results(job_id: str, user: dict = Depends(get_current_user)):
    """
    THE FORGE: Export job results to CSV.
    """
    supabase = get_supabase()
    res = supabase.table('results').select("*").eq('job_id', job_id).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="No results found to export")
        
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=res.data[0]['data_payload'].keys())
    writer.writeheader()
    
    for r in res.data:
        writer.writerow(r['data_payload'])
        
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=scout_export_{job_id}.csv"}
    )
