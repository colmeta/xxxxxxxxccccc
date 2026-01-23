import asyncio
import urllib.parse
from utils.humanizer import Humanizer

class GoogleMapsEngine:
    def __init__(self, page):
        self.page = page
        self.platform = "google_maps"

    async def scrape(self, query):
        print(f"[{self.platform}] 🗺️  Navigating to Google Maps for: {query}")
        
        # 1. Navigate
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/maps/search/{encoded_query}"
        
        try:
            # 1. Navigate (Hardened against timeouts)
            try:
                await self.page.goto(url, wait_until="domcontentloaded", timeout=45000)
            except Exception as nav_err:
                print(f"[{self.platform}] ⚠️ Navigation timeout (partial load). Attempting extraction anyway...")
            
            await Humanizer.random_sleep(3, 5)
            
            # Check for "Accept Cookies" - Harder look
            cookie_selectors = [
                "button[aria-label='Accept all']",
                "button:has-text('Accept all')",
                "form[action*='consent'] button"
            ]
            for selector in cookie_selectors:
                try:
                    btn = await self.page.query_selector(selector)
                    if btn:
                        await btn.click(timeout=3000)
                        print(f"[{self.platform}] 🍪 Cookies handled via '{selector}'.")
                        await asyncio.sleep(1)
                        break
                except: continue

            # 2. Identify the Feed
            feed_selector = "div[role='feed']"
            try:
                await self.page.wait_for_selector(feed_selector, timeout=20000)
            except:
                print(f"[{self.platform}] ⚠️ Feed selector not found. Checking for single result or alternate layout...")
                return await self._scrape_single_result()

            # 3. Scroll to load more (Deep Scoping)
            print(f"[{self.platform}] 📜 Scrolling feed...")
            for _ in range(15): 
                await self.page.evaluate(f'document.querySelector("{feed_selector}").scrollTop = 10000')
                await Humanizer.random_sleep(2, 3)

            # 4. Extract
            results = []
            # More specific selectors for current Google Maps layout
            feed_children = await self.page.query_selector_all("div[role='article']")
            if not feed_children:
                feed_children = await self.page.query_selector_all("a[href*='/maps/place/']")
            
            # If still nothing, try to find any link inside the feed
            if not feed_children:
                 feed_children = await self.page.query_selector_all(f"{feed_selector} a[href*='/maps/place/']")

            print(f"[{self.platform}] 🧐 Extracting all loaded listings...")

            for item in feed_children:
                try:
                    text_content = await item.inner_text()
                    href = await item.get_attribute("href")
                    
                    if not href or "/maps/place/" not in href:
                        link_el = await item.query_selector("a[href*='/maps/place/']")
                        if link_el: href = await link_el.get_attribute("href")
                        else: continue

                    lines = [line.strip() for line in text_content.split("\n") if line.strip()]
                    if len(lines) < 1: continue
                    
                    name = lines[0]
                    # Filter out purely coordinate names or placeholders
                    if len(name) < 2 or name.startswith("Coordinates"): continue

                    rating = "N/A"
                    address = "Unknown"
                    phone = "N/A"
                    website = None
                    
                    for line in lines:
                        if "(" in line and ")" in line and ("." in line or "," in line):
                            rating = line.split("·")[0].strip()
                        if "United States" in line or "UK" in line or "Canada" in line or (", " in line and any(char.isdigit() for char in line)):
                            address = line
                        if line.startswith("+") or (line.count("-") == 2 and any(char.isdigit() for char in line)):
                            phone = line
                        # Try to extract website from buttons or links
                        if "http" in line and "google.com" not in line:
                            website = line.strip()

                    results.append({
                        "name": name,
                        "rating": rating,
                        "address": address,
                        "phone": phone,
                        "website": website,
                        "source_url": href,
                        "verified": True,
                        "snippet": f"{name} ({rating}) - {address}"
                    })
                except: continue
            
            return results

        except Exception as e:
            print(f"[{self.platform}] ❌ Extraction Failed: {e}")
            return [] # Return empty list so bridge doesn't pivot on errors

    async def _scrape_single_result(self):
        """Fallback for when Maps redirects directly to a single result."""
        try:
            print(f"[{self.platform}] 📍 Analyzing single location view...")
            
            # Wait for content
            await self.page.wait_for_selector("h1", timeout=10000)
            h1 = await self.page.query_selector("h1")
            name = await h1.inner_text() if h1 else None
            
            if not name or "Maps" in name: return []
                
            address = "N/A"
            phone = "N/A"
            website = "N/A"
            rating = "N/A"

            try:
                addr_btn = await self.page.query_selector("button[data-item-id='address']") 
                if addr_btn: address = await addr_btn.get_attribute("aria-label")
                
                phone_btn = await self.page.query_selector("button[data-item-id*='phone']")
                if phone_btn: phone = await phone_btn.get_attribute("aria-label")
                
                web_btn = await self.page.query_selector("a[data-item-id='authority']")
                if web_btn: website = await web_btn.get_attribute("href")
            except: pass

            return [{
                "name": name,
                "address": address.replace("Address: ", ""),
                "phone": phone.replace("Phone: ", ""),
                "website": website,
                "rating": rating,
                "source_url": self.page.url,
                "verified": True,
                "snippet": f"Single Result: {name}"
            }]
        except: return []
