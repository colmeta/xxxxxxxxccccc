import httpx
import os
import json
from typing import Optional, List

class ScraperAPIBridge:
    """
    CLARITY PEARL - SCRAPERAPI CRAWLER BRIDGE
    Interfaces with ScraperAPI's 2026 Crawler technology.
    """
    def __init__(self):
        self.api_key = os.getenv("SCRAPER_API_KEY")
        self.base_url = "https://api.scraperapi.com/crawler"

    async def start_crawl(self, seed_url: str, callback_url: str = None) -> Optional[str]:
        """
        Starts an automated crawl session on a domain.
        Offloads memory-heavy URL discovery to ScraperAPI's infrastructure.
        """
        if not self.api_key:
            print("⚠️ ScraperAPIBridge: SCRAPER_API_KEY not found in environment.")
            return None

        payload = {
            "apiKey": self.api_key,
            "url": seed_url,
            "callbackUrl": callback_url,
            "crawler": {
                "max_depth": 2, # Stay efficient
                "follow_pagination": True,
                "discovery_paths": ["/contact", "/about", "/team", "/leadership"],
                "ignore_duplicates": True
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(self.base_url, json=payload)
                if res.status_code in [200, 201, 202]:
                    job_data = res.json()
                    print(f"📡 ScraperAPI Crawler: Session Started for {seed_url} (Job ID: {job_data.get('jobId')})")
                    return job_data.get('jobId')
                else:
                    print(f"⚠️ ScraperAPI Crawler Failed: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"❌ ScraperAPIBridge Error: {e}")
            
        return None

    async def get_results(self, job_id: str) -> List[str]:
        """
        Retrieves discovered URLs from a completed crawl.
        """
        if not self.api_key or not job_id:
            return []

        url = f"{self.base_url}/{job_id}/results?apiKey={self.api_key}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    results = res.json()
                    # Expecting a list of discovery data
                    urls = [item.get('url') for item in results if item.get('url')]
                    return urls
        except Exception as e:
            print(f"❌ ScraperAPI Get Results Error: {e}")
            
        return []

# Singleton instance
scraper_api_bridge = ScraperAPIBridge()
