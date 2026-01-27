import asyncio
import os
import sys

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'worker'))

# Mock Env
os.environ["FREE_TIER"] = "true"

from playwright.async_api import async_playwright
from worker.scrapers.trade_data_engine import TradeDataEngine
from worker.scrapers.government_contracts_engine import GovernmentContractsEngine

async def test_phase1_scrapers():
    print("🚀 Starting Phase 1 Verification (Trade & Gov)...")
    
    async with async_playwright() as p:
        print("   -> Launching Browser for Government Checks...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. Test Trade Data (API Based)
        print("\n📦 Testing TradeDataEngine (APIs)...")
        trade_engine = TradeDataEngine(page) # Page not needed but passed
        # Use a commodity keyword likely to exist
        trade_results = await trade_engine.fetch_usa_trade_data("coffee")
        print(f"   -> Census Results: {len(trade_results)}")
        
        comtrade_results = await trade_engine.fetch_un_comtrade()
        print(f"   -> Comtrade Results: {len(comtrade_results)}")
        
        # 2. Test Government Contracts (Scrape + API)
        print("\n🏛️ Testing GovernmentContractsEngine...")
        gov_engine = GovernmentContractsEngine(page)
        
        # USAspending (API)
        spending_results = await gov_engine.scrape_usaspending("technology")
        print(f"   -> USAspending Results: {len(spending_results)}")
        
        # SAM.gov (Scrape - Protected)
        # Note: SAM.gov often blocks headless, so this tests our resilience/fallbacks
        sam_results = await gov_engine.scrape_sam_gov("software")
        print(f"   -> SAM.gov Results: {len(sam_results)}")
        
        await browser.close()
        
    print("\n✅ Verification Complete.")

if __name__ == "__main__":
    asyncio.run(test_phase1_scrapers())
