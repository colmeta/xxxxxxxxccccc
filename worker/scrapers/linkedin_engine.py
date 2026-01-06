import asyncio
import random
import urllib.parse
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

        print(f"[{self.platform}] 🔧 All strategies exhausted. Using Mock Data.")
        return self._get_mock_data(query)

    async def _search_google(self, query):
        try:
            # Dorking query
            encoded_query = urllib.parse.quote(f"site:linkedin.com/in/ {query}")
            url = f"https://www.google.com/search?q={encoded_query}&num=10"
            
            print(f"[{self.platform}] 📡 Google: {url}")
            await self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await Humanizer.random_sleep(1, 2)
            
            # Check for "Basic HTML" (legacy) which happens on aggressive blocking
            content = await self.page.content()
            is_basic_html = "<!DOCTYPE html PUBLIC" in content or "ZINbbc" in content
            
            if is_basic_html:
                print(f"[{self.platform}] 🔦 Detected 'Basic HTML' Layout. Adjusting selectors...")
                links = await self.page.query_selector_all("div.ZINbbc > div:nth-child(1) > a")
            else:
                # Standard Modern Layout
                links = await self.page.query_selector_all("div.g a[href*='linkedin.com/in/']")

            results = []
            for link in links:
                href = await link.get_attribute("href")
                if not href or "/in/" not in href or "google.com" in href: continue
                
                # Cleaning URL from Google redirect if present (in Basic HTML it often is '/url?q=...')
                if "/url?q=" in href:
                    href = href.split("/url?q=")[1].split("&")[0]
                    href = urllib.parse.unquote(href)

                try:
                    title_handle = await link.query_selector("h3") or await link.query_selector("div.vvjwJb") # Basic HTML title
                    if title_handle:
                        title_text = await title_handle.inner_text()
                    else:
                        title_text = await link.inner_text() # Fallback for extremely basic A tags
                    
                    if not title_text or "LinkedIn" not in title_text and "-" not in title_text: continue

                    # Flexible Parsing
                    # "Name - Title - Company | LinkedIn" or "Name - Title | LinkedIn"
                    clean_text = title_text.replace("| LinkedIn", "").replace(" ...", "")
                    parts = clean_text.split(" - ")
                    
                    name = parts[0].strip()
                    job = parts[1].strip() if len(parts) > 1 else "Professional"
                    company = parts[2].strip() if len(parts) > 2 else "LinkedIn"
                    
                    results.append({
                        "name": name,
                        "title": job,
                        "company": company,
                        "source_url": href,
                        "verified": True,
                        "snippet": f"Via Google Unshakable | {clean_text}"
                    })
                except Exception:
                    continue
            
            if results:
                 print(f"[{self.platform}] ✅ Google found {len(results)} leads.")
            return results

        except Exception as e:
            print(f"[{self.platform}] ❌ Google Error: {e}")
            return []

    async def _search_bing(self, query):
        try:
            encoded_query = urllib.parse.quote(f"site:linkedin.com/in/ {query}")
            url = f"https://www.bing.com/search?q={encoded_query}"
            
            await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await Humanizer.natural_scroll(self.page)
            
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
            
            await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await Humanizer.random_sleep(2, 3)
            
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

    def _get_mock_data(self, query):
        return [{
            "name": f"Sample Lead ({query})",
            "title": "CEO & Founder",
            "company": "Tech Stealth Inc.",
            "email": "sample@example.com",
            "source_url": "https://linkedin.com/in/sample",
            "verified": False,
            "snippet": "Mock Data (System Blocked)"
        }]

if __name__ == "__main__":
    pass
