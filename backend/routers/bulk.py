from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from backend.services.supabase_client import get_supabase
from backend.dependencies import get_current_user
import csv
import io
import gc

router = APIRouter(prefix="/api/bulk", tags=["Bulk Operations"])

MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB Limit

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """
    Accepts a CSV file with a 'query' or 'website' column.
    Creates scraping/verification jobs for each row.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
        
    # Check Content-Length if available
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max size is 5MB.")

    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=503, detail="Database unavailable")

    content = await file.read()
    
    if len(content) > MAX_FILE_SIZE:
         raise HTTPException(status_code=413, detail="File too large. Max size is 5MB.")

    try:
        # Decode bytes to string
        text_content = content.decode('utf-8')
        f = io.StringIO(text_content)
        # Free up the raw byte memory immediately
        del content
        gc.collect() 
        
        reader = csv.DictReader(f)
        
        jobs_to_insert = []
        user_id = user.get("id")
        
        # Validate CSV headers
        if not reader.fieldnames or ('query' not in reader.fieldnames and 'website' not in reader.fieldnames):
             raise HTTPException(status_code=400, detail="CSV must have a 'query' or 'website' column")

        for row in reader:
            # Determine query target
            target = row.get('query') or row.get('website')
            if not target:
                continue
                
            jobs_to_insert.append({
                "user_id": user_id,
                "org_id": user.get("org_id"),
                "target_query": target,
                "target_platform": "generic", # default
                "compliance_mode": "standard",
                "status": "queued",
                "ab_test_group": "A" # Default to Control group
            })
            
        if not jobs_to_insert:
             raise HTTPException(status_code=400, detail="No valid rows found in CSV")

        # Batch Insert (Supabase/PostgREST supports list insert)
        # Note: Large files might need chunking, but for MVP <1000 rows this is fine.
        res = supabase.table('jobs').insert(jobs_to_insert).execute()
        
        return {
            "status": "success", 
            "message": f"Successfully queued {len(jobs_to_insert)} verification jobs.",
            "jobs_created": len(jobs_to_insert)
        }

@router.post("/audit")
async def audit_csv(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """
    REALITY CHECK - APOLLO/ZOOMINFO AUDIT
    Specialized upload for existing lead lists to verify accuracy.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
        
    content = await file.read()
    supabase = get_supabase()
    
    try:
        text_content = content.decode('utf-8')
        f = io.StringIO(text_content)
        reader = csv.DictReader(f)
        
        jobs_to_insert = []
        user_id = user.get("id")
        
        # Apollo standard header is often 'First Name', 'Last Name', 'Company', 'Email'
        # or exactly 'LinkedIn URL'
        for row in reader:
            # Priority 1: LinkedIn URL (Most accurate for verification)
            # Priority 2: Full Name + Company
            target = row.get('LinkedIn URL') or row.get('Contact LinkedIn URL')
            if not target:
                name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                company = row.get('Company') or row.get('Account Name')
                if name and company:
                    target = f"{name} at {company}"
            
            if not target:
                continue
                
            jobs_to_insert.append({
                "user_id": user_id,
                "org_id": user.get("org_id"),
                "target_query": target,
                "target_platform": "linkedin", # Force LinkedIn for audit accuracy
                "compliance_mode": "strict",
                "status": "queued",
                "ab_test_group": "A",
                "search_metadata": {"audit_mode": True, "original_record": row}
            })
            
        if not jobs_to_insert:
             raise HTTPException(status_code=400, detail="No valid leads found for audit. Ensure headers like 'LinkedIn URL' or 'First Name' exist.")

        supabase.table('jobs').insert(jobs_to_insert).execute()
        
        return {
            "status": "success", 
            "message": f"Reality Check Initialized. Auditing {len(jobs_to_insert)} leads.",
            "leads_audited": len(jobs_to_insert)
        }

    except Exception as e:
        print(f"❌ Audit upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
