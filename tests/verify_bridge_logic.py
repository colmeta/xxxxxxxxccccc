
print("DEBUG: Script started", flush=True)
import sys
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock

print("DEBUG: Modules imported", flush=True)

# Add worker to path
worker_path = os.path.join(os.getcwd(), 'worker')
sys.path.append(worker_path)
print(f"DEBUG: Added {worker_path} to sys.path", flush=True)

# PURE MOCKING: Force feed mocks into sys.modules to prevent ANY real imports of dependencies
sys.modules['utils'] = MagicMock()
sys.modules['utils.humanizer'] = MagicMock()
sys.modules['utils.email_verifier'] = MagicMock()
sys.modules['scrapers'] = MagicMock()
sys.modules['scrapers.linkedin_engine'] = MagicMock()
sys.modules['scrapers.website_engine'] = MagicMock()

print("DEBUG: Mocks injected", flush=True)

try:
    # Manual import to verify
    from utils.enrichment_bridge import EnrichmentBridge
    print("DEBUG: EnrichmentBridge imported successfully", flush=True)
except Exception as e:
    print(f"DEBUG: Import failed: {e}", flush=True)
    sys.exit(1)

async def test_enrichment_flow():
    print("🧪 Starting Enrichment Bridge Verification...", flush=True)
    
    # Mock Page
    mock_page = MagicMock()
    
    # Initialize Bridge
    bridge = EnrichmentBridge(mock_page)
    
    # Setup the mock for WebsiteEngine
    # The class is instantiated as `website_engine = WebsiteEngine(self.page)`
    # So we need to mock the return value of that instantiation.
    
    mock_engine_instance = AsyncMock()
    mock_engine_instance.find_company_website.return_value = "https://test-company.com"
    mock_engine_instance.scrape.return_value = [{
        "emails": ["contact@test-company.com"],
        "phones": ["555-0199"],
        "socials": {"twitter": "https://twitter.com/test"},
        "meta_description": "A test company description."
    }]
    
    # IMPORTANT: We must patch the WebsiteEngine class *where it is looked up*
    # Since we mocked `scrapers.website_engine` in sys.modules, we set the class on that mock.
    sys.modules['scrapers.website_engine'].WebsiteEngine = MagicMock(return_value=mock_engine_instance)
    
    # Create dummy leads
    leads = [{
        "name": "Test Company",
        "source_url": "http://test-source.com",
        "status": "new"
    }]
    
    print("   Running enrich_business_leads...", flush=True)
    enriched = await bridge.enrich_business_leads(leads)
    
    # Verify results
    lead = enriched[0]
    print(f"   Result Lead: {lead}", flush=True)
    
    failures = []
    if lead.get('website') != "https://test-company.com":
        failures.append("❌ Failed to find/set website URL")
    
    if "contact@test-company.com" not in lead.get('emails', []):
        failures.append("❌ Failed to extract/merge emails")
        
    if "555-0199" not in lead.get('phones', []):
        failures.append("❌ Failed to extract/merge phones")
        
    if lead.get('socials', {}).get('twitter') != "https://twitter.com/test":
        failures.append("❌ Failed to extract/merge socials")
        
    if not failures:
        print("✅ SUCCESS: All contacts extracted and merged correctly!", flush=True)
    else:
        print("🚨 FAILURES found:", flush=True)
        for f in failures:
            print(f"   {f}", flush=True)

if __name__ == "__main__":
    asyncio.run(test_enrichment_flow())
