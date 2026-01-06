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

        print(f"[{self.platform}] 🔧 All strategies exhausted. No results.")
        return []

    async def _search_google(self, query, site_filter):
        try:
            encoded_val = urllib.parse.quote(f"site:{site_filter} {query}")
            url = f"https://www.google.com/search?q={encoded_val}&num=10"
            
            await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await Humanizer.random_sleep(1, 2)
            
            # Check for Basic HTML
            content = await self.page.content()
            is_basic = "<!DOCTYPE html PUBLIC" in content or "ZINbbc" in content
            
            results = []
            
            if is_basic:
                links = await self.page.query_selector_all("div.ZINbbc > div:nth-child(1) > a")
            else:
                links = await self.page.query_selector_all("div.g a")

            for link in links:
                try:
                    href = await link.get_attribute("href")
                    if not href or site_filter not in href: continue
                    
                    if "/url?q=" in href:
                        href = href.split("/url?q=")[1].split("&")[0]
                        href = urllib.parse.unquote(href)
                    
                    title_wrapper = await link.query_selector("h3") or await link.query_selector("div.vvjwJb")
                    title = await title_wrapper.inner_text() if title_wrapper else "Unknown Result"
                    
                    results.append({
                        "name": title,
                        "title": "N/A",  # To be parsed by child class if needed
                        "company": self.platform.capitalize(),
                        "source_url": href,
                        "verified": True,
                        "snippet": f"Via Google ({self.platform})"
                    })
                except:
                    continue
            
            return results
        except Exception as e:
            print(f"[{self.platform}] ❌ Google Error: {e}")
            return []

    async def _search_bing(self, query, site_filter):
        try:
            encoded = urllib.parse.quote(f"site:{site_filter} {query}")
            url = f"https://www.bing.com/search?q={encoded}"
            
            await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await Humanizer.natural_scroll(self.page)
            
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
            
            await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await Humanizer.random_sleep(2, 3)
            
            links = await self.page.query_selector_all("a[data-testid='result-title-a']")
            results = []
            for link in links:
                href = await link.get_attribute("href")
                if href and site_filter in href:
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
