from pydantic import BaseModel
from typing import Optional, Any, Dict

class JobRequest(BaseModel):
    query: str
    platform: str = "linkedin" # 'linkedin' or 'google_maps'
    compliance_mode: str = "standard" 

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
