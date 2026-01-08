from pydantic import BaseModel, validator, Field
from typing import Optional, Any, Dict, Literal

class JobRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500, description="Search query (3-500 characters)")
    platform: Literal[
        "linkedin", "google_news", "amazon", "real_estate", 
        "job_scout", "reddit", "tiktok", "facebook", "google_maps", "generic"
    ] = Field(default="linkedin", description="Target platform")
    compliance_mode: Literal["standard", "strict", "gdpr"] = Field(default="standard", description="Compliance level")
    priority: int = Field(default=1, ge=1, le=10, description="Job priority (1-10)")
    ab_test_group: Literal["A", "B", "C"] = Field(default="A", description="A/B Testing Group (A=Google, B=Direct, C=Mobile Swarm)")
    channel_priority: Optional[List[Literal["email", "dm", "call"]]] = Field(default=["email", "dm"], description="Preferred contact channels")
    search_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional search context")
    
    @validator('query')
    def validate_query(cls, v):
        """Ensure query is sanitized and reasonable."""
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty or whitespace only")
        # Basic SQL injection prevention (though we use prepared statements, defense in depth)
        dangerous_chars = ["';", "--", "/*", "*/", "xp_", "sp_"]
        if any(char in v.lower() for char in dangerous_chars):
            raise ValueError("Query contains potentially dangerous characters")
        return v

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    truth_score: Optional[int] = None
    verdict: Optional[str] = None
