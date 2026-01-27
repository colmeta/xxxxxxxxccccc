import asyncio
import os
import sys

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'worker'))

# Mock Env
os.environ["FREE_TIER"] = "true"

from playwright.async_api import async_playwright
from worker.scrapers.job_scout_engine import JobScoutEngine
from worker.scrapers.capital_growth_engine import CapitalGrowthEngine
from worker.scrapers.reputation_engine import ReputationEngine

async def test_phase3_scrapers():
    print("Starting Phase 3 Verification (Depth Sources)...")
    
    async with async_playwright() as p:
        print("   -> Launching Browser for Depth Checks...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. Test Hiring Signals (Hybrid)
        print("\nTesting JobScoutEngine...")
        job_engine = JobScoutEngine(page)
        
        # Google Jobs
        g_results = await job_engine.scrape_google_jobs("python developer")
        print(f"   -> Google Jobs Results: {len(g_results)}")
        
        # RemoteOK
        r_results = await job_engine.scrape_remoteok("engineer")
        print(f"   -> RemoteOK Results: {len(r_results)}")
        
        # 2. Test Capital (API + Scrape)
        print("\nTesting CapitalGrowthEngine...")
        cap_engine = CapitalGrowthEngine(page)
        
        # SEC EDGAR (Apple - AAPL)
        sec_results = await cap_engine.scrape_sec_edgar("Apple Inc")
        print(f"   -> SEC Results: {len(sec_results)}")
        
        # Companies House (Dyson)
        uk_results = await cap_engine.scrape_companies_house("Dyson")
        print(f"   -> Companies House Results: {len(uk_results)}")
        
        # 3. Test Reputation (Dorking)
        print("\nTesting ReputationEngine...")
        rep_engine = ReputationEngine(page)
        
        # Salesforce
        rep_results = await rep_engine.scrape("Salesforce")
        print(f"   -> Reputation Score: {rep_results[0].get('calculated_trust_score', 0)}")
        print(f"   -> Keys Found: {list(rep_results[0].keys())}")
        
        await browser.close()
        
    print("\nVerification Complete.")

if __name__ == "__main__":
    asyncio.run(test_phase3_scrapers())
