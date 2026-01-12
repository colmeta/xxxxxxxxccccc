import asyncio
# from scrapers.linkedin_engine import LinkedInEngine # Lazy-loaded in __init__
from utils.email_verifier import email_verifier

class EnrichmentBridge:
    """
    CLARITY PEARL - THE BRIDGE
    Logic to pivot from a business (entity) to a person (lead).
    """
    def __init__(self, page):
        from scrapers.linkedin_engine import LinkedInEngine
        self.page = page
        self.linkedin = LinkedInEngine(page)

    async def enrich_business_leads(self, leads):
        """
        Takes a list of business leads and attempts to find the Decision Maker.
        """
        print(f"🌉 Bridge: Enrching {len(leads)} business leads...")
        enriched_leads = []
        
        for lead in leads:
            # If lead already has an email, skip deep enrichment to save time
            if lead.get('email') and '@' in lead['email']:
                enriched_leads.append(lead)
                continue
            
            try:
                # Strategy: Search LinkedIn for "Owner" or "CEO" of the business
                business_name = lead.get('name')
                location = lead.get('address', '').split(',')[-1].strip() if lead.get('address') else ""
                
                search_query = f'owner CEO "{business_name}" {location}'
                print(f"🌉 Bridge: Pivot-searching for decision maker: {search_query}")
                
                # Use LinkedIn Engine (reusing the page)
                person_results = await self.linkedin.scrape(search_query)
                
                if person_results:
                    # Merge data: keep business info, but add representative info
                    best_match = person_results[0]
                    lead['full_name'] = best_match.get('name')
                    lead['title'] = best_match.get('title')
                    lead['linkedin_url'] = best_match.get('source_url')
                    lead['email'] = best_match.get('email') # If found
                    lead['bridge_leverage'] = True
                    print(f"💎 Bridge Hit: Found {lead['full_name']} for {business_name}")
                
                enriched_leads.append(lead)
            except Exception as e:
                print(f"⚠️ Bridge Error for {lead.get('name')}: {e}")
                enriched_leads.append(lead)
                
        return enriched_leads
