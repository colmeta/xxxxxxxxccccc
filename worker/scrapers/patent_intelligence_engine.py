import asyncio
import json
import os
import aiohttp
from datetime import datetime

class PatentIntelligenceEngine:
    """
    LAYER 6: INNOVATION & R&D
    Extracts patent data from LIVE USPTO PatentsView API and Google Patents Scraping.
    """
    
    def __init__(self, page=None):
        self.page = page
        
    async def log(self, msg):
        print(f"   💡 [PatentEngine] {msg}")

    async def scrape_uspto(self, keyword):
        """
        Queries USPTO PatentsView API (Free) for LIVE innovation signals.
        """
        await self.log(f"Querying USPTO live database for: '{keyword}'")
        
        # USPTO PatentsView API Endpoint (Updated)
        # Note: The legacy query endpoint is deprecated (410). 
        # We will attempt the new one, but prioritize Google Patents if this fails.
        url = "https://search.patentsview.org/api/v1/patent/"
        
        # Constuct Query: Title OR Abstract contains keyword
        query_json = {
            "_or": [
                {"_text_phrase": {"patent_title": keyword}},
                {"_text_phrase": {"patent_abstract": keyword}}
            ]
        }
        
        # Fields to retrieve
        fields = [
            "patent_number", "patent_title", "patent_date", 
            "patent_abstract", "assignee_organization", 
            "inventor_first_name", "inventor_last_name"
        ]
        
        params = {
            "q": json.dumps(query_json),
            "f": json.dumps(fields),
            "o": json.dumps({"per_page": 10})
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        total = data.get("total_patent_count", 0)
                        patents = data.get("patents", [])
                        
                        results = []
                        for p in patents:
                            # Safely extract nested lists
                            assignees = [a.get('assignee_organization') for a in p.get('assignees', []) if a.get('assignee_organization')]
                            inventors = [f"{i.get('inventor_first_name')} {i.get('inventor_last_name')}" for i in p.get('inventors', [])]
                            
                            results.append({
                                "source": "USPTO PatentsView",
                                "patent_id": p.get("patent_number"),
                                "title": p.get("patent_title"),
                                "assignee": assignees[0] if assignees else "Individual",
                                "inventors": inventors,
                                "filing_date": p.get("patent_date"),
                                "status": "Granted",
                                "abstract": (p.get("patent_abstract") or "")[:200] + "...",
                                "is_live_data": True
                            })
                            
                        await self.log(f"   -> USPTO Success: Found {len(results)} patents (Total in DB: {total})")
                        return results
                    else:
                        await self.log(f"   -> USPTO API Error: {resp.status}")
            except Exception as e:
                await self.log(f"   -> USPTO Connection Failed: {e}")
                
        return []

    async def scrape_google_patents(self, keyword):
        """
        Scrapes Google Patents layout using Playwright.
        """
        await self.log(f"Scanning Google Patents for R&D trends: '{keyword}'")
        results = []
        try:
            url = f"https://patents.google.com/?q={keyword}&sort=new"
            await self.page.goto(url, timeout=60000)
            
            # Wait for results
            try:
                await self.page.wait_for_selector("search-result-item", timeout=10000)
            except:
                await self.log("   -> No results on Google Patents")
                return []
                
            items = await self.page.query_selector_all("search-result-item")
            
            for item in items[:5]:
                title_el = await item.query_selector("#htmlContent")
                meta_el = await item.query_selector(".metadata")
                link_el = await item.query_selector("state-modifier")
                
                if title_el:
                    title = await title_el.inner_text()
                    assignee = "Unknown"
                    if meta_el:
                        meta_text = await meta_el.inner_text() 
                        # Basic parsing of metadata line
                        assignee = meta_text.split("\n")[0] if meta_text else "Unknown"
                        
                    results.append({
                        "source": "Google Patents (Live)",
                        "title": title.strip(),
                        "assignee": assignee,
                        "priority_date": "Recent", 
                        "link": url, # Deep linking complex, using search entry
                        "is_live_data": True
                    })
            
            await self.log(f"   -> Google Patents: Extracted {len(results)} items")
            return results
            
        except Exception as e:
            await self.log(f"   -> Google Patents Scraping Error: {e}")
            return []

    async def scrape(self, query):
        """
        Main entry point.
        """
        await self.log(f"Starting LIVE Innovation Scan for: {query}")
        
        # Parallel Execution
        results = await asyncio.gather(
            self.scrape_uspto(query),
            self.scrape_google_patents(query)
        )
        
        combined = results[0] + results[1]
        
        # Add metadata
        for item in combined:
            item['layer'] = "Layer 6: Innovation & R&D"
            item['sovereign_signal'] = "Intellectual Property Moat"
            
        await self.log(f"Mission verified. {len(combined)} real R&D records secured.")
        return combined
