import asyncio
import re
from scrapers.base_dork_engine import BaseDorkEngine

class IntentSignalEngine:
    """
    CLARITY PEARL - INTENT SIGNAL ENGINE
    Mission: Capture high-velocity "buy" signals.
    Layer 5: Hiring (Headcount growth) & Advertising (Capital burn).
    """
    def __init__(self, page):
        self.page = page
        self.dork_engine = BaseDorkEngine(page, "intent_oracle")

    async def scrape_hiring_signals(self, company_name):
        """
        Dorks Indeed and LinkedIn Jobs.
        Signal: "We are hiring" = Increased budget & capacity needs.
        """
        print(f"[Intent Oracle] 🔎 Probing Hiring Signals for '{company_name}'...")
        query = f'site:indeed.com/cmp/"{company_name}" jobs'
        results = await self.dork_engine.run_dork_search(query, "")
        
        if not results: return None
        
        best = results[0]
        snippet = best.get('snippet', '')
        
        # Look for headcount indicators
        job_count = re.search(r'([\d,]+)\s+openings', snippet, re.I)
        is_aggressive = any(k in snippet.lower() for k in ["hiring now", "growing", "urgent", "immediate"])

        return {
            "hiring_intent_url": best.get('source_url'),
            "open_job_count": job_count.group(1) if job_count else "1-5",
            "is_aggressively_hiring": is_aggressive,
            "intent_layer": "Hiring Growth"
        }

    async def scrape_ad_signals(self, domain):
        """
        Detects if company is spending on ads via Dorking discovery.
        """
        print(f"[Intent Oracle] 💰 Probing Ad Spend for '{domain}'...")
        # Check standard tracking markers in search results
        query = f'"{domain}" (site:facebook.com/ads/library | site:google.com/search?q=ads)'
        results = await self.dork_engine.run_dork_search(query, "")
        
        has_ads = len(results) > 0
        
        return {
            "is_actively_advertising": has_ads,
            "advertising_intel_source": "Discovery Dork" if has_ads else "Blank",
            "intent_layer": "Paid Acquisition"
        }

    async def calculate_intent_multiplier(self, lead):
        """
        Synthesizes hiring and ad signals into a weight multiplier.
        """
        name = lead.get('name')
        domain = lead.get('website')
        
        if not name: return lead
        
        tasks = [self.scrape_hiring_signals(name)]
        if domain:
             tasks.append(self.scrape_ad_signals(domain))
             
        intel = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_intent_score = 0
        for res in intel:
            if res and isinstance(res, dict):
                lead.update(res)
                if res.get('is_actively_advertising'): total_intent_score += 25
                if res.get('is_aggressively_hiring'): total_intent_score += 35
                
        # Inject synthetic intent field
        lead['intent_surge_weight'] = total_intent_score
        return lead
