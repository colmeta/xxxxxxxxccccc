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
        print(f"[{self.platform}] Launching 'Total Recall' Radar for: {query} (site:{site_filter})")
        
        all_results = []
        seen_urls = set()

        def add_unique(new_results, source_name):
            count = 0
            for res in new_results:
                url = res.get('source_url')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(res)
                    count += 1
            if count > 0:
                print(f"[{self.platform}] [OK] {source_name} added {count} unique leads.")

        # 1. Google
        try:
            google_results = await self._search_google(query, site_filter)
            add_unique(google_results, "Google")
        except Exception as e:
            print(f"[{self.platform}] [ERR] Google failed: {e}")

        # ISO-BLAST
        await self._hard_reset()
        
        # 2. Bing
        try:
            print(f"[{self.platform}] Engaging BING for additional coverage...")
            bing_results = await self._search_bing(query, site_filter)
            add_unique(bing_results, "Bing")
        except Exception as e:
            print(f"[{self.platform}] [ERR] Bing failed: {e}")

        # ISO-BLAST
        await self._hard_reset()
        
        # 3. DDG
        try:
            print(f"[{self.platform}] Engaging DUCKDUCKGO for deep web coverage...")
            ddg_results = await self._search_ddg(query, site_filter)
            add_unique(ddg_results, "DuckDuckGo")
        except Exception as e:
             print(f"[{self.platform}] [ERR] DDG failed: {e}")

        if not all_results:
             print(f"[{self.platform}] All strategies exhausted. Returning fallback.")
             return [{
                "name": f"Search: {query}",
                "company": self.platform.capitalize(),
                "source_url": f"https://www.google.com/search?q={query}",
                "verified": False,
                "snippet": "No direct leads found via automated channels. Manual check recommended."
             }]

        print(f"[{self.platform}] Total Recall Complete. Aggregated {len(all_results)} leads.")
        return all_results

    async def _hard_reset(self):
        """Memory & State Isolation"""
        try:
            await self.page.goto("about:blank")
            try: await self.page.context.clear_cookies()
            except: pass
            await asyncio.sleep(2)
        except: pass


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
            print(f"[{self.platform}] Google API: {url}")
            try:
                await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception as nav_err:
                 print(f"[{self.platform}] [ERR] Google Navigation Interrupted: {nav_err}")
                 await self._hard_reset()
                 return []
                 
            await Humanizer.random_sleep(2, 3)
            
            # Re-check page state
            if self.page.is_closed(): return []
            
            content = await self.page.content()
            is_basic = "<!DOCTYPE html PUBLIC" in content or "ZINbbc" in content or "google.com/search" in content and "gb_e" not in content
            
            results = []
            if is_basic:
                print(f"[{self.platform}] Basic HTML Detected on Google. Bypassing...")
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
            print(f"[{self.platform}] [ERR] Google Error: {e}")
            return []

    async def _search_bing(self, query, site_filter):
        try:
            encoded = urllib.parse.quote(f"site:{site_filter} {query}")
            url = f"https://www.bing.com/search?q={encoded}"
            
            try:
                await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
            except Exception as nav_err:
                 print(f"[{self.platform}] [ERR] Bing Navigation Interrupted: {nav_err}")
                 return []
                 
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
            
            try:
                await self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
            except Exception as nav_err:
                 print(f"[{self.platform}] [ERR] DDG Navigation Interrupted: {nav_err}")
                 return []
            
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
