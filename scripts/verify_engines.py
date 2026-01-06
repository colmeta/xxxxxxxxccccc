import asyncio
import sys
import os

# Add global worker path to sys.path so we can import modules
sys.path.append(os.path.join(os.getcwd(), 'worker'))

def verify_imports():
    print("🔍 Verifying Imports...")
    try:
        from hydra_controller import HydraController
        print("✅ HydraController imported")
        
        from utils.stealth import StealthContext
        print("✅ StealthContext imported")
        
        from utils.humanizer import Humanizer
        print("✅ Humanizer imported")
        
        from scrapers.linkedin_engine import LinkedInEngine
        from scrapers.google_maps_engine import GoogleMapsEngine
        from scrapers.social_radar import TwitterEngine, InstagramEngine
        from scrapers.startup_radar import CrunchbaseEngine, ProductHuntEngine, RedditEngine, YCombinatorEngine
        from scrapers.website_engine import WebsiteEngine
        print("✅ All Scraper Engines imported")
        
        print("🎉 code structure is valid!")
        return True
    except Exception as e:
        print(f"❌ Import Error: {e}")
        return False

if __name__ == "__main__":
    success = verify_imports()
    if not success:
        sys.exit(1)
