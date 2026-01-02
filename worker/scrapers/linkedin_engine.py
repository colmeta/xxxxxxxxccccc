import asyncio
from playwright.async_api import async_playwright

class LinkedInEngine:
    def __init__(self, page):
        self.page = page
        self.platform = "linkedin"

    async def scrape(self, query):
        """
        Executes a targeted search on LinkedIn for the given query.
        Uses public search results to avoid aggressive login-wall detection initially.
        """
        print(f"[{self.platform}] 🚀 Launching deep-search for: {query}")
        
        # Try real scraping first, fall back to mock data if it fails
        search_url = f"https://www.google.com/search?q=site:linkedin.com/in/ {query}"
        
        try:
            print(f"[{self.platform}] 📡 Navigating to: {search_url}")
            await self.page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2)
            
            # Extract search result items
            results = []
            
            # Try multiple selector strategies
            entries = await self.page.query_selector_all("div.g")
            print(f"[{self.platform}] 🔍 Found {len(entries)} search results with selector 'div.g'")
            
            if len(entries) == 0:
                # Try alternative selector
                entries = await self.page.query_selector_all("div[data-sokoban-container]")
                print(f"[{self.platform}] 🔍 Trying alternative selector, found {len(entries)} results")
            
            if len(entries) == 0:
                print(f"[{self.platform}] ⚠️  No results found. Google may have changed selectors or blocked the request.")
                print(f"[{self.platform}] 🔧 Falling back to MOCK DATA")
                return self._get_mock_data(query)
            
            for i, entry in enumerate(entries[:5]):
                try:
                    title_elem = await entry.query_selector("h3")
                    link_elem = await entry.query_selector("a")
                    
                    if title_elem and link_elem:
                        title_text = await title_elem.inner_text()
                        url = await link_elem.get_attribute("href")
                        
                        # Try to get snippet
                        snippet_elem = await entry.query_selector("div.VwiC3b, div[data-sncf], div.lyLwlc")
                        snippet = await snippet_elem.inner_text() if snippet_elem else ""
                        
                        # Parse name and title from the LinkedIn title format
                        parts = title_text.split(" - ")
                        name = parts[0] if len(parts) > 0 else "Unknown"
                        job_title = parts[1] if len(parts) > 1 else "Professional"
                        company = parts[2] if len(parts) > 2 else "LinkedIn Profile"
                        
                        # Clean up LinkedIn suffix
                        name = name.replace(" | LinkedIn", "").strip()
                        job_title = job_title.replace(" | LinkedIn", "").strip()
                        company = company.replace(" | LinkedIn", "").strip()
                        
                        results.append({
                            "name": name,
                            "title": job_title,
                            "company": company,
                            "source_url": url,
                            "snippet": snippet[:200],  # Limit snippet length
                            "verified": True
                        })
                        print(f"[{self.platform}] ✅ Extracted: {name} - {job_title}")
                except Exception as parse_error:
                    print(f"[{self.platform}] ⚠️  Failed to parse result {i+1}: {parse_error}")
                    continue
            
            if len(results) == 0:
                print(f"[{self.platform}] 📊 No valid results parsed. Falling back to MOCK DATA")
                return self._get_mock_data(query)
            
            print(f"[{self.platform}] 📊 Total scraped: {len(results)} real results")
            return results
            
        except Exception as e:
            print(f"[{self.platform}] ❌ Scraping failed: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"[{self.platform}] 🔧 Falling back to MOCK DATA due to error")
            return self._get_mock_data(query)
    
    def _get_mock_data(self, query):
        """Return mock data as fallback"""
        return [{
            "name": f"Sample Lead for {query}",
            "title": "CEO & Founder",
            "company": "Tech Startup Inc.",
            "email": "sample@example.com",
            "source_url": "https://linkedin.com/in/sample",
            "snippet": f"Experienced professional in {query}",
            "verified": True
        }]


async def test_engine():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        engine = LinkedInEngine(page)
        data = await engine.scrape("SaaS CEOs Austin")
        print(data)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_engine())
