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
            # Google Maps results are usually in a div with role='feed'
            feed_selector = "div[role='feed']"
            try:
                await self.page.wait_for_selector(feed_selector, timeout=10000)
            except:
                print(f"[{self.platform}] ⚠️ Feed not found. Might be a single location result or empty.")
                return await self._scrape_single_result()

            # 3. Scroll to load more (The "Unshakable" Scroll)
            print(f"[{self.platform}] 📜 Scrolling feed...")
            previously_counted = 0
            
            # Scroll loop (limit to 3 scrolls for efficiency in this version)
            for _ in range(3): 
                # Hover over the feed to ensure scroll focus
                await self.page.hover(feed_selector)
                
                # Scroll down using the feed element itself
                await self.page.evaluate(f"""
                    const feed = document.querySelector("{feed_selector}");
                    if(feed) feed.scrollTop = feed.scrollHeight;
                """)
                await Humanizer.random_sleep(2, 3)
                
                # Check execution
                items = await self.page.query_selector_all(f"{feed_selector} > div")
                if len(items) == previously_counted:
                    break # End of list
                previously_counted = len(items)

            # 4. Extract
            results = []
            # Maps listings often use 'a' tags with specific classes or structure
            # A robust way is to find elements with aria-label containing "video" or "Photo" which usually indicates a listing card, 
            # OR iterate through the feed children.
            
            feed_children = await self.page.query_selector_all(f"{feed_selector} > div > div[role='article']")
            if not feed_children:
                # Fallback selector
                feed_children = await self.page.query_selector_all("a[href*='/maps/place/']")

            print(f"[{self.platform}] 🧐 Analyzing {len(feed_children)} potential listings...")

            for item in feed_children[:10]: # Limit to top 10 for safety/speed
                try:
                    # Maps is dynamic text. Extract text and parse.
                    text_content = await item.inner_text()
                    href = await item.get_attribute("href")
                    
                    if not href or "/maps/place/" not in href:
                        # Sometimes the card wrapper isn't the link, the link is inside
                        link_el = await item.query_selector("a[href*='/maps/place/']")
                        if link_el:
                            href = await link_el.get_attribute("href")
                        else:
                            continue

                    # Basic parsing of text block usually:
                    # "Business Name\nRating\nCategory · Address\nOpen..."
                    lines = [line.strip() for line in text_content.split("\n") if line.strip()]
                    
                    if not lines: continue
                    
                    name = lines[0]
                    rating = "N/A"
                    address = "Unknown"
                    phone = "N/A"
                    
                    # Heuristic parsing
                    for line in lines:
                        if "(" in line and ")" in line and ("." in line or "," in line): # Rating line often "4.5(200) · Category"
                            rating = line.split("·")[0].strip()
                        if "United States" in line or ", " in line and any(char.isdigit() for char in line): # Address-ish
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

                except Exception as e:
                    continue
            
            if results:
                print(f"[{self.platform}] ✅ Extracted {len(results)} locations.")
                return results
            else:
                 return await self._scrape_single_result()

        except Exception as e:
            print(f"[{self.platform}] ❌ Error: {e}")
            return []

    async def _scrape_single_result(self):
        """Fallback for when Maps redirects directly to a single result."""
        try:
            print(f"[{self.platform}] 📍 analyzing single location view...")
            
            # Wait for main header
            try:
                h1 = await self.page.query_selector("h1")
                name = await h1.inner_text()
            except:
                return []
                
            # Extract via Accessibility labels which are robust on Google Maps
            # "Copy address", "Copy phone number" buttons often exist beside the text, or we invoke simple text search
            
            content = await self.page.content()
            
            # Simple heuristic extraction from content dump if selectors fail (Robustness)
            address = "N/A"
            phone = "N/A"
            website = "N/A"
            rating = "N/A"

            # Try finding standard buttons via selector (aria-labels)
            # Address: button[data-item-id="address"]
            # Phone: button[data-item-id*="phone"]
            
            try:
               addr_btn = await self.page.query_selector("button[data-item-id='address']") 
               if addr_btn: address = await addr_btn.get_attribute("aria-label")
               
               phone_btn = await self.page.query_selector("button[data-item-id*='phone']")
               if phone_btn: phone = await phone_btn.get_attribute("aria-label")
               
               web_btn = await self.page.query_selector("a[data-item-id='authority']")
               if web_btn: website = await web_btn.get_attribute("href")
               
               # Rating usually in a span near the top
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
             return []
