
import asyncio
import sys
import os
from playwright.async_api import async_playwright

# Ensure worker is in path
sys.path.append(os.path.join(os.getcwd(), 'worker'))

try:
    from utils.enrichment_bridge import EnrichmentBridge
    from utils.humanizer import Humanizer
except Exception as e:
    print(f"❌ Import Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

async def test_bridge():
    print("🔹 Starting Contact Discovery Test...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Headless for agent
        context = await browser.new_context()
        page = await context.new_page()
        
        bridge = EnrichmentBridge(page)
        
        # Test Case 1: Positive match (Digital Agency)
        # We need a real agency that is easy to find
        test_leads = [
            {"name": "Ogilvy", "source_url": ""} # Missing website, bridge should find it
        ]
        
        print("\n🧪 TEST 1: Positive Case (Ogilvy) - Expecting Website + Contacts")
        results = await bridge.enrich_business_leads(test_leads)
        print("RESULTS:", results)
        
        # Test Case 2: Negative match (Trucking Company but looking for Marketing)
        # "JB Hunt" is a trucking company
        bad_leads = [
            {"name": "J.B. Hunt Transport Services", "source_url": ""} 
        ]
        
        print("\n🧪 TEST 2: Negative Case (JB Hunt) - Expecting 'IRRELEVANT'")
        results_bad = await bridge.enrich_business_leads(bad_leads, target_industry_keywords=["marketing", "agency"], negative_keywords=["transport", "logistics", "trucking"])
        print("RESULTS BAD:", results_bad)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_bridge())
