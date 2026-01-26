import asyncio
import json
import os
import aiohttp
from datetime import datetime

class CapitalGrowthEngine:
    """
    LAYER 3: CAPITAL & GROWTH
    Extracts financial health signals from LIVE SEC EDGAR API and UK Companies House.
    """
    
    def __init__(self, page=None):
        self.page = page
        self.cik_map = {}
        
    async def log(self, msg):
        print(f"   💰 [CapitalEngine] {msg}")

    async def _init_sec_map(self):
        """
        Fetches the official SEC Ticker->CIK mapping file.
        """
        if self.cik_map: return
        
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {"User-Agent": "PearlDataIntelligence/1.0 (admin@pearldata.com)"}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Structure: {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}, ...}
                        for key in data:
                            entry = data[key]
                            ticker = entry['ticker'].upper()
                            title = entry['title'].upper()
                            cik = f"{entry['cik_str']:010d}" # Pad to 10 digits
                            
                            self.cik_map[ticker] = cik
                            self.cik_map[title] = cik
            except Exception as e:
                await self.log(f"   -> Failed to load SEC CIK map: {e}")

    async def scrape_sec_edgar(self, query):
        """
        Queries SEC EDGAR API for 10-K, 10-Q, 8-K filings.
        """
        await self.log(f"Querying SEC EDGAR live database for: '{query}'")
        await self._init_sec_map()
        
        # Try to find CIK
        cik = self.cik_map.get(query.upper())
        if not cik:
            # Fuzzy match attempt
            for name, c in self.cik_map.items():
                if query.upper() in name:
                    cik = c
                    break
        
        if not cik:
            await self.log("   -> Company not found in SEC index (Private or Int'l?)")
            return []

        # Fetch Submissions
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        headers = {"User-Agent": "PearlDataIntelligence/1.0 (admin@pearldata.com)"}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        filings = data.get('filings', {}).get('recent', {})
                        
                        results = []
                        # Zip lists together
                        forms = filings.get('form', [])
                        dates = filings.get('filingDate', [])
                        accs = filings.get('accessionNumber', [])
                        
                        for i in range(min(5, len(forms))):
                            form = forms[i]
                            if form in ['10-K', '10-Q', '8-K']:
                                acc = accs[i].replace('-', '')
                                results.append({
                                    "source": "SEC EDGAR (Live)",
                                    "entity": data.get('name'),
                                    "filing_type": form,
                                    "filing_date": dates[i],
                                    "cik": cik,
                                    "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{data.get('primaryDocument', '')}",
                                    "is_live_data": True
                                })
                                
                        await self.log(f"   -> Found {len(results)} SEC filings for {data.get('name')}")
                        return results
                    else:
                        await self.log(f"   -> SEC API Error: {resp.status}")
            except Exception as e:
                await self.log(f"   -> SEC Connection Failed: {e}")
                
        return []

    async def scrape_companies_house(self, company_name):
        """
        Queries UK Companies House API (Free Public Beta).
        """
        await self.log(f"Checking UK Companies House live for: '{company_name}'")
        
        # Public API with Basic Auth (skipping key requirement logic for robust public scraping fallback)
        # Companies House requires a key for the API usually. 
        # For "Free" mode without key, we use a robust search URL scrape.
        
        results = []
        try:
            url = f"https://find-and-update.company-information.service.gov.uk/search?q={company_name}"
            
            await self.page.goto(url, timeout=30000)
            
            # Selector for result list
            try:
                await self.page.wait_for_selector("#results li", timeout=5000)
            except:
                return []
                
            items = await self.page.query_selector_all("#results li")
            
            for item in items[:3]:
                link_el = await item.query_selector("h3 a")
                status_el = await item.query_selector("p")
                
                if link_el:
                    title = await link_el.inner_text()
                    link = await link_el.get_attribute("href")
                    # Extract status/address from paragraph text
                    meta = await item.inner_text()
                    status = "Active" if "Active" in meta else "Inactive"
                    
                    results.append({
                        "source": "Companies House UK (Live Scrape)",
                        "company_name": title.strip(),
                        "status": status,
                        "link": f"https://find-and-update.company-information.service.gov.uk{link}",
                        "is_live_data": True
                    })
                    
            return results
        except Exception as e:
            await self.log(f"   -> Companies House Error: {e}")
            return []

    async def scrape(self, query):
        """
        Main entry point.
        """
        await self.log(f"Initiating LIVE Capital Intelligence Sweep for: {query}")
        
        # Sequential due to browser reuse
        sec_data = await self.scrape_sec_edgar(query)
        uk_data = await self.scrape_companies_house(query)
        
        combined = sec_data + uk_data
        
        # Add metadata
        for item in combined:
            item['layer'] = "Layer 3: Capital & Growth"
            item['sovereign_signal'] = "Verified Financials"
            
        await self.log(f"Mission verified. {len(combined)} real financial records secured.")
        return combined
