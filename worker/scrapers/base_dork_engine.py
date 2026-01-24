import asyncio
import urllib.parse
from utils.humanizer import Humanizer

class BaseDorkEngine:
    """
    The 'Unshakable' Base Engine.
    Uses multi-headed search (Google -> Bing -> DDG) to find results for a specific site filter.
    """
    def __init__(self, page, platform_name):
        self.page = page
        self.platform = platform_name

    async def run_dork_search(self, query, site_filter):
        print(f"[{self.platform}] 🚀 Launching Radar for: {query} (site:{site_filter})")
        
        # 1. Google
        results = await self._search_google(query, site_filter)
        if results: return results
        
        # 2. Bing
        print(f"[{self.platform}] ⚠️ Google dry. Engaging BING...")
        results = await self._search_bing(query, site_filter)
        if results: return results
        
        # 3. DDG
        print(f"[{self.platform}] ⚠️ Bing dry. Engaging DUCKDUCKGO...")
        results = await self._search_ddg(query, site_filter)
        if results: return results

        # 4. ScraperAPI (The Unshakable Fallback)
        import os
        if os.getenv("SCRAPER_API_KEY"):
            print(f"[{self.platform}] 🚀 Local engines blocked. Engaging ScraperAPI Proxy Search...")
            results = await self._search_google(query, site_filter, use_proxy=True)
            if results: return results

        print(f"[{self.platform}] 🔧 All strategies exhausted. Returning fallback.")
        return [{
            "name": f"Search: {query}",
            "company": self.platform.capitalize(),
            "source_url": f"https://www.google.com/search?q={query}",
            "verified": False,
            "snippet": "No direct leads found via automated channels. Manual check recommended."
        }]

    async def _search_google(self, query, site_filter, use_proxy=False):
        try:
            import os
            dork_query = f"site:{site_filter} {query}" if site_filter else query
            encoded_val = urllib.parse.quote(dork_query)
            
            if use_proxy and os.getenv("SCRAPER_API_KEY"):
                api_key = os.getenv("SCRAPER_API_KEY")
                url = f"http://api.scraperapi.com?api_key={api_key}&url=https://www.google.com/search?q={encoded_val}&num=10"
            else:
                url = f"https://www.google.com/search?q={encoded_val}&num=10"
            
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await Humanizer.random_sleep(2, 3)
            
            # Re-check page state
            if self.page.is_closed(): return []
            
            content = await self.page.content()
            is_basic = "<!DOCTYPE html PUBLIC" in content or "ZINbbc" in content or "google.com/search" in content and "gb_e" not in content
            
            results = []
            if is_basic:
                print(f"[{self.platform}] 🔦 Basic HTML Detected on Google. Bypassing...")
                items = await self.page.query_selector_all("div.ZINbbc")
                for item in items:
                    link_handle = await item.query_selector("a[href*='/url?q=']")
                    if not link_handle: continue

                    href = await link_handle.get_attribute("href")
                    if "/url?q=" in href:
                        href = href.split("/url?q=")[1].split("&")[0]
                        href = urllib.parse.unquote(href)
                    
                    if site_filter not in href: continue

                    title_handle = await item.query_selector("h3") or await item.query_selector("div.vvjwJb")
                    title = await title_handle.inner_text() if title_handle else "Social Profile"
                    
                    results.append({
                        "name": title,
                        "company": self.platform.capitalize(),
                        "source_url": href,
                        "verified": True,
                        "snippet": f"Via Google Basic ({self.platform})"
                    })
            else:
                links = await self.page.query_selector_all("div.g a")
                for link in links:
                    href = await link.get_attribute("href")
                    if not href or site_filter not in href: continue
                    
                    title_handle = await link.query_selector("h3")
                    title = await title_handle.inner_text() if title_handle else await link.inner_text()
                    
                    results.append({
                        "name": title,
                        "company": self.platform.capitalize(),
                        "source_url": href,
                        "verified": True,
                        "snippet": f"Via Google Stealth ({self.platform})"
                    })
            
            return results
        except Exception as e:
            print(f"[{self.platform}] ❌ Google Error: {e}")
            return []

    async def _search_bing(self, query, site_filter):
        try:
            encoded = urllib.parse.quote(f"site:{site_filter} {query}")
            url = f"https://www.bing.com/search?q={encoded}"
            
            await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(1) # Extra stability for Bing context
            await Humanizer.natural_scroll(self.page)
            
            # Re-check page state before selecting
            if self.page.is_closed(): return []
            
            links = await self.page.query_selector_all("li.b_algo h2 a")
            results = []
            for link in links:
                href = await link.get_attribute("href")
                if href and site_filter in href:
                    results.append({
                        "name": await link.inner_text(),
                        "company": self.platform.capitalize(),
                        "source_url": href,
                        "verified": True,
                        "snippet": f"Via Bing ({self.platform})"
                    })
            return results
        except Exception:
            return []

    async def _search_ddg(self, query, site_filter):
        try:
            encoded = urllib.parse.quote(f"site:{site_filter} {query}")
            url = f"https://duckduckgo.com/?q={encoded}&t=hp&ia=web"
            
            await self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await Humanizer.random_sleep(2, 3)
            
            # Re-check page state
            if self.page.is_closed(): return []
            
            links = await self.page.query_selector_all("a[data-testid='result-title-a']")
            results = []
            for link in links:
                href = await link.get_attribute("href")
                if href and site_filter in href:
                    # Filter out DDG Ad/Tracking links
                    if "/y.js" in href or "duckduckgo.com" in href: 
                        continue
                        
                    results.append({
                         "name": await link.inner_text(),
                         "company": self.platform.capitalize(),
                         "source_url": href,
                         "verified": True,
                         "snippet": f"Via DDG ({self.platform})"
                    })
            return results
        except Exception:
            return []
