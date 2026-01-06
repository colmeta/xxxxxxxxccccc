from fastapi import APIRouter, Depends, HTTPException, Body
from backend.services.supabase_client import get_supabase
from backend.dependencies import get_current_user
from worker.utils.gemini_client import gemini_client
import json

router = APIRouter(prefix="/api/oracle", tags=["The Oracle"])

@router.post("/dispatch")
async def dispatch_mission(
    prompt: str = Body(..., embed=True), 
    user: dict = Depends(get_current_user)
):
    """
    THE ORACLE DISPATCHER
    Converts a NL prompt into a multi-job mission.
    """
    supabase = get_supabase()
    user_id = user.get("id")
    org_id = user.get("org_id")
    
    if not org_id:
         raise HTTPException(status_code=400, detail="Organization context missing.")

    print(f"🔮 The Oracle is interpreting mission: {prompt[:50]}...")
    
    # 1. Interpret Mission via Gemini
    jobs_to_create = await gemini_client.dispatch_mission(prompt)
    
    if not jobs_to_create:
         raise HTTPException(status_code=422, detail="The Oracle could not derive a mission from your prompt.")

    # 2. Verify Credits
    org_res = supabase.table('organizations').select('credits_monthly', 'credits_used').eq('id', org_id).execute()
    if not org_res.data:
         raise HTTPException(status_code=404, detail="Org not found.")
    
    org_data = org_res.data[0]
    available = org_data.get('credits_monthly', 0) - org_data.get('credits_used', 0)
    
    if available < len(jobs_to_create):
         raise HTTPException(status_code=402, detail=f"Insufficient credits for a {len(jobs_to_create)} step mission.")

    # 3. Deploy Mission
    created_jobs = []
    for job_info in jobs_to_create:
        payload = {
            "user_id": user_id,
            "org_id": org_id,
            "target_query": job_info.get("query"),
            "target_platform": job_info.get("platform", "generic"),
            "compliance_mode": job_info.get("compliance_mode", "standard"),
            "priority": 10 if job_info.get("boost") else 1,
            "status": "queued",
            "search_metadata": {"oracle_origin": True, "master_prompt": prompt}
        }
        res = supabase.table('jobs').insert(payload).execute()
        if res.data:
             created_jobs.append(res.data[0]['id'])

    # 4. Deduct Credits
    supabase.table('organizations').update({"credits_used": org_data['credits_used'] + len(jobs_to_create)}).eq('id', org_id).execute()

    return {
        "status": "success",
        "mission_id": created_jobs[0] if created_jobs else None,
        "steps_deployed": len(created_jobs),
        "interpretation": jobs_to_create
    }
