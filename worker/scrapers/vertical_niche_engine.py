import asyncio
import re
from scrapers.base_dork_engine import BaseDorkEngine

class VerticalNicheEngine:
    """
    CLARITY PEARL - VERTICAL NICHE ENGINE
    Mission: Deep penetration into industry-specific hubs.
    Layers 7 & 8: Legal, Medical, Construction, Trade.
    """
    def __init__(self, page):
        self.page = page
        self.dork_engine = BaseDorkEngine(page, "niche_hunter")

    async def scrape_legal(self, company_or_person):
        """
        Signals from Avvo, Martindale, Justia.
        """
        print(f"[Niche Engine] Probing Legal Hubs for '{company_or_person}'...")
        # Check Avvo
        avvo_query = f'site:avvo.com/attorney "{company_or_person}"'
        results = await self.dork_engine.run_dork_search(avvo_query, "")
        
        if not results: return None
        
        best = results[0]
        snippet = best.get('snippet', '')
        
        ratings = re.search(r'Rating:\s+([\d\.]+)/10', snippet)
        practice_areas = re.search(r'Practice areas: ([\w\s,]+)\.', snippet, re.I)
        
        return {
            "legal_rep_url": best.get('source_url'),
            "avvo_rating": ratings.group(1) if ratings else None,
            "practice_areas": practice_areas.group(1).split(', ') if practice_areas else [],
            "industry_vertical": "Legal"
        }

    async def scrape_medical(self, entity_name):
        """
        Signals from Healthgrades, Doximity.
        """
        print(f"[Niche Engine] Probing Medical Hubs for '{entity_name}'...")
        query = f'site:healthgrades.com/physician "{entity_name}"'
        results = await self.dork_engine.run_dork_search(query, "")
        
        if not results: return None
        
        best = results[0]
        snippet = best.get('snippet', '')
        
        # Patients choice / highly rated signals
        highly_rated = "highly rated" in snippet.lower()
        stars = re.search(r'([\d\.]+)\s+stars', snippet)

        return {
            "medical_directory_url": best.get('source_url'),
            "healthgrades_rating": stars.group(1) if stars else None,
            "distinguished_medical_signal": highly_rated,
            "industry_vertical": "Medical"
        }

    async def scrape_findlaw(self, company_name):
        """
        Signals from FindLaw (Legal).
        """
        print(f"[Niche Engine] Checking FindLaw for '{company_name}'...")
        query = f'site:lawyers.findlaw.com "{company_name}"'
        results = await self.dork_engine.run_dork_search(query, "")
        
        if not results: return None
        
        best = results[0]
        return {
            "findlaw_url": best.get('source_url'),
            "industry_vertical": "Legal",
            "source": "FindLaw (Dork)"
        }

    async def scrape_webmd(self, company_name):
        """
        Signals from WebMD (Medical).
        """
        print(f"[Niche Engine] Checking WebMD for '{company_name}'...")
        query = f'site:doctor.webmd.com "{company_name}"'
        results = await self.dork_engine.run_dork_search(query, "")
        
        if not results: return None
        
        best = results[0]
        return {
            "webmd_url": best.get('source_url'),
            "industry_vertical": "Medical",
            "source": "WebMD (Dork)"
        }

    async def scrape_construction(self, company_name):
        """
        Signals from BuildZoom, Contractors.com.
        """
        print(f"[Niche Engine] Probing Construction Hubs for '{company_name}'...")
        query = f'site:buildzoom.com/contractor "{company_name}"'
        results = await self.dork_engine.run_dork_search(query, "")
        
        if not results: return None
        
        best = results[0]
        snippet = best.get('snippet', '')
        
        permits = re.search(r'([\d,]+)\s+permits', snippet, re.I)
        score = re.search(r'BuildZoom score:\s+([\d\.]+)', snippet, re.I)

        return {
            "construction_profile_url": best.get('source_url'),
            "buildzoom_score": score.group(1) if score else None,
            "permit_count_historical": permits.group(1) if permits else "Unknown",
            "industry_vertical": "Construction"
        }

    async def auto_detect_vertical_enrich(self, lead):
        """
        Intelligent vertical routing based on keyword detection.
        """
        name = lead.get('name', '')
        desc = lead.get('meta_description', '').lower()
        
        # Detection logic
        is_legal = any(k in desc for k in ["law", "attorney", "legal", "firm", "justice"])
        is_med = any(k in desc for k in ["medical", "clinic", "health", "doctor", "physician", "dentist"])
        is_const = any(k in desc for k in ["construction", "builder", "roofing", "plumbing", "contractor"])
        
        intel = {}
        if is_legal:
            intel = await self.scrape_legal(name)
        elif is_med:
            intel = await self.scrape_medical(name)
        elif is_const:
            intel = await self.scrape_construction(name)
            
        if intel:
            lead.update(intel)
            
        return lead
