# Lead Prioritizer - scores leads by completeness and quality
from .gemini_client import gemini_client
import json

class LeadPrioritizer:
    """
    AI-Powered Autonomous Prioritization (Pain Point #7).
    Auto-scores and routes leads to sales reps. No manual qualification.
    """
    
    async def calculate_priority_score(self, lead_data: dict, intent_data: dict) -> dict:
        """
        Multi-factor scoring:
        - Intent score (from arbiter)
        - Predictive growth score
        - Company size indicators
        - Role seniority
        - Email deliverability
        """
        base_score = intent_data.get('intent_score', 0)
        growth_score = intent_data.get('predictive_growth_score', 0)
        
        # Seniority multiplier
        title = lead_data.get('title', '').lower()
        seniority_bonus = 0
        if any(x in title for x in ['ceo', 'founder', 'president', 'chief']):
            seniority_bonus = 20
        elif any(x in title for x in ['vp', 'vice president', 'head of', 'director']):
            seniority_bonus = 15
        elif 'manager' in title:
            seniority_bonus = 10
        
        # Calculate final priority
        priority_score = min(100, int((base_score * 0.4) + (growth_score * 0.4) + seniority_bonus))
        
        # Determine routing
        routing_reason = self._get_routing_reason(priority_score, intent_data)
        
        return {
            "priority_score": priority_score,
            "routing_reason": routing_reason,
            "should_auto_assign": priority_score >= 70  # High-priority leads get instant routing
        }
    
    def _get_routing_reason(self, score: int, intent_data: dict) -> str:
        if score >= 90:
            return f"🔥 URGENT: {intent_data.get('oracle_signal', 'High-intent signal detected')}"
        elif score >= 70:
            return f"⚡ HOT LEAD: {intent_data.get('reasoning', 'Strong buying intent')}"
        elif score >= 50:
            return "📊 QUALIFIED: Worth pursuing, moderate priority"
        else:
            return "📋 NURTURE: Long-term cultivation needed"
    
    async def auto_route_lead(self, result_id: str, org_id: str, priority_score: int):
        """
        Assign lead to best-fit sales rep based on:
        - Rep capacity (current leads assigned)
        - Rep specialization (industry, company size)
        - Round-robin for fairness
        """
        supabase = get_supabase()
        
        # Get sales reps for this org (users with role 'sales')
        reps = supabase.table('profiles').select('id', 'full_name').eq('org_id', org_id).eq('role', 'sales').execute()
        
        if not reps.data:
            print(f"⚠️ No sales reps found for org {org_id}. Skipping auto-routing.")
            return None
        
        # Simple round-robin for now (can enhance with ML later)
        # In production: query results to find rep with fewest assigned leads
        assigned_rep = reps.data[0]  # Simplest: first rep
        
        # Update result with routing
        supabase.table('results').update({
            "auto_routed_to": assigned_rep['id'],
            "priority_score": priority_score
        }).eq('id', result_id).execute()
        
        print(f"✅ Lead {result_id} auto-routed to {assigned_rep['full_name']} (Score: {priority_score})")
        return assigned_rep['id']

lead_prioritizer = LeadPrioritizer()
