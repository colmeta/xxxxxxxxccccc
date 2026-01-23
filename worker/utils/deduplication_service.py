"""
CLARITY PEARL - DEDUPLICATION SERVICE
Prevents duplicate lead delivery to maintain client trust.
"""

import hashlib
import re
from typing import Dict, List, Optional, Tuple
from supabase import Client

class DeduplicationService:
    """Central service for preventing duplicate lead delivery."""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    def normalize_company(self, company_name: str, company_domain: Optional[str] = None) -> str:
        """
        Create consistent hash for company matching.
        
        Args:
            company_name: Company name from data
            company_domain: Website domain (optional)
        
        Returns:
            MD5 hash for consistent matching
        """
        # Normalize name: lowercase, remove punctuation, collapse spaces
        if not company_name:
            company_name = "unknown"
        
        normalized_name = company_name.lower().strip()
        normalized_name = re.sub(r'[^a-z0-9\s]', '', normalized_name)
        normalized_name = re.sub(r'\s+', ' ', normalized_name)
        
        # Normalize domain: remove protocol, www, path
        normalized_domain = ""
        if company_domain:
            normalized_domain = company_domain.lower()
            normalized_domain = re.sub(r'^(https?://)?(www\.)?', '', normalized_domain)
            normalized_domain = re.sub(r'/.*$', '', normalized_domain)  # remove path
        
        # Create hash
        combined = f"{normalized_name}|{normalized_domain}"
        company_hash = hashlib.md5(combined.encode()).hexdigest()
        
        return company_hash
    
    def is_duplicate(self, org_id: str, company_name: str, company_domain: Optional[str], category: str) -> bool:
        """
        Check if company was already delivered to this org in this category.
        
        Args:
            org_id: Organization ID
            company_name: Company name to check
            company_domain: Company website
            category: Search category (e.g., "SaaS CEOs")
        
        Returns:
            True if company already delivered, False otherwise
        """
        try:
            company_hash = self.normalize_company(company_name, company_domain)
            
            # Check delivered_leads table
            response = self.supabase.table('delivered_leads').select('id').eq('org_id', org_id).eq('company_identifier', company_hash).eq('category', category).limit(1).execute()
            
            return len(response.data) > 0
        except Exception as e:
            print(f"⚠️ Duplicate check failed: {e}")
            return False  # On error, allow (better to have duplicate than miss lead)
    
    def mark_delivered(self, org_id: str, job_id: str, category: str, delivery_method: str = 'csv_export') -> int:
        """
        Mark all results from a job as delivered.
        
        Args:
            org_id: Organization ID
            job_id: Job ID to mark as delivered
            category: Category of the search
            delivery_method: How leads were delivered
        
        Returns:
            Number of leads marked as delivered
        """
        try:
            # Call database function
            response = self.supabase.rpc('fn_mark_as_delivered', {
                'p_org_id': org_id,
                'p_job_id': job_id,
                'p_category': category,
                'p_delivery_method': delivery_method
            }).execute()
            
            count = response.data if response.data else 0
            print(f"✅ Marked {count} leads as delivered (Category: {category})")
            return count
        except Exception as e:
            print(f"❌ Failed to mark as delivered: {e}")
            return 0
    
    def get_category_stats(self, org_id: str, category: Optional[str] = None) -> List[Dict]:
        """
        Get delivery statistics per category.
        
        Args:
            org_id: Organization ID
            category: Optional category filter
        
        Returns:
            List of stats per category
        """
        try:
            response = self.supabase.rpc('fn_get_category_stats', {
                'p_org_id': org_id,
                'p_category': category
            }).execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️ Failed to get category stats: {e}")
            return []
    
    def filter_duplicates(self, org_id: str, leads: List[Dict], category: str) -> Tuple[List[Dict], int]:
        """
        Filter out already-delivered leads from a list.
        
        Args:
            org_id: Organization ID
            leads: List of lead dictionaries
            category: Search category
        
        Returns:
            Tuple of (filtered_leads, duplicate_count)
        """
        filtered = []
        duplicate_count = 0
        
        for lead in leads:
            company_name = lead.get('name') or lead.get('company') or lead.get('decision_maker_name')
            company_domain = lead.get('website') or lead.get('source_url')
            
            if self.is_duplicate(org_id, company_name, company_domain, category):
                duplicate_count += 1
                print(f"   🔄 Skipping duplicate: {company_name}")
            else:
                filtered.append(lead)
        
        if duplicate_count > 0:
            print(f"📊 Filtered out {duplicate_count} duplicates, {len(filtered)} new leads")
        
        return filtered, duplicate_count
    
    def auto_detect_category(self, query: str) -> str:
        """
        Auto-detect category from search query using keywords.
        
        Args:
            query: Search query string
        
        Returns:
            Detected category or "Uncategorized"
        """
        query_lower = query.lower()
        
        # Category detection patterns
        patterns = {
            "SaaS Companies": ["saas", "software", "cloud", "platform"],
            "C-Level Executives": ["ceo", "founder", "cto", "cfo", "coo", "executive"],
            "Marketing Agencies": ["marketing", "agency", "advertising", "digital marketing"],
            "Real Estate": ["real estate", "realtor", "property", "broker"],
            "Food & Beverage": ["restaurant", "cafe", "food", "catering"],
            "Healthcare": ["doctor", "clinic", "hospital", "medical"],
            "Finance": ["financial", "accounting", "investment", "banking"],
            "E-commerce": ["ecommerce", "shopify", "online store", "retail"]
        }
        
        for category, keywords in patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return "Uncategorized"
    
    def get_delivery_history(self, org_id: str, limit: int = 50) -> List[Dict]:
        """
        Get recent delivery history for an organization.
        
        Args:
            org_id: Organization ID
            limit: Max number of deliveries to return
        
        Returns:
            List of delivery records
        """
        try:
            response = self.supabase.table('delivered_leads').select('*').eq('org_id', org_id).order('delivered_at', desc=True).limit(limit).execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️ Failed to get delivery history: {e}")
            return []


# Singleton instance
_dedup_service = None

def get_dedup_service(supabase: Client = None) -> DeduplicationService:
    """Get or create deduplication service singleton."""
    global _dedup_service
    if _dedup_service is None and supabase:
        _dedup_service = DeduplicationService(supabase)
    return _dedup_service
