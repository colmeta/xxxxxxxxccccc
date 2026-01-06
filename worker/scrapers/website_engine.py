import re
import asyncio
from utils.humanizer import Humanizer

class WebsiteEngine:
    def __init__(self, page):
        self.page = page
        self.platform = "generic_website"
        
    async def scrape(self, url):
        """
        Visits a company website and attempts to extract contact info (Emails, Phones).
        """
        print(f"[{self.platform}] 🌐 Visiting Target Headquarters: {url}")
        
        try:
            # 1. Visit Homepage
            await self.page.goto(url, wait_until="domcontentloaded", timeout=25000)
            await Humanizer.random_sleep(1, 2)
            
            # 2. Look for "Contact" or "About" links
            contact_link = await self.page.query_selector("a[href*='contact']") or \
                           await self.page.query_selector("a:has-text('Contact')") or \
                           await self.page.query_selector("a[href*='about']")
                           
            if contact_link:
                try:
                    href = await contact_link.get_attribute("href")
                    print(f"[{self.platform}] 🔗 Navigating to Contact Page: {href}")
                    await contact_link.click()
                    await self.page.wait_for_load_state("domcontentloaded", timeout=15000)
                    await Humanizer.random_sleep(1, 2)
                except:
                    pass # Failed to click or navigate, stay on homepage
            
            # 3. Extract Text & Regex Hunt
            content = await self.page.content()
            text = await self.page.inner_text("body")
            
            emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))
            phones = set(re.findall(r"(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}", text))
            
            # Filter junk emails (images, extensions)
            valid_emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.svg', '.gif'))]
            
            results = []
            if valid_emails or phones:
                results.append({
                    "name": await self.page.title(),
                    "company": "Target Company",
                    "emails": list(valid_emails),
                    "phones": list(phones),
                    "source_url": self.page.url,
                    "verified": True,
                    "snippet": f"Extracted {len(valid_emails)} emails, {len(phones)} phones."
                })
                print(f"[{self.platform}] ✅ Extracted: {len(valid_emails)} emails, {len(phones)} phones.")
            else:
                print(f"[{self.platform}] 🔸 visited but found no contact info.")
            
            return results

        except Exception as e:
            print(f"[{self.platform}] ❌ Website Visit Error: {e}")
            return []
