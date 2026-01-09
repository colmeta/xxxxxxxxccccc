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

        # Batch Insert
        res = supabase.table('jobs').insert(jobs_to_insert).execute()
        
        return {
            "status": "success", 
            "message": f"Successfully queued {len(jobs_to_insert)} verification jobs.",
            "jobs_created": len(jobs_to_insert)
        }
    except Exception as e:
        print(f"❌ CSV upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
async def create_bulk_jobs(
    queries: list[str],
    platform: str = "linkedin",
    user: dict = Depends(get_current_user)
):
    """
    Create multiple jobs from a list of queries (for BulkMissionControl paste input).
    Accepts JSON body with array of query strings.
    """
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    if not queries or len(queries) == 0:
        raise HTTPException(status_code=400, detail="No queries provided")
    
    jobs_to_insert = []
    user_id = user.get("id")
    org_id = user.get("org_id")
    
    for query in queries:
        if not query or not query.strip():
            continue
            
        jobs_to_insert.append({
            "user_id": user_id,
            "org_id": org_id,
            "target_query": query.strip(),
            "target_platform": platform,
            "compliance_mode": "standard",
            "status": "queued",
            "ab_test_group": "A"
        })
    
    if not jobs_to_insert:
        raise HTTPException(status_code=400, detail="No valid queries provided")
    
    try:
        res = supabase.table('jobs').insert(jobs_to_insert).execute()
        
        return {
            "status": "success",
            "message": f"Created {len(jobs_to_insert)} missions",
            "count": len(jobs_to_insert)
        }
    except Exception as e:
        print(f"❌ Bulk create failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audit")
async def audit_csv(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """
    REALITY CHECK - CLARITY PEARL AUDIT
    Specialized upload for existing lead lists to verify accuracy.
    Now with intelligent delimiter sniffing and header mapping.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
        
    content = await file.read()
    supabase = get_supabase()
    
    try:
        # Detect delimiter
        text_content = content.decode('utf-8')
        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(text_content[:2048])
        except Exception:
            dialect = 'excel' # Fallback
            
        f = io.StringIO(text_content)
        reader = csv.DictReader(f, dialect=dialect)
        
        jobs_to_insert = []
        user_id = user.get("id")
        org_id = user.get("org_id")
        
        for row in reader:
            # Flexible Header Mapping
            target = (
                row.get('LinkedIn URL') or 
                row.get('Contact LinkedIn URL') or 
                row.get('linkedin_url') or 
                row.get('url')
            )
            
            if not target:
                # Try Name + Company combination
                first = row.get('First Name') or row.get('first_name') or row.get('FirstName') or ''
                last = row.get('Last Name') or row.get('last_name') or row.get('LastName') or ''
                name = f"{first} {last}".strip()
                
                company = (
                    row.get('Company') or 
                    row.get('Account Name') or 
                    row.get('company_name') or 
                    row.get('Organization')
                )
                
                if name and company:
                    target = f"{name} at {company}"
                elif company:
                    target = company
                elif name:
                    target = name
            
            if not target:
                continue
                
            jobs_to_insert.append({
                "user_id": user_id,
                "org_id": org_id,
                "target_query": target,
                "target_platform": "linkedin" if "linkedin.com" in str(target) else "generic", 
                "compliance_mode": "strict",
                "status": "queued",
                "ab_test_group": "A",
                "search_metadata": {
                    "audit_mode": True, 
                    "original_record": row,
                    "source": "reality_check_v2"
                }
            })
            
        if not jobs_to_insert:
             raise HTTPException(status_code=400, detail="No valid leads found for audit. Please ensure headers like 'LinkedIn URL' or 'First Name', 'Last Name', and 'Company' are present.")

        # Batch insert for performance
        supabase.table('jobs').insert(jobs_to_insert).execute()
        
        return {
            "status": "success", 
            "message": f"Reality Check Initialized. Auditing {len(jobs_to_insert)} leads.",
            "leads_audited": len(jobs_to_insert)
        }

    except Exception as e:
        print(f"❌ Audit upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Audit Process Failed: {str(e)}")
