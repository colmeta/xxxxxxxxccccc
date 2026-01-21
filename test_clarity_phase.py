from playwright.async_api import async_playwright
import asyncio
from worker.utils.enrichment_bridge import EnrichmentBridge
from worker.utils.gemini_client import GeminiClient # Just in case dependencies need it

async def test_clarity_protocol():
    print("🚀 Starting Clarity Protocol Test...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Run headless for speed, or false for debug
        page = await browser.new_page()
        
        bridge = EnrichmentBridge(page)
        
        # Test Case 1: Positive Match (Real Digital Agency)
        # Assuming 'Huge' or 'Ogilvy' is big enough to be found easily
        leads = [
            {"name": "Ogilvy", "source_url": "https://www.ogilvy.com"}, 
            {"name": "Rapid Auto Shipping", "source_url": None}, # Logistics (Should be flagged)
            {"name": "ClarityPearl Test", "source_url": "https://claritypearl.ai"} # Unknown/Fake (Discovery test)
        ]
        
        print("\n🧪 Testing Enrichment on Sample Data...")
        enriched = await bridge.enrich_business_leads(
            leads, 
            target_industry_keywords=["marketing", "agency", "creative", "advertising"],
            negative_keywords=["shipping", "trucking", "logistics"]
        )
        
        print("\n📊 RESULTS:")
        for lead in enriched:
            status = lead.get('status', 'UNKNOWN')
            reason = lead.get('relevance_reason', 'N/A')
            dm = lead.get('decision_maker_name', 'None')
            print(f"  - {lead['name']}: [{status}] Reason: {reason} | DM: {dm} | Site: {lead.get('website')}")
            if 'site_emails' in lead:
                print(f"    Contacts: {len(lead['site_emails'])} emails, {len(lead.get('social_links', {}))} socials")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_clarity_protocol())
