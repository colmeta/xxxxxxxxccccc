import asyncio
import os
import sys

# Mock Environment for Free Tier
os.environ["FREE_TIER"] = "true"
os.environ["GEMINI_API_KEY"] = "" # Simulate missing key
os.environ["GROQ_API_KEY"] = ""
os.environ["WORKER_ID"] = "test_worker_free_tier"

# Add worker to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'worker'))

from worker.scrapers.base_dork_engine import BaseDorkEngine
from playwright.async_api import async_playwright

async def test_free_tier_flow():
    print("Starting Free Tier Verification...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        engine = BaseDorkEngine(page, "TestRadar")
        
        # Test Multi-Source Aggregation
        print("\n--- Testing Total Recall (Multi-Source) ---")
        # Use a query likely to have results
        results = await engine.run_dork_search("marketing agencies", "instagram.com")
        
        print(f"\nAggregated {len(results)} results.")
        
        # Verify Sources
        sources = set(r['snippet'].split('(')[0].strip() for r in results if 'snippet' in r)
        print(f"Sources Found: {sources}")
        
        # Verify Screenshots Disabled
        if os.path.exists("screenshots"):
            print("Warning: 'screenshots' folder exists. Ensure no new screenshots were created if FREE_TIER=true.")
        else:
             print("Visuals Disabled (No screenshots folder).")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_free_tier_flow())
