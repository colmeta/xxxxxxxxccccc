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
        # 2. Extract Org ID from User
        org_id = user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="User is not associated with an organization. Please create or join one.")

        # 3. Check Org-Level Credits
        org_res = supabase.table('organizations').select('credits_monthly', 'credits_used').eq('id', org_id).execute()
        
        if not org_res.data or len(org_res.data) == 0:
            raise HTTPException(status_code=404, detail="Organization record not found")
        
        org_data = org_res.data[0]
        allowance = org_data.get('credits_monthly', 0)
        used = org_data.get('credits_used', 0)
        
        if (allowance - used) < 1:
            raise HTTPException(status_code=402, detail="Organization has exhausted monthly credits. Please upgrade your plan.")
        
        # 4. Deduct credit (Record usage)
        supabase.table('organizations').update({'credits_used': used + 1}).eq('id', org_id).execute()
        
        # 5. Create job data
        data = {
            "user_id": user_id, 
            "org_id": org_id,
            "target_query": job.query,
            "target_platform": job.platform,
            "compliance_mode": job.compliance_mode,
            "status": "queued"
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
            message=f"Job accepted for workspace. {allowance - used - 1} credits remaining."
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
