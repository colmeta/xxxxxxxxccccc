"""
CLARITY PEARL - DELIVERY TRACKING API
Endpoints for marking jobs as delivered and tracking delivery history.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.dependencies import get_current_user
from backend.services.supabase_client import get_supabase

router = APIRouter(prefix="/api/deliveries", tags=["deliveries"])

class MarkDeliveredRequest(BaseModel):
    job_id: str
    category: Optional[str] = None
    delivery_method: str = "csv_export"

class DeliveryHistoryResponse(BaseModel):
    id: str
    company_name: str
    category: str
    delivered_at: str
    delivery_method: str

@router.post("/mark")
async def mark_job_delivered(
    request: MarkDeliveredRequest,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    """Mark all results from a job as delivered to prevent future duplicates."""
    
    # Get user's organization
    org_id = user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="No organization found for user")
    
    # Get job details
    job_response = supabase.table('jobs').select('*').eq('id', request.job_id).eq('user_id', user['id']).single().execute()
    
    if not job_response.data:
        raise HTTPException(status_code=404, detail="Job not found or access denied")
    
    job = job_response.data
    
    # Use provided category or auto-detect
    category = request.category or job.get('category') or job.get('target_query', 'Uncategorized')
    
    try:
        # Call database function to mark as delivered
        result = supabase.rpc('fn_mark_as_delivered', {
            'p_org_id': org_id,
            'p_job_id': request.job_id,
            'p_category': category,
            'p_delivery_method': request.delivery_method
        }).execute()
        
        count = result.data if result.data else 0
        
        return {
            "success": True,
            "delivered_count": count,
            "category": category,
            "job_id": request.job_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark as delivered: {str(e)}")

@router.get("/history")
async def get_delivery_history(
    limit: int = 50,
    category: Optional[str] = None,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    """Get delivery history for the user's organization."""
    
    org_id = user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="No organization found for user")
    
    try:
        query = supabase.table('delivered_leads').select('*').eq('org_id', org_id).order('delivered_at', desc=True).limit(limit)
        
        if category:
            query = query.eq('category', category)
        
        response = query.execute()
        
        return {
            "success": True,
            "deliveries": response.data,
            "count": len(response.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get delivery history: {str(e)}")

@router.get("/stats")
async def get_delivery_stats(
    category: Optional[str] = None,
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    """Get delivery statistics per category."""
    
    org_id = user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="No organization found for user")
    
    try:
        result = supabase.rpc('fn_get_category_stats', {
            'p_org_id': org_id,
            'p_category': category
        }).execute()
        
        return {
            "success": True,
            "stats": result.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/categories")
async def get_categories(
    user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    """Get list of unique categories for this organization."""
    
    org_id = user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="No organization found for user")
    
    try:
        response = supabase.table('delivered_leads').select('category').eq('org_id', org_id).execute()
        
        # Get unique categories
        categories = list(set(item['category'] for item in response.data if item.get('category')))
        categories.sort()
        
        return {
            "success": True,
            "categories": categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")
