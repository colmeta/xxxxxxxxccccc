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
            await self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await Humanizer.random_sleep(2, 4)
            
            # Check for "Accept Cookies" (common on Google Maps)
            try:
                await self.page.click("button[aria-label='Accept all']", timeout=2000)
                print(f"[{self.platform}] 🍪 Cookies accepted.")
            except:
                pass

            # 2. Identify the Feed
            feed_selector = "div[role='feed']"
            try:
                await self.page.wait_for_selector(feed_selector, timeout=10000)
            except:
                print(f"[{self.platform}] ⚠️ Feed not found. Might be a single location result or empty.")
                return await self._scrape_single_result()

            # 3. Scroll to load more
            print(f"[{self.platform}] 📜 Scrolling feed...")
            previously_counted = 0
            
            for _ in range(3): 
                await self.page.hover(feed_selector)
                await self.page.evaluate(f"""
                    const feed = document.querySelector("{feed_selector}");
                    if(feed) feed.scrollTop = feed.scrollHeight;
                """)
                await Humanizer.random_sleep(2, 3)
                
                items = await self.page.query_selector_all(f"{feed_selector} > div")
                if len(items) == previously_counted:
                    break
                previously_counted = len(items)

            # 4. Extract
            results = []
            feed_children = await self.page.query_selector_all(f"{feed_selector} > div > div[role='article']")
            if not feed_children:
                feed_children = await self.page.query_selector_all("a[href*='/maps/place/']")

            print(f"[{self.platform}] 🧐 Analyzing {len(feed_children)} potential listings...")

            for item in feed_children[:10]:
                try:
                    text_content = await item.inner_text()
                    href = await item.get_attribute("href")
                    
                    if not href or "/maps/place/" not in href:
                        link_el = await item.query_selector("a[href*='/maps/place/']")
                        if link_el:
                            href = await link_el.get_attribute("href")
                        else:
                            continue

                    lines = [line.strip() for line in text_content.split("\n") if line.strip()]
                    if not lines: continue
                    
                    name = lines[0]
                    rating = "N/A"
                    address = "Unknown"
                    phone = "N/A"
                    
                    for line in lines:
                        if "(" in line and ")" in line and ("." in line or "," in line):
                            rating = line.split("·")[0].strip()
                        if "United States" in line or (", " in line and any(char.isdigit() for char in line)):
                            address = line
                        if line.startswith("+") or (line.count("-") == 2 and any(char.isdigit() for char in line)):
                            phone = line

                    results.append({
                        "name": name,
                        "rating": rating,
                        "address": address,
                        "phone": phone,
                        "source_url": href,
                        "verified": True,
                        "snippet": f"{name} ({rating}) - {address}"
                    })
                except:
                    continue
            
            if results:
                print(f"[{self.platform}] ✅ Extracted {len(results)} locations.")
                return results
            else:
                return await self._scrape_single_result()

        except Exception as e:
            print(f"[{self.platform}] ❌ Error: {e}")
            return [{
                "name": "Google Maps Query",
                "source_url": url,
                "verified": False,
                "snippet": f"Search initiated for: {query}. Visual verification required.",
                "error": str(e)
            }]

    async def _scrape_single_result(self):
        """Fallback for when Maps redirects directly to a single result."""
        try:
            print(f"[{self.platform}] 📍 analyzing single location view...")
            
            try:
                h1 = await self.page.query_selector("h1")
                name = await h1.inner_text()
            except:
                return []
                
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
                
                rating_span = await self.page.query_selector("div[role='complementary'] span[aria-label*='stars']")
                if rating_span: rating = await rating_span.get_attribute("aria-label")
            except:
                pass

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
            
        except Exception as e:
            print(f"[{self.platform}] ❌ Single Result Error: {e}")
            return [{
                 "name": "Google Maps Search",
                 "address": "Unknown Location",
                 "source_url": self.page.url,
                 "verified": False,
                 "snippet": f"Visual confirmation required for: {self.page.url}",
                 "error": str(e)
            }]
