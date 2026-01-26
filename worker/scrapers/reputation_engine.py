import asyncio
import re
from scrapers.base_dork_engine import BaseDorkEngine

class ReputationEngine:
    """
    LAYER 2: TRUST & REPUTATION (ENHANCED)
    Extracts ratings and reviews from Capterra, TrustRadius, BBB, Glassdoor.
    Uses 'dorking' to find profiles without direct API costs.
    """
    
    def __init__(self, page):
        self.page = page
        self.dork_engine = BaseDorkEngine(page, "reputation_hunter")
        
    async def log(self, msg):
        print(f"   ⭐ [ReputationEngine] {msg}")

    async def scrape_software_reviews(self, company_name):
        """
        Scrapes Capterra / TrustRadius for SaaS reputation.
        """
        await self.log(f"Checking Software Reviews for '{company_name}'...")
        
        # Capterra Dork
        capterra_query = f'site:capterra.com/p "{company_name}" reviews'
        results = await self.dork_engine.run_dork_search(capterra_query, "")
        
        reputation_data = {}
        
        if results:
            best = results[0]
            snippet = best.get('snippet', '')
            rating_match = re.search(r'([\d\.]+)/5', snippet)
            reviews_match = re.search(r'(\d+)\s+reviews', snippet, re.I)
            
            reputation_data.update({
                "capterra_url": best.get('source_url'),
                "capterra_rating": rating_match.group(1) if rating_match else None,
                "capterra_reviews": reviews_match.group(1) if reviews_match else None
            })
            await self.log(f"Found Capterra: {reputation_data.get('capterra_rating')} stars")

        # TrustRadius Dork
        tr_query = f'site:trustradius.com/products "{company_name}" reviews'
        tr_results = await self.dork_engine.run_dork_search(tr_query, "")
        
        if tr_results:
            best = tr_results[0]
            reputation_data["trustradius_url"] = best.get('source_url')
            
        return reputation_data

    async def scrape_business_trust(self, company_name):
        """
        Scrapes BBB and Glassdoor for general business trust.
        """
        await self.log(f"Checking Business Trust Signals for '{company_name}'...")
        
        trust_data = {}
        
        # BBB Dork
        bbb_query = f'site:bbb.org/us "{company_name}"'
        bbb_results = await self.dork_engine.run_dork_search(bbb_query, "")
        
        if bbb_results:
            best = bbb_results[0]
            snippet = best.get('snippet', '')
            rating = re.search(r'Rating:\s+([A-F][\+\-]?)', snippet, re.I)
            
            trust_data.update({
                "bbb_url": best.get('source_url'),
                "bbb_rating": rating.group(1) if rating else "Not Accredited"
            })
            await self.log(f"Found BBB Rating: {trust_data.get('bbb_rating')}")

        # Glassdoor Dork (Employee sentiment = Trust signal)
        gd_query = f'site:glassdoor.com/Reviews "{company_name}"'
        gd_results = await self.dork_engine.run_dork_search(gd_query, "")
        
        if gd_results:
            best = gd_results[0]
            snippet = best.get('snippet', '')
            stars = re.search(r'([\d\.]+)\s+stars', snippet)
            
            trust_data.update({
                "glassdoor_url": best.get('source_url'),
                "employee_rating": stars.group(1) if stars else None
            })
            
        return trust_data

    async def scrape(self, query):
        """
        Main entry point.
        """
        company_name = query.replace("reviews", "").replace("rating", "").strip()
        await self.log(f"Starting Reputation Audit for: {company_name}")
        
        # 1. Software/SaaS Ratings
        software_rep = await self.scrape_software_reviews(company_name)
        
        # 2. General Trust Ratings
        trust_rep = await self.scrape_business_trust(company_name)
        
        combined = {**software_rep, **trust_rep}
        combined['layer'] = "Layer 2: Trust & Reputation"
        
        # Calculate Reliability Score (0-100)
        score = 50
        if combined.get('capterra_rating'): score += float(combined['capterra_rating']) * 5
        if combined.get('bbb_rating') in ['A+', 'A']: score += 20
        if combined.get('employee_rating'): score += float(combined['employee_rating']) * 4
        
        combined['calculated_trust_score'] = min(score, 100)
        
        await self.log(f"Audit complete. Trust Score: {combined['calculated_trust_score']}/100")
        
        # Wrap in list for consistency
        return [combined]
