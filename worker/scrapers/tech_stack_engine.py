import asyncio
import re
from scrapers.base_dork_engine import BaseDorkEngine

class TechStackEngine:
    """
    CLARITY PEARL - TECHNOGRAPHICS ENGINE
    Mission: Uncover the "Digital Wiring" of a business.
    Layer 4 & 10: Tech Stacks, E-commerce, Analytics, Infrastructure.
    """
    def __init__(self, page):
        self.page = page
        self.dork_engine = BaseDorkEngine(page, "tech_sleuth")

    async def scrape_builtwith_patterns(self, domain):
        """
        Uses discovery dorking to mimic BuiltWith profiles.
        Signal: Identify high-spend tools like Salesforce, Shopify, Adobe.
        """
        print(f"[Tech Sleuth] 🛠️  Probing Tech Stack for '{domain}'...")
        query = f'site:builtwith.com "{domain}"'
        results = await self.dork_engine.run_dork_search(query, "")
        
        if not results: return None
        
        best = results[0]
        snippet = best.get('snippet', '')
        
        # Regex for common valuable technologies
        technologies = []
        tech_map = {
            "Shopify": r"Shopify",
            "Magento": r"Magento",
            "Salesforce": r"Salesforce|SFDC",
            "HubSpot": r"HubSpot",
            "Klaviyo": r"Klaviyo",
            "Google Ads": r"Google Ads",
            "Facebook Ads": r"Facebook Pixel"
        }
        
        for name, pattern in tech_map.items():
            if re.search(pattern, snippet, re.I):
                technologies.append(name)
                
        return {
            "tech_lookup_url": best.get('source_url'),
            "identified_tech_stack": technologies,
            "tech_surface_area": "Wide" if len(technologies) > 3 else "Moderate",
            "layer": "Technographics"
        }

    async def scrape_infrastructure_signals(self, domain):
        """
        Dorks security and hosting providers.
        Layer 10: Infrastructure.
        """
        print(f"[Tech Sleuth] 🌐 Probing Infrastructure for '{domain}'...")
        query = f'"{domain}" (site:shodan.io | site:censys.io | site:urlscan.io)'
        results = await self.dork_engine.run_dork_search(query, "")
        
        has_infra_record = len(results) > 0
        hosting = re.search(r'(AWS|Cloudflare|Google Cloud|DigitalOcean|Microsoft Azure)', str(results))
        
        return {
            "infrastructure_record_found": has_infra_record,
            "hosting_provider_guess": hosting.group(1) if hosting else "Independent/On-Prem",
            "infra_security_score": 85 if "Cloudflare" in str(results) else 50
        }

    async def unified_tech_enrich(self, lead):
        """
        Full technographic profile build.
        """
        domain = lead.get('website')
        if not domain: return lead
        
        # Cleanup domain (remove http/https)
        clean_domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
        
        tasks = [
            self.scrape_builtwith_patterns(clean_domain),
            self.scrape_infrastructure_signals(clean_domain)
        ]
        
        intel = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in intel:
            if res and isinstance(res, dict):
                lead.update(res)
                
        return lead
