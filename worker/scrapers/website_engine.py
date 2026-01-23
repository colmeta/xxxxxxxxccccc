import re
import asyncio
import urllib.parse
from utils.humanizer import Humanizer

class WebsiteEngine:
    def __init__(self, page):
        self.page = page
        self.platform = "generic_website"
        
    async def find_company_website(self, company_name, use_proxy=False):
        """
        Multi-headed search to find the official website.
        Google -> Bing -> DuckDuckGo
        """
        print(f"[{self.platform}] 🔍 Searching for website: {company_name}")
        
        # 1. Google Search
        url = await self._search_google(company_name, use_proxy=use_proxy)
        if url: return url
        
        # 2. Bing Search
        print(f"[{self.platform}] ⚠️ Google dry/blocked. Engaging BING fallback...")
        url = await self._search_bing(company_name, use_proxy=use_proxy)
        if url: return url

        # 3. DuckDuckGo Search
        print(f"[{self.platform}] ⚠️ Bing dry. Engaging DUCKDUCKGO...")
        url = await self._search_ddg(company_name, use_proxy=use_proxy)
        if url: return url

        return None

    async def _search_google(self, company_name, use_proxy=False):
        try:
            query = urllib.parse.quote(f"{company_name} official site")
            
            if use_proxy and os.getenv("SCRAPER_API_KEY"):
                api_key = os.getenv("SCRAPER_API_KEY")
                url = f"http://api.scraperapi.com?api_key={api_key}&url=https://www.google.com/search?q={query}&num=10"
            else:
                url = f"https://www.google.com/search?q={query}&num=10"
            
            await self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await Humanizer.random_sleep(1, 2)
            
            # Check for Basic HTML (Blocking)
            content = await self.page.content()
            is_basic_html = "ZINbbc" in content
            
            links = []
            if is_basic_html:
                # Legacy Mobile/Basic HTML
                items = await self.page.query_selector_all("div.ZINbbc > div:first-child > a")
                links = items
            else:
                # Modern Desktop
                links = await self.page.query_selector_all("div.g a")

            for link in links:
                href = await link.get_attribute("href")
                if not href: continue
                
                # Clean Google redirect
                if "/url?q=" in href:
                    href = href.split("/url?q=")[1].split("&")[0]
                    href = urllib.parse.unquote(href)
                
                if self._is_valid_company_url(href):
                    print(f"[{self.platform}] 🎯 Google Found URL: {href}")
                    return href
            return None
        except Exception as e:
            print(f"[{self.platform}] ❌ Google Error: {e}")
            return None

    async def _search_bing(self, company_name, use_proxy=False):
        try:
            query = urllib.parse.quote(f"{company_name} official site")
            
            if use_proxy and os.getenv("SCRAPER_API_KEY"):
                api_key = os.getenv("SCRAPER_API_KEY")
                url = f"http://api.scraperapi.com?api_key={api_key}&url=https://www.bing.com/search?q={query}"
            else:
                url = f"https://www.bing.com/search?q={query}"
            
            await self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await Humanizer.random_sleep(1, 2)
            
            links = await self.page.query_selector_all("li.b_algo h2 a")
            for link in links:
                href = await link.get_attribute("href")
                if self._is_valid_company_url(href):
                    print(f"[{self.platform}] 🎯 Bing Found URL: {href}")
                    return href
            return None
        except Exception as e:
            print(f"[{self.platform}] ❌ Bing Error: {e}")
            return None

    async def _search_ddg(self, company_name, use_proxy=False):
        try:
            query = urllib.parse.quote(f"{company_name} official site")
            
            if use_proxy and os.getenv("SCRAPER_API_KEY"):
                api_key = os.getenv("SCRAPER_API_KEY")
                url = f"http://api.scraperapi.com?api_key={api_key}&url=https://duckduckgo.com/?q={query}"
            else:
                url = f"https://duckduckgo.com/?q={query}&t=hp&ia=web"
            
            await self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await Humanizer.random_sleep(1, 2)
            
            links = await self.page.query_selector_all("a[data-testid='result-title-a']")
            for link in links:
                href = await link.get_attribute("href")
                if self._is_valid_company_url(href):
                    print(f"[{self.platform}] 🎯 DDG Found URL: {href}")
                    return href
            return None
        except Exception as e:
            print(f"[{self.platform}] ❌ DDG Error: {e}")
            return None

    def _is_valid_company_url(self, url):
        if not url: return False
        blocked = ["google.", "linkedin.", "facebook.", "instagram.", "twitter.", "youtube.", "glassdoor.", "zoominfo.", "crunchbase.", "yellowpages.", "yelp."]
        if any(b in url for b in blocked): return False
        return True

    async def verify_industry(self, html_content, target_industry_keywords, negative_keywords):
        """
        The 'Bouncer' Logic.
        Checks if the website aligns with the Target Industry and DOES NOT match Negative Keywords.
        Returns: (is_relevant, reason)
        """
        text = html_content.lower()
        
        # 1. Negative Check (Bounce incorrect industries)
        # e.g. "trucking", "logistics" if we want "marketing"
        for neg in negative_keywords:
            if neg.lower() in text:
                return False, f"Matched Negative Keyword: {neg}"
                
        # 2. Positive Check (Must have at least one relevant keyword)
        # e.g. "marketing", "agency", "seo"
        match_found = False
        for pos in target_industry_keywords:
            if pos.lower() in text:
                match_found = True
                break
                
        if not match_found:
            return False, "No Target Industry Keywords Found"
            
        return True, "Verified Industry Match"

    async def scrape(self, url, company_name=None, target_keywords=None, negative_keywords=None):
        """
        Visits a company website and attempts to extract contact info (Emails, Phones, Socials).
        Also runs 'The Bouncer' verification if keywords are provided.
        """
        print(f"[{self.platform}] 🌐 Visiting Target Headquarters: {url}")
        
        results = {
            "source_url": url,
            "emails": [],
            "phones": [],
            "socials": {},
            "verified_industry": None,
            "relevance_reason": "Not Checked",
            "meta_description": "",
            "logo_url": None
        }

        try:
            # 1. Visit Homepage
            await self.page.goto(url, wait_until="domcontentloaded", timeout=25000)
            await Humanizer.random_sleep(1, 2)
            
            content = await self.page.content()
            text = await self.page.inner_text("body")
            
            # Extract Logo / Favicon
            try:
                # 1. Look for Favicon/Icon
                icon_handle = await self.page.query_selector("link[rel*='icon']")
                if icon_handle:
                    results["logo_url"] = await icon_handle.get_attribute("href")
                
                # 2. Look for OG Image (often the logo or brand image)
                if not results["logo_url"]:
                    og_handle = await self.page.query_selector("meta[property='og:image']")
                    if og_handle:
                        results["logo_url"] = await og_handle.get_attribute("content")

                # 3. Clearbit Fallback (The Industry Standard)
                if not results["logo_url"] or results["logo_url"].startswith('/'):
                    domain = urllib.parse.urlparse(url).netloc
                    results["logo_url"] = f"https://logo.clearbit.com/{domain}"
            except: pass

            # 2. Industry Verification (The Bouncer)
            if target_keywords and negative_keywords:
                is_relevant, reason = await self.verify_industry(
                    text + " " + results["meta_description"], 
                    target_keywords, 
                    negative_keywords
                )
                results["verified_industry"] = is_relevant
                results["relevance_reason"] = reason
                print(f"[{self.platform}] 🛡️ Bouncer Verdict: {'✅ Allowed' if is_relevant else '⛔ Denied'} ({reason})")

            # Extract physical address (for Location)
            try:
                # Look for address-like patterns in footer or body
                # Standard US address: City, ST Zip
                addr_match = re.search(r'([A-Z][a-z]+, [A-Z]{2}\s+\d{5})', text)
                if addr_match:
                    results["location"] = addr_match.group(0)
            except: pass

            # 4. Look for "Contact" / "About" links for deeper scraping
            # We scrape current page (Home) + potentially Contact page
            pages_to_scrape = [text] # Start with homepage text
            
            contact_link = await self.page.query_selector("a[href*='contact']") or \
                           await self.page.query_selector("a:has-text('Contact')")
            
            if contact_link:
                try:
                    c_href = await contact_link.get_attribute("href")
                    print(f"[{self.platform}] 🔗 Navigating to Contact Page: {c_href}")
                    await contact_link.click()
                    await self.page.wait_for_load_state("domcontentloaded", timeout=15000)
                    await Humanizer.random_sleep(1, 2)
                    pages_to_scrape.append(await self.page.inner_text("body"))
                except: pass

            # 4. Extract Data from all visited pages
            full_text = " ".join(pages_to_scrape)
            
            # Emails
            emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", full_text))
            results["emails"] = [e for e in emails if not e.endswith(('.png', '.jpg', '.svg', '.gif', '.webp'))]
            
            # Phones (US/Intl formats)
            phones = set(re.findall(r"(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}", full_text))
            results["phones"] = list(phones)
            
            # Socials
            social_patterns = {
                "linkedin": r"linkedin\.com/company/[\w-]+",
                "facebook": r"facebook\.com/[\w\.]+",
                "twitter": r"(twitter\.com|x\.com)/[\w]+",
                "instagram": r"instagram\.com/[\w\.]+",
                "youtube": r"youtube\.com/(channel|c|user)/[\w]+"
            }
            
            for platform, pattern in social_patterns.items():
                matches = re.search(pattern, content) # Check HTML content for links
                if matches:
                    results["socials"][platform] = "https://" + matches.group(0)

            print(f"[{self.platform}] ✅ Extracted: {len(results['emails'])} emails, {len(results['phones'])} phones, {len(results['socials'])} socials.")
            
            return [results]

        except Exception as e:
            print(f"[{self.platform}] ❌ Website Visit Error: {e}")
            results["error"] = str(e)
            return [results]
