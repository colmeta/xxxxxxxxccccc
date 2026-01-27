import asyncio
import os
import sys

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'worker'))

# Mock Env
os.environ["FREE_TIER"] = "true"

from playwright.async_api import async_playwright
from worker.scrapers.patent_intelligence_engine import PatentIntelligenceEngine
from worker.scrapers.events_networking_engine import EventsNetworkingEngine

async def test_phase2_scrapers():
    print("Starting Phase 2 Verification (Patents & Events)...")
    
    async with async_playwright() as p:
        print("   -> Launching Browser for Innovation Checks...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. Test Patents (API + Scrape)
        print("\nTesting PatentIntelligenceEngine...")
        patent_engine = PatentIntelligenceEngine(page)
        
        # USPTO (API)
        uspto_results = await patent_engine.scrape_uspto("artificial intelligence")
        print(f"   -> USPTO Results: {len(uspto_results)}")
        
        # Google Patents (Scrape)
        google_patents = await patent_engine.scrape_google_patents("cybersecurity")
        print(f"   -> Google Patents Results: {len(google_patents)}")
        
        # 2. Test Events (Scrape)
        print("\nTesting EventsNetworkingEngine...")
        events_engine = EventsNetworkingEngine(page)
        
        # Eventbrite
        eventbrite_results = await events_engine.scrape_eventbrite("startups")
        print(f"   -> Eventbrite Results: {len(eventbrite_results)}")
        
        # Meetup
        meetup_results = await events_engine.scrape_meetup("tech networking")
        print(f"   -> Meetup Results: {len(meetup_results)}")
        
        await browser.close()
        
    print("\nVerification Complete.")

if __name__ == "__main__":
    asyncio.run(test_phase2_scrapers())
