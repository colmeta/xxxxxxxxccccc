import asyncio
import urllib.parse
from utils.humanizer import Humanizer
from utils.hydra_client import hydra_client

class BaseDorkEngine:
    """
    The 'Unshakable' Base Engine - Hydra-Enhanced.
    Uses multi-headed search (Serper -> SearchAPI -> ... -> Playwright) 
    to find results for a specific site filter.
    """
    def __init__(self, page, platform_name):
        self.page = page
        self.platform = platform_name

    async def run_dork_search(self, query, site_filter):
        full_query = f"site:{site_filter} {query}" if site_filter else query
        print(f"[{self.platform}] Launching 'Total Recall' Radar for: {full_query}")
        
        all_results = []
        seen_urls = set()

        def add_unique(new_results, source_name):
            if not new_results: return
            count = 0
            for res in new_results:
                url = res.get('source_url') or res.get('link')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(res)
                    count += 1
            if count > 0:
                print(f"[{self.platform}] [OK] {source_name} added {count} unique leads.")

        # 1. API LAYER (The Speed of Light)
        # Try Hydra Client first (Serper/SearchAPI etc.)
        try:
             api_results = await hydra_client.search(full_query, type="search", num=20)
             if api_results:
                 add_unique(api_results, "Hydra API")
                 # If we got good results from API, we can return early and skip slow browser
                 if len(all_results) >= 10:
                      print(f"[{self.platform}] ⚡ Hydra API delivered sufficient results. Skipping browser crawl.")
                      return all_results
        except Exception as hydra_err:
             print(f"[{self.platform}] Hydra Client Error: {hydra_err}")

        # 2. BROWSER LAYER (The Fallback)
        print(f"[{self.platform}] 🐢 API exhausted/insufficient. Engaging Playwright Fallback...")
        
        # Google Fallback
        try:
            google_results = await self._search_google(query, site_filter)
            add_unique(google_results, "Google (Browser)")
        except Exception as e:
            print(f"[{self.platform}] [ERR] Google failed: {e}")

        # ISO-BLAST
        await self._hard_reset()
        
        # Bing Fallback (only if needed)
        if len(all_results) < 5:
            try:
                print(f"[{self.platform}] Engaging BING for additional coverage...")
                bing_results = await self._search_bing(query, site_filter)
                add_unique(bing_results, "Bing")
            except Exception as e:
                print(f"[{self.platform}] [ERR] Bing failed: {e}")

        if not all_results:
             print(f"[{self.platform}] All strategies exhausted. Returning fallback.")
             return [{
                "name": f"Search: {query}",
                "company": self.platform.capitalize(),
                "source_url": f"https://www.google.com/search?q={full_query}",
                "verified": False,
                "snippet": "No direct leads found via automated channels. Manual check recommended."
             }]

        print(f"[{self.platform}] Total Recall Complete. Aggregated {len(all_results)} leads.")
        return all_results

    async def _hard_reset(self):
        """Memory & State Isolation"""
        try:
            if not self.page.is_closed():
                await self.page.goto("about:blank")
                # clear_cookies might fail if context is closed
        except: pass


    async def _search_google(self, query, site_filter, use_proxy=False):
        try:
            dork_query = f"site:{site_filter} {query}" if site_filter else query
            encoded_val = urllib.parse.quote(dork_query)
            
            # Legacy ScraperAPI fallback logic (now handled by HydraClient mostly, but kept for browser backup)
            url = f"https://www.google.com/search?q={encoded_val}&num=10"
            print(f"[{self.platform}] Google Browser: {url}")
            
            try:
                await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception as nav_err:
                 print(f"[{self.platform}] [ERR] Google Browser Nav Error: {nav_err}")
                 return []
                 
            await Humanizer.random_sleep(2, 3)
            
            if self.page.is_closed(): return []
            
            content = await self.page.content()
            is_basic = "ZINbbc" in content
            
            results = []
            if is_basic:
                # Basic HTML parser
                items = await self.page.query_selector_all("div.ZINbbc")
                for item in items:
                    link_handle = await item.query_selector("a[href*='/url?q=']")
                    if not link_handle: continue

                    href = await link_handle.get_attribute("href")
                    if "/url?q=" in href:
                        href = href.split("/url?q=")[1].split("&")[0]
                        href = urllib.parse.unquote(href)
                    
                    if site_filter and site_filter not in href: continue

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
                # Standard HTML parser
                links = await self.page.query_selector_all("div.g a")
                for link in links:
                    href = await link.get_attribute("href")
                    if not href or (site_filter and site_filter not in href): continue
                    
                    title_handle = await link.query_selector("h3")
                    if not title_handle: continue 
                    
                    title = await title_handle.inner_text()
                    
                    results.append({
                        "name": title,
                        "company": self.platform.capitalize(),
                        "source_url": href,
                        "verified": True,
                        "snippet": f"Via Google Stealth ({self.platform})"
                    })
            
            return results
        except Exception as e:
            print(f"[{self.platform}] [ERR] Google Browser Error: {e}")
            return []

    async def _search_bing(self, query, site_filter):
        try:
            encoded = urllib.parse.quote(f"site:{site_filter} {query}")
            url = f"https://www.bing.com/search?q={encoded}"
            
            try:
                await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
            except: return []
                 
            await asyncio.sleep(1)
            
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
         # Kept as stub, Hydra replaces this
         return []
