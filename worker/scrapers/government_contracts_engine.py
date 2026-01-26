import asyncio
import json
import os
import aiohttp
from datetime import datetime

class GovernmentContractsEngine:
    """
    LAYER 11: PUBLIC SECTOR
    Extracts LIVE government contract data from SAM.gov (via Stealth Scraping) and USAspending (API).
    """
    
    def __init__(self, page=None):
        self.page = page
        self.sam_api_key = os.getenv("SAM_API_KEY") 
        
    async def log(self, msg):
        print(f"   🏛️ [GovEngine] {msg}")

    async def scrape_sam_gov(self, keyword):
        """
        Scrapes active contract opportunities from SAM.gov (System for Award Management).
        Uses Playwright to bypass dynamic loading.
        """
        await self.log(f"Accessing SAM.gov live portal for: '{keyword}'")
        
        results = []
        try:
            # Navigate to SAM.gov Search
            # URL structure for search:
            search_url = f"https://sam.gov/search/?index=opp&page=1&sort=-modifiedDate&pageSize=25&sfm%5BsimpleSearch%5D%5BkeywordRadio%5D=ALL&sfm%5BsimpleSearch%5D%5BkeywordTags%5D={keyword}&sfm%5Bstatus%5D%5Bis_active%5D=true"
            
            await self.page.goto(search_url, timeout=60000)
            await self.page.wait_for_load_state("networkidle")
            
            # Wait for results to load
            try:
                await self.page.wait_for_selector(".usa-card__body", timeout=10000)
            except:
                await self.log("   -> No results found or timeout on SAM.gov")
                return []

            # Extract Data
            cards = await self.page.query_selector_all(".usa-card__body")
            
            for card in cards[:10]: # Limit to top 10 for speed
                title_el = await card.query_selector("h3 a")
                if title_el:
                    title = await title_el.inner_text()
                    link = await title_el.get_attribute("href")
                    
                    # Extract Agency/Dept if available (logic simplified for robust selector)
                    agency = "Unknown Agency"
                    desc_el = await card.query_selector(".usa-card__body p")
                    if desc_el:
                        agency = await desc_el.inner_text()

                    results.append({
                        "source": "SAM.gov (Live Scrape)",
                        "title": title.strip(),
                        "url": f"https://sam.gov{link}" if link.startswith("/") else link,
                        "agency": agency.strip(),
                        "status": "Active Opportunity",
                        "scraped_at": datetime.now().isoformat()
                    })
            
            await self.log(f"   -> Extracted {len(results)} live opportunities from SAM.gov")
            return results
            
        except Exception as e:
            await self.log(f"   -> SAM.gov Scraping Failed: {e}")
            return []

    async def scrape_usaspending(self, keyword):
        """
        Queries USAspending.gov API (Free) for historical awards.
        """
        await self.log(f"Querying USAspending.gov API for awards...")
        
        # USAspending API V2 Endpoint for Award Search
        url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
        
        payload = {
            "filters": {
                "keywords": [keyword],
                "time_period": [{"start_date": f"{datetime.now().year-2}-01-01", "end_date": f"{datetime.now().year}-12-31"}],
                "award_type_codes": ["A", "B", "C", "D"], # Contracts
                "limit": 10
            },
            "fields": ["Award ID", "Recipient Name", "Start Date", "End Date", "Award Amount", "Awarding Agency", "Description"],
            "limit": 10,
            "page": 1
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = []
                        for item in data.get('results', []):
                            results.append({
                                "source": "USAspending.gov (API)",
                                "recipient": item.get('Recipient Name'),
                                "amount": item.get('Award Amount'),
                                "agency": item.get('Awarding Agency'),
                                "description": item.get('Description'),
                                "start_date": item.get('Start Date'),
                                "is_live_data": True
                            })
                        
                        await self.log(f"   -> Found {len(results)} historical awards via API")
                        return results
                    else:
                        await self.log(f"   -> USAspending API Error: {resp.status}")
            except Exception as e:
                await self.log(f"   -> USAspending Connection Failed: {e}")
                
        return []

    async def scrape(self, query):
        """
        Main entry point.
        """
        await self.log(f"Initiating LIVE Public Sector sweep for: {query}")
        
        # Parallel Execution
        results = await asyncio.gather(
            self.scrape_sam_gov(query),
            self.scrape_usaspending(query)
        )
        
        combined = results[0] + results[1]
        
        # Add metadata
        for item in combined:
            item['layer'] = "Layer 11: Public Sector"
            item['sovereign_signal'] = "Government Backing"
            
        await self.log(f"Mission verified. {len(combined)} real gov records secured.")
        return combined
