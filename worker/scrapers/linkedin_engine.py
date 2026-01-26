import asyncio
import random
import os
import urllib.parse
import re
from playwright.async_api import TimeoutError
from utils.humanizer import Humanizer

class LinkedInEngine:
    def __init__(self, page):
        self.page = page
        self.platform = "linkedin"

    async def scrape(self, query):
        """
        Executes a targeted search on LinkedIn using a 'Multi-Headed' approach.
        Tries Google (Standard + Basic) -> Bing -> DuckDuckGo.
        """
        print(f"[{self.platform}] 🚀 Launching 'Unshakable' Search for: {query}")
        
        results = []
        
        # 1. Google Search (Priority)
        results = await self._search_google(query)
        if results: return results
        
        # 2. Bing Search (Fallback 1)
        print(f"[{self.platform}] ⚠️ Google dry/blocked. engaging BING fallback...")
        results = await self._search_bing(query)
        if results: return results

        # 3. DuckDuckGo (Last Resort)
        print(f"[{self.platform}] ⚠️ Bing dry. Engaging DUCKDUCKGO...")
        results = await self._search_ddg(query)
        if results: return results

        # 4. ScraperAPI Fallback (The Force Multiplier)
        from utils.scraper_api_bridge import scraper_api_bridge
        if os.getenv("SCRAPER_API_KEY"):
            print(f"[{self.platform}] 🚀 Local engines blocked. Engaging ScraperAPI Proxy Search...")
            results = await self._search_via_scraper_api(query)
            if results: return results

        print(f"[{self.platform}] 🔧 All strategies exhausted. Using Mock Data.")
        return self._get_mock_data(query)

    async def _search_via_scraper_api(self, query):
        """Uses ScraperAPI to fetch LinkedIn search results if local worker is throttled."""
        from utils.scraper_api_bridge import scraper_api_bridge
        encoded_query = urllib.parse.quote(f"site:linkedin.com/in/ {query}")
        url = f"https://www.google.com/search?q={encoded_query}&num=20"
        
        try:
            # We use the bridge's logic to fetch content via proxy
            # Note: We need a method in ScraperAPIBridge for simple get_content
            import httpx
            api_key = os.getenv("SCRAPER_API_KEY")
            proxy_url = f"http://scraperapi:{api_key}@proxy-server.scraperapi.com:8001"
            
            async with httpx.AsyncClient(proxies=proxy_url, timeout=30.0, verify=False) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    # We can't use Playwright on the returned HTML directly easily, 
                    # so we'll do a simple regex/selector parse of the raw HTML
                    # or better: we'll use the page.goto WITH the proxy in a new context
                    return await self._search_google(query, use_proxy=True)
        except Exception as e:
            print(f"❌ ScraperAPI Proxy Search Error: {e}")
        return []

    async def _search_google(self, query, use_proxy=False):
        try:
            # Dorking query
            encoded_query = urllib.parse.quote(f"site:linkedin.com/in/ {query}")
            
            if use_proxy and os.getenv("SCRAPER_API_KEY"):
                api_key = os.getenv("SCRAPER_API_KEY")
                url = f"http://api.scraperapi.com?api_key={api_key}&url=https://www.google.com/search?q={encoded_query}&num=20"
            else:
                url = f"https://www.google.com/search?q={encoded_query}&num=100"
            
            print(f"[{self.platform}] 📡 Google: {url}")
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await Humanizer.random_sleep(2, 3)
            
            # Re-check page state before selecting
            if self.page.is_closed(): return []
            
            # Check for "Basic HTML" (legacy) which happens on aggressive blocking
            content = await self.page.content()
            is_basic_html = "<!DOCTYPE html PUBLIC" in content or "ZINbbc" in content or "google.com/search" in content and "gb_e" not in content
            
            results = []
            if is_basic_html:
                print(f"[{self.platform}] 🔦 Detected 'Basic HTML' Layout. Extraction bypass active...")
                # In Basic HTML, results are in div.ZINbbc
                items = await self.page.query_selector_all("div.ZINbbc")
                for item in items:
                    link_handle = await item.query_selector("a[href*='/url?q=']")
                    if not link_handle: continue
                    
                    href = await link_handle.get_attribute("href")
                    if "/url?q=" in href:
                        href = href.split("/url?q=")[1].split("&")[0]
                        href = urllib.parse.unquote(href)
                    
                    if "/in/" not in href: continue

                    title_handle = await item.query_selector("h3") or await item.query_selector("div.vvjwJb")
                    title_text = await title_handle.inner_text() if title_handle else "LinkedIn Profile"
                    
                    # Snippet extraction
                    snippet_handle = await item.query_selector("div.s3v9rd")
                    snippet = await snippet_handle.inner_text() if snippet_handle else ""
                    
                    # Avatar Extraction
                    avatar_url = None
                    try:
                        img_handle = await item.query_selector("img")
                        if img_handle:
                            avatar_url = await img_handle.get_attribute("src")
                    except: pass

                    results.append(self._parse_linkedin_title(title_text, href, snippet, avatar_url))
            else:
                # Standard Modern Layout
                links = await self.page.query_selector_all("div.g a[href*='linkedin.com/in/']")
                for link in links:
                    href = await link.get_attribute("href")
                    if not href or "/in/" not in href: continue
                    
                    title_handle = await link.query_selector("h3")
                    title_text = await title_handle.inner_text() if title_handle else await link.inner_text()
                    
                    # Find snippet in the same .g container
                    snippet = ""
                    try:
                        container = await self.page.evaluate_handle("el => el.closest('.g')", link)
                        if container:
                            snippet = await container.as_element().inner_text()
                    except: pass
                    
                    # Avatar Extraction
                    avatar_url = None
                    try:
                        # In modern Google, avatars are often in the parent .g container or adjacent
                        container = await self.page.evaluate_handle("el => el.closest('.g')", link)
                        if container:
                            img_handle = await container.as_element().query_selector("img")
                            if img_handle:
                                avatar_url = await img_handle.get_attribute("src")
                    except: pass
                    
                    results.append(self._parse_linkedin_title(title_text, href, snippet, avatar_url))

            if results:
                 print(f"[{self.platform}] ✅ Google found {len(results)} leads.")
            return results

        except Exception as e:
            print(f"[{self.platform}] ❌ Google Error: {e}")
            return []

    def _parse_linkedin_title(self, title_text, href, snippet="", avatar_url=None):
        """Centralized parser for LinkedIn search results."""
        clean_text = title_text.replace("| LinkedIn", "").replace(" ...", "").strip()
        parts = clean_text.split(" - ")
        
        name = parts[0].strip()
        job = parts[1].strip() if len(parts) > 1 else "Professional"
        company = "LinkedIn"
        
        if len(parts) > 2:
            company = parts[2].strip()
        elif " at " in job:
            job_parts = job.split(" at ")
            job = job_parts[0].strip()
            company = job_parts[1].strip()

        # Check snippet for email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', f"{clean_text} {snippet}")
        email = email_match.group(0) if email_match else None
        
        # Extract location from snippet or title
        location = None
        # Look for patterns like "Austin, TX" or "New York, New York"
        loc_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?,\s+[A-Z]{2}(?:\s+\d{5})?)|([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?,\s+[A-Z][a-z]+)', f"{clean_text} {snippet}")
        if loc_match:
            location = loc_match.group(0)
        else:
            # Try to find "Greater City Area" pattern
            area_match = re.search(r'Greater\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:Area|Metropolitan)', f"{clean_text} {snippet}")
            if area_match:
                location = area_match.group(1)

        return {
            "name": name,
            "title": job,
            "company": company,
            "location": location,
            "linkedin_url": href,
            "email": email,
            "avatar_url": avatar_url,
            "source_url": href,
            "platform": "linkedin",
            "verified": True
        }

    async def _search_bing(self, query):
        try:
            encoded_query = urllib.parse.quote(f"site:linkedin.com/in/ {query}")
            url = f"https://www.bing.com/search?q={encoded_query}"
            
            await self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await Humanizer.random_sleep(2, 3)
            
            # Re-check page state before selecting
            if self.page.is_closed(): return []
            
            # Bing Selectors
            links = await self.page.query_selector_all("li.b_algo h2 a")
            
            results = []
            for link in links:
                href = await link.get_attribute("href")
                title_text = await link.inner_text()
                
                if href and "linkedin.com/in/" in href:
                     # Parse Title
                     parts = title_text.split(" - ")
                     name = parts[0].replace("| LinkedIn", "").strip()
                     results.append({
                        "name": name,
                        "title": parts[1].strip() if len(parts)>1 else "Professional",
                         "company": parts[2].strip() if len(parts)>2 else "Unknown",
                        "source_url": href,
                        "verified": True,
                        "snippet": "Via Bing Fallback"
                     })
            
            if results:
                 print(f"[{self.platform}] ✅ Bing found {len(results)} leads.")
            return results

        except Exception as e:
            print(f"[{self.platform}] ❌ Bing Error: {e}")
            return []

    async def _search_ddg(self, query):
        try:
            # DuckDuckGo
            encoded_query = urllib.parse.quote(f"site:linkedin.com/in/ {query}")
            url = f"https://duckduckgo.com/?q={encoded_query}&t=hp&ia=web"
            
            await self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await Humanizer.random_sleep(2, 3)
            
            # Re-check page state before selecting
            if self.page.is_closed(): return []
            
            links = await self.page.query_selector_all("a[data-testid='result-title-a']")
            
            results = []
            for link in links:
                href = await link.get_attribute("href")
                title_text = await link.inner_text()
                
                if href and "linkedin.com/in/" in href:
                     results.append({
                        "name": title_text.split("-")[0].strip(),
                        "title": "Professional", # DDG titles are often cleaner/shorter
                        "company": "LinkedIn",
                        "source_url": href,
                        "verified": True,
                        "snippet": "Via DDG Fallback"
                     })
            
            if results:
                 print(f"[{self.platform}] ✅ DDG found {len(results)} leads.")
            return results

        except Exception as e:
            print(f"[{self.platform}] ❌ DDG Error: {e}")
            return []

    async def _get_mock_data(self, query):
        print(f"[{self.platform}] 🔧 Specific person search exhausted. Attempting broad Company Page sweep...")
        # Fallback 4: Broad Company Search (Never fail completely)
        try:
             broad_query = f"{query} company linkedin"
             # Remove "Founder" or titles to just find the entity
             if "Founder" in query or "CEO" in query:
                 company_only = query.split('"')[1] if '"' in query else query
                 broad_query = f"{company_only} linkedin"
                 
             results = await self._search_google(broad_query)
             if results:
                 print(f"[{self.platform}] ⚠️ Found Company Page as fallback.")
                 return results
        except: pass

        return []

if __name__ == "__main__":
    pass
