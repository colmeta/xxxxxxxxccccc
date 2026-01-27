import asyncio
import os
import sys

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'worker'))

# Mock Env
os.environ["FREE_TIER"] = "true"

from playwright.async_api import async_playwright
from worker.scrapers.deep_infrastructure_engine import DeepInfrastructureEngine
from worker.scrapers.vertical_niche_engine import VerticalNicheEngine
from worker.scrapers.academic_research_engine import AcademicResearchEngine
from worker.scrapers.technographics_engine import TechnographicsEngine

async def test_phase4_scrapers():
    print("Starting Phase 4 Verification (Comprehensive Coverage)...")
    
    async with async_playwright() as p:
        print("   -> Launching Browser for Deep Checks...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. Test Deep Infrastructure
        print("\nTesting DeepInfrastructureEngine...")
        infra_engine = DeepInfrastructureEngine(page)
        
        # Check a known domain
        infra_results = await infra_engine.scrape("google.com")
        print(f"   -> Infrastructure Signals: {len(infra_results)}")
        
        # 2. Test Vertical Niche (Legal/Medical)
        print("\nTesting VerticalNicheEngine...")
        vertical_engine = VerticalNicheEngine(page)
        
        # FindLaw (Legal)
        legal = await vertical_engine.scrape_findlaw("Latham & Watkins")
        print(f"   -> FindLaw Result: {'Found' if legal else 'None'}")
        
        # WebMD (Medical)
        medical = await vertical_engine.scrape_webmd("Mayo Clinic")
        print(f"   -> WebMD Result: {'Found' if medical else 'None'}")
        

        # 3. Test Academic Frontier
        print("\nTesting AcademicResearchEngine...")
        academic_engine = AcademicResearchEngine(page)
        
        # PubMed/arXiv
        research = await academic_engine.scrape("Quantum Computing")
        print(f"   -> Academic Papers: {len(research)}")
        
        # 4. Test Technographics
        print("\nTesting TechnographicsEngine...")
        tech_engine = TechnographicsEngine(page)
        
        # Shodan/SecurityTrails (OpenAI)
        tech_data = await tech_engine.scrape("openai.com")
        print(f"   -> Technographics Signals: {len(tech_data)}")
        
        await browser.close()
        
    print("\nVerification Complete.")

if __name__ == "__main__":
    asyncio.run(test_phase4_scrapers())
