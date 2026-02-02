
import asyncio
import random
from playwright.async_api import async_playwright
from utils.humanizer import Humanizer

class OpenSourceMapsScraper:
    """
    ZERO-COST FALLBACK:
    A lightweight, open-source Google Maps scraper for when all APIs fail.
    Prioritizes stealth over speed.
    """
    def __init__(self):
        pass

    async def scrape(self, query):
        print(f"   ☠️ Hydra: Engaging Open Source Fallback for '{query}'...")
        results = []
        
        async with async_playwright() as p:
            # Launch in Stealth Mode
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                # Navigate to Maps
                await page.goto(f"https://www.google.com/maps/search/{query}", timeout=60000)
                await page.wait_for_selector("div[role='feed']", timeout=15000)
                
                # Auto-Scroll to load results
                feed = page.locator("div[role='feed']")
                for _ in range(5):
                    await feed.evaluate("node => node.scrollTop += 2000")
                    await asyncio.sleep(random.uniform(1, 3))
                
                # Extract Data
                listings = await page.locator("div[role='article']").all()
                print(f"      -> Found {len(listings)} raw candidates via fallback.")
                
                for listing in listings[:10]: # Limit to 10 for fallback speed
                    try:
                        text = await listing.inner_text()
                        # Simple Regex-free parsing
                        lines = text.split('\n')
                        if len(lines) > 0:
                            results.append({
                                "name": lines[0],
                                "platform": "google_maps_fallback",
                                "verified": False, # Requires verification
                                "note": "Scraped via Open Source Fallback"
                            })
                    except: pass
                    
            except Exception as e:
                print(f"      [Fallback Error] {e}")
            finally:
                await browser.close()
                
        return results

# Singleton
open_source_scraper = OpenSourceMapsScraper()
