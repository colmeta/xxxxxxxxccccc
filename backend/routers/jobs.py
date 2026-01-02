import os
from fastapi import APIRouter, Depends, HTTPException
from backend.schemas import JobRequest, JobResponse, JobStatusResponse
from backend.dependencies import get_current_user
from backend.services.supabase_client import get_supabase

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.post("/", response_model=JobResponse)
def create_job(job: JobRequest, user: dict = Depends(get_current_user)):
    """
    Receives a Job from the User/Dashboard and writes to 'jobs' table.
    Deducts 1 credit from user's account.
    """
    supabase = get_supabase()
    
    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable. Please try again later."
        )

    # Insert into 'jobs' table
    try:
        # Extract user_id from the user object returned by auth
        user_id = user.get("id")
        
        # Check user credits first
        profile_res = supabase.table('profiles').select('credits_remaining').eq('id', user_id).execute()
        
        if not profile_res.data or len(profile_res.data) == 0:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        credits = profile_res.data[0].get('credits_remaining', 0)
        
        if credits < 1:
            raise HTTPException(status_code=402, detail="Insufficient credits. Please upgrade your plan.")
        
        # Deduct credit
        supabase.table('profiles').update({'credits_remaining': credits - 1}).eq('id', user_id).execute()
        
        # Create job data
        data = {
            "user_id": user_id, 
            "target_query": job.query,
            "target_platform": job.platform,
            "compliance_mode": job.compliance_mode,
            "status": "queued"  # Fixed: was 'pending', now matches DB enum
        }
        
        # Insert job
        res = supabase.table('jobs').insert(data).execute()
        
        # Check if we got data back
        if res.data and len(res.data) > 0:
            job_id = res.data[0]['id']
        else:
            # Fallback if no data returned (shouldn't happen on successful insert)
            job_id = "unknown_id"

        return JobResponse(
            job_id=job_id,
            status="queued",
            message=f"Job accepted: {job.query}. {credits - 1} credits remaining."
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 402, 404)
        raise
    except Exception as e:
        # Security: Log error type only, not the full message which may contain PII
        error_type = type(e).__name__
        print(f"⚠️  Job creation failed: {error_type}")
        raise HTTPException(status_code=500, detail="Database operation failed. Please contact support.")

@router.get("/{job_id}/", response_model=JobStatusResponse)
def get_job_status(job_id: str, user: dict = Depends(get_current_user)):
    """
    Check the status of a specific job.
    """
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable."
        )
        
    try:
        res = supabase.table('jobs').select("*").eq('id', job_id).execute()
        if not res.data:
             raise HTTPException(status_code=404, detail="Job not found")
        
        job_data = res.data[0]
        return JobStatusResponse(
            job_id=job_id, 
            status=job_data.get("status", "unknown"),
            progress=job_data.get("progress_message", "Processing..."), # Assuming a progress_message column or similar
            data=job_data
        )
    except Exception as e:
        # Security: Sanitized error logging
        error_type = type(e).__name__
        print(f"⚠️  Job status fetch failed: {error_type}")
        # If it's the 404 from above, re-raise
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Failed to retrieve job status. Please try again.")
