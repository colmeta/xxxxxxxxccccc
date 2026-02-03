import os
import aiohttp
import asyncio
import json
import random
from urllib.parse import quote

class HydraClient:
    """
    The Hydra Protocol Client.
    Manages a pool of free-tier search APIs and falls back to open-source scraping.
    Prioritizes: Serper > SearchAPI > HasData > ... > Fallback
    """
    def __init__(self):
        # SEARCH PROVIDERS (Speed Layer)
        self.api_keys = {
            "serper": os.getenv("SERPER_API_KEY"),
            "searchapi": os.getenv("SEARCHAPI_API_KEY"), # searchapi.io
            "hasdata": os.getenv("HASDATA_API_KEY"),
            "scrapingdog": os.getenv("SCRAPINGDOG_API_KEY"),
            "serpapi": os.getenv("SERPAPI_API_KEY"), # SerpApi (250/mo)
            "scraperapi": os.getenv("SCRAPER_API_KEY"), # ScraperAPI (1000/mo free)
        }
        
        # ENRICHMENT PROVIDERS (Clarity Layer)
        self.enrichment_keys = {
            "hunter": os.getenv("HUNTER_API_KEY"),
            "proxycurl": os.getenv("PROXYCURL_API_KEY"),
            "tomtom": os.getenv("TOMTOM_API_KEY"),
        }

        # Usage tracking (simple in-memory for this session)
        self.usage = {k: 0 for k in self.api_keys.keys()}
        
        # Free Tier Limits (Approximate daily/monthly safe limits)
        self.limits = {
            "serper": 2500, # 2500 total free
            "searchapi": 100, # 100 total free
            "hasdata": 100, # 100 credits
            "scrapingdog": 1000, # 1000 requests
            "serpapi": 100, # Approx limit (actually 250/mo, conservative)
            "scraperapi": 1000 # 1000 free credits usually
        }

    async def search(self, query, type="search", num=10):
        """
         Unified search method that tries providers in order of preference.
         type: 'search', 'maps', 'news'
        """
        # 1. Serper.dev (Fastest, Largest Free Tier)
        if self._can_use("serper"):
            print(f"   🐍 Hydra: Engaging Serper.dev for '{query}'...")
            res = await self._query_serper(query, type, num)
            if res: return res

        # 2. SearchAPI.io
        if self._can_use("searchapi"):
            print(f"   🐍 Hydra: Engaging SearchAPI.io for '{query}'...")
            res = await self._query_searchapi(query, type, num)
            if res: return res

        # 3. ScrapingDog
        if self._can_use("scrapingdog") and type == "search":
             print(f"   🐍 Hydra: Engaging ScrapingDog for '{query}'...")
             res = await self._query_scrapingdog(query, num)
             if res: return res

        # 4. SerpApi (Reliable but low volume)
        if self._can_use("serpapi"):
            print(f"   🐍 Hydra: Engaging SerpApi for '{query}'...")
            res = await self._query_serpapi(query, type, num)
            if res: return res
             
        # 5. ScraperAPI (If available, good volume)
        if self._can_use("scraperapi") and type == "search":
             print(f"   🐍 Hydra: Engaging ScraperAPI for '{query}'...")
             res = await self._query_scraperapi(query, num)
             if res: return res

        # 6. HasData (Web Scraping API)
        if self._can_use("hasdata") and type == "search":
            print(f"   🐍 Hydra: Engaging HasData for '{query}'...")
            res = await self._query_hasdata(query, num)
            if res: return res

        print("   ⚠️ Hydra: All fast APIs exhausted or failed. Returning None (Controller will fallback to browser).")
        return None

    def _can_use(self, provider):
        """Check if provider has key and is under limit"""
        key = self.api_keys.get(provider)
        if not key or key.strip() == "": return False
        
        # Ensure provider exists in usage/limits to prevent KeyError
        if provider not in self.usage or provider not in self.limits:
             return False

        if self.usage[provider] >= self.limits[provider]: 
            # print(f"   [Limit] {provider} exhausted.")
            return False
        return True

    # --- PROVIDER IMPLEMENTATIONS ---

    async def _query_serper(self, query, type, num):
        url = "https://google.serper.dev/search"
        if type == "maps": url = "https://google.serper.dev/places"
        if type == "news": url = "https://google.serper.dev/news"

        payload = json.dumps({"q": query, "num": num})
        headers = {
            'X-API-KEY': self.api_keys["serper"],
            'Content-Type': 'application/json'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.usage["serper"] += 1
                        return self._parse_serper(data, type)
                    else:
                        print(f"   [Serper] Error {response.status}: {await response.text()}")
        except Exception as e:
            print(f"   [Serper] Exception: {e}")
        return None

    async def _query_searchapi(self, query, type, num):
        # SearchAPI usually just supports general search well
        engine = "google"
        if type == "maps": engine = "google_maps"
        if type == "news": engine = "google_news"
        
        params = {
            "engine": engine,
            "q": query,
            "api_key": self.api_keys["searchapi"],
            "num": num
        }
        
        try:
             async with aiohttp.ClientSession() as session:
                async with session.get("https://www.searchapi.io/api/v1/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.usage["searchapi"] += 1
                        return self._parse_searchapi(data, type)
        except Exception as e:
             print(f"   [SearchAPI] Exception: {e}")
        return None

    async def _query_scrapingdog(self, query, num):
        try:
            params = {
                "api_key": self.api_keys["scrapingdog"],
                "url": f"https://www.google.com/search?q={quote(query)}&num={num}",
                "dynamic": "false"
            }
            async with aiohttp.ClientSession() as session:
                 async with session.get("https://api.scrapingdog.com/scrape", params=params) as response:
                     # ScrapingDog returns raw HTML usually, but we need parsing. 
                     # Actually, for SERP they likely have a specific endpoint or we rely on their HTML output.
                     # For now, let's assume we skip if it implies complex parsing in this client.
                     # Wait, ScrapingDog has a Google Search API endpoint specifically:
                     # https://api.scrapingdog.com/google?api_key=...&query=...
                     pass
        except: pass
        
        # Revised for ScrapingDog Google Search API
        try:
             params = {
                 "api_key": self.api_keys["scrapingdog"],
                 "query": query,
                 "results": num
             }
             async with aiohttp.ClientSession() as session:
                  async with session.get("https://api.scrapingdog.com/google", params=params) as response:
                      if response.status == 200:
                          data = await response.json()
                          self.usage["scrapingdog"] += 1
                          return self._parse_scrapingdog(data)
        except Exception as e:
             print(f"   [ScrapingDog] Exception: {e}")
        return None
        
    async def _query_scraperapi(self, query, num):
        # ScraperAPI Structured Google Search endpoint
        url = "https://api.scraperapi.com/structured/google/search"
        params = {
            'api_key': self.api_keys["scraperapi"],
            'query': query,
            'num': num
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.usage["scraperapi"] += 1
                        return self._parse_scraperapi(data)
                    else:
                        print(f"   [ScraperAPI] Error {response.status}: {await response.text()}")
        except Exception as e:
            print(f"   [ScraperAPI] Exception: {e}")
        return None
        
    async def _query_hasdata(self, query, num):
        # HasData Google Search API
        url = "https://api.hasdata.com/scrape/google-search/serp"
        headers = {"x-api-key": self.api_keys["hasdata"], "Content-Type": "application/json"}
        payload = json.dumps({"q": query, "num": num})
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.usage["hasdata"] += 1
                        return self._parse_hasdata(data)
        except Exception as e:
            print(f"   [HasData] Exception: {e}")
        return None


    async def _query_serpapi(self, query, type, num):
        # SerpApi implementation
        engine = "google"
        if type == "maps": engine = "google_maps"
        # SerpApi maps is different, usually google_maps engine
        
        params = {
            "engine": engine,
            "q": query,
            "api_key": self.api_keys["serpapi"],
            "num": num
        }
        if type == "maps":
             # Maps specific params
             params["type"] = "search"
        
        try:
             async with aiohttp.ClientSession() as session:
                async with session.get("https://serpapi.com/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.usage["serpapi"] += 1
                        return self._parse_serpapi(data, type)
                    else:
                        print(f"   [SerpApi] Error {response.status}: {await response.text()}")
        except Exception as e:
             print(f"   [SerpApi] Exception: {e}")
        return None

    # --- PARSERS (Normalize to Pearl Schema) ---
    
    def _parse_serpapi(self, data, type):
        results = []
        if type == "maps":
            for place in data.get("local_results", []):
                results.append({
                    "name": place.get("title"),
                    "address": place.get("address"),
                    "rating": place.get("rating"),
                    "reviews": place.get("reviews"),
                    "phone": place.get("phone"),
                    "website": place.get("website"),
                    "category": place.get("type"),
                    "source_url": place.get("place_id_search", ""),
                    "platform": "google_maps",
                    "verified": True
                })
        else:
            # Organic
            for item in data.get("organic_results", []):
                results.append({
                    "name": item.get("title"),
                    "source_url": item.get("link"),
                    "snippet": item.get("snippet"),
                    "company": "Google Search",
                    "verified": True
                })
        return results

    def _parse_serper(self, data, type):
        results = []
        if type == "maps":
            for place in data.get("places", []):
                results.append({
                    "name": place.get("title"),
                    "address": place.get("address"),
                    "rating": place.get("rating"),
                    "reviews": place.get("reviews"),
                    "phone": place.get("phoneNumber"),
                    "website": place.get("website"),
                    "category": place.get("category"),
                    "source_url": place.get("cid", ""), # CID or similar
                    "platform": "google_maps",
                    "verified": True
                })
        else:
            # Organic & News
            for item in data.get("organic", []) or data.get("news", []):
                results.append({
                    "name": item.get("title"),
                    "source_url": item.get("link"),
                    "snippet": item.get("snippet"),
                    "company": "Google Search",
                    "verified": True
                })
        return results

    def _parse_searchapi(self, data, type):
        results = []
        if type == "maps" and "local_results" in data:
             for place in data["local_results"]:
                results.append({
                    "name": place.get("title"),
                    "address": place.get("address"),
                    "phone": place.get("phone"),
                    "website": place.get("website"),
                    "platform": "google_maps",
                    "verified": True
                })
        else:
            for item in data.get("organic_results", []):
                 results.append({
                    "name": item.get("title"),
                    "source_url": item.get("link"),
                    "snippet": item.get("snippet"),
                    "company": "Google Search",
                    "verified": True
                })
        return results

    def _parse_scrapingdog(self, data):
        results = []
        # Normalizing ScrapingDog structure (varies, assuming 'organic_results' list)
        for item in data.get("organic_results", []):
             results.append({
                "name": item.get("title"),
                "source_url": item.get("link"),
                "snippet": item.get("snippet"),
                "company": "Google Search",
                "verified": True
            })
        return results

    def _parse_scraperapi(self, data):
        results = []
        for item in data.get("organic_results", []):
             results.append({
                "name": item.get("title"),
                "source_url": item.get("link"),
                "snippet": item.get("snippet"),
                "company": "Google Search",
                "verified": True
            })
        return results

    def _parse_hasdata(self, data):
        results = []
        for item in data.get("organicResults", []):
             results.append({
                "name": item.get("title"),
                "source_url": item.get("url"),
                "snippet": item.get("description"),
                "company": "Google Search",
                "verified": True
            })
        return results

# Singleton instance
hydra_client = HydraClient()
