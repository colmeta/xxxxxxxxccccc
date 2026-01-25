import asyncio
import re
import urllib.parse
import json
from scrapers.base_dork_engine import BaseDorkEngine

class B2BPlatformEngine:
    """
    CLARITY PEARL - B2B CORE HUB ENGINE
    Targeting high-trust platforms: Clutch, G2, Crunchbase, Wellfound.
    Provides "Social Proof" and "Capital" intelligence.
    """
    def __init__(self, page):
        self.page = page
        self.dork_engine = BaseDorkEngine(page, "b2b_hubs")

    async def scrape_clutch(self, company_name):
        """
        Extracts Agency metadata from Clutch.co.
        Signal: Project sizes, ratings, employee verification.
        """
        print(f"[B2B Engine] 🔍 Probing Clutch.co for '{company_name}'...")
        query = f'site:clutch.co/profile "{company_name}"'
        results = await self.dork_engine.run_dork_search(query, "")
        
        if not results: return None
        
        # Take best match
        best_match = results[0]
        snippet = best_match.get('snippet', '')
        
        # Regex extraction from G-Snippet
        rating = re.search(r'([\d\.]+)\s+stars', snippet, re.I)
        projects = re.search(r'\$(\d+,?\d+)\+', snippet)
        team_size = re.search(r'(\d+\s*-\s*\d+)\s+employees', snippet, re.I)
        
        return {
            "clutch_url": best_match.get('source_url'),
            "clutch_rating": rating.group(1) if rating else None,
            "min_project_size": projects.group(0) if projects else None,
            "team_size_clutch": team_size.group(1) if team_size else None,
            "verified_on_clutch": True
        }

    async def scrape_g2(self, product_name):
        """
        Extracts SaaS metadata from G2.com.
        Signal: Market segment (SMB/Mid/Ent), satisfaction scores.
        """
        print(f"[B2B Engine] 🔍 Probing G2 for '{product_name}'...")
        query = f'site:g2.com/products "{product_name}" reviews'
        results = await self.dork_engine.run_dork_search(query, "")
        
        if not results: return None
        
        best_match = results[0]
        snippet = best_match.get('snippet', '')
        
        rating = re.search(r'Rating:\s+([\d\.]+)/5', snippet)
        reviews_count = re.search(r'([\d,]+)\s+reviews', snippet, re.I)
        
        return {
            "g2_url": best_match.get('source_url'),
            "g2_rating": rating.group(1) if rating else None,
            "g2_review_count": reviews_count.group(1) if reviews_count else None,
            "category_g2": "SaaS / Software"
        }

    async def scrape_crunchbase(self, company_name):
        """
        Extracts Funding metadata from Crunchbase.
        Signal: Funding stage, Total raised, Lead investors.
        """
        print(f"[B2B Engine] 🔍 Probing Crunchbase for '{company_name}'...")
        query = f'site:crunchbase.com/organization "{company_name}" funding'
        results = await self.dork_engine.run_dork_search(query, "")
        
        if not results: return None
        
        best_match = results[0]
        snippet = best_match.get('snippet', '')
        
        funding_round = re.search(r'(Series [A-Z]|Seed|Pre-seed|Late Stage|Debt)', snippet, re.I)
        total_raised = re.search(r'raised\s+\$?([\d\.]+[MB])', snippet, re.I)
        
        return {
            "crunchbase_url": best_match.get('source_url'),
            "funding_stage": funding_round.group(1) if funding_round else "Stealth/Unknown",
            "total_funding": total_raised.group(1) if total_raised else None,
            "capital_signal": "HIGH" if total_raised else "MODERATE"
        }

    async def scrape_wellfound(self, company_name):
        """
        Extracts Startup metadata from Wellfound (AngelList).
        Signal: Hiring status, team velocity.
        """
        print(f"[B2B Engine] 🔍 Probing Wellfound for '{company_name}'...")
        query = f'site:wellfound.com/company "{company_name}"'
        results = await self.dork_engine.run_dork_search(query, "")
        
        if not results: return None
        
        best_match = results[0]
        snippet = best_match.get('snippet', '')
        
        hiring = "hiring" in snippet.lower() or "jobs" in snippet.lower()
        team_size = re.search(r'(\d+[\+-]?\d*)\s+people', snippet, re.I)

        return {
            "wellfound_url": best_match.get('source_url'),
            "wellfound_team_size": team_size.group(1) if team_size else None,
            "actively_hiring": hiring,
            "startup_signal": True
        }

    async def unified_b2b_enrich(self, lead):
        """
        Parallel enrichment for a single lead across all B2B hubs.
        """
        name = lead.get('name')
        if not name: return lead
        
        tasks = [
            self.scrape_clutch(name),
            self.scrape_g2(name),
            self.scrape_crunchbase(name),
            self.scrape_wellfound(name)
        ]
        
        intel_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge valid results
        for res in intel_results:
            if res and isinstance(res, dict):
                lead.update(res)
        
        return lead
