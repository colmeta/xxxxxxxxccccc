import asyncio
import random
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

        print(f"[{self.platform}] 🔧 All strategies exhausted. Using Mock Data.")
        return self._get_mock_data(query)

    async def _search_google(self, query):
        try:
            # Dorking query
            encoded_query = urllib.parse.quote(f"site:linkedin.com/in/ {query}")
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
                    
                    results.append(self._parse_linkedin_title(title_text, href, snippet))
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
                    
                    results.append(self._parse_linkedin_title(title_text, href, snippet))

            if results:
                 print(f"[{self.platform}] ✅ Google found {len(results)} leads.")
            return results

        except Exception as e:
            print(f"[{self.platform}] ❌ Google Error: {e}")
            return []

    def _parse_linkedin_title(self, title_text, href, snippet=""):
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
        
        return {
            "name": name,
            "title": job,
            "company": company,
            "email": email,
            "source_url": href,
            "verified": True,
            "snippet": snippet[:200] if snippet else clean_text,
            "channel_priority": ["email", "dm"]
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
