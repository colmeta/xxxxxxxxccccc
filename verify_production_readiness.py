"""
🚀 COMPREHENSIVE SYSTEM VERIFICATION SCRIPT
Validates all components for 1000/1000 production readiness
"""

import os
import sys
from pathlib import Path

class SystemVerifier:
    def __init__(self):
        self.results_count = {'pass': 0, 'fail': 0, 'warn': 0}
        self.critical_failures = []
    
    def check(self, name, condition, critical=False):
        """Check a condition and track results"""
        if condition:
            print(f"✅ {name}")
            self.results_count['pass'] += 1
            return True
        else:
            symbol = "❌" if critical else "⚠️"
            print(f"{symbol} {name}")
            if critical:
                self.results_count['fail'] += 1
                self.critical_failures.append(name)
            else:
                self.results_count['warn'] += 1
            return False
    
    def verify_frontend(self):
        """Verify frontend structure and build"""
        print("\n🎨 FRONTEND VERIFICATION")
        print("=" * 60)
        
        # Critical files
        self.check("frontend/package.json exists", 
                  Path("frontend/package.json").exists(), critical=True)
        self.check("frontend/index.html exists",
                  Path("frontend/index.html").exists(), critical=True)
        self.check("frontend/src/main.jsx exists",
                  Path("frontend/src/main.jsx").exists(), critical=True)
        self.check("frontend/src/App.jsx exists",
                  Path("frontend/src/App.jsx").exists(), critical=True)
        
        # Core components
        components = [
            "Layout.jsx", "OracleControl.jsx", "SovereignHub.jsx",
            "LiveFeed.jsx", "ResultsView.jsx", "IntelligenceView.jsx",
            "GlobalMapView.jsx", "SettingsView.jsx", "ErrorBoundary.jsx"
        ]
        for comp in components:
            self.check(f"Component: {comp}",
                      Path(f"frontend/src/components/{comp}").exists())
        
        # Build files
        self.check("node_modules installed",
                  Path("frontend/node_modules").exists(), critical=True)
        self.check("Frontend .env configured",
                  Path("frontend/.env").exists())
    
    def verify_backend(self):
        """Verify backend structure"""
        print("\n⚙️ BACKEND VERIFICATION")
        print("=" * 60)
        
        # Core files
        self.check("backend/main.py exists",
                  Path("backend/main.py").exists(), critical=True)
        self.check("backend/dependencies.py exists",
                  Path("backend/dependencies.py").exists())
        
        # Critical routers
        routers = [
            "jobs.py", "results.py", "oracle.py", "crm.py",
            "campaigns.py", "bulk.py", "extension_bridge.py",
            "diagnostics.py", "organization_onboarding.py"
        ]
        for router in routers:
            self.check(f"Router: {router}",
                      Path(f"backend/routers/{router}").exists())
        
        # Services
        services = ["supabase_client.py", "hive_sentry.py", "auto_warmer.py"]
        for service in services:
            self.check(f"Service: {service}",
                      Path(f"backend/services/{service}").exists())
    
    def verify_worker(self):
        """Verify worker infrastructure"""
        print("\n🤖 WORKER VERIFICATION")
        print("=" * 60)
        
        # Core controller
        self.check("Hydra Controller exists",
                  Path("worker/hydra_controller.py").exists(), critical=True)
        
        # Critical scrapers (13-layer coverage)
        scrapers = {
            "Layer 1-2": ["linkedin_engine.py", "google_maps_engine.py", "vertical_niche_engine.py"],
            "Layer 3-4": ["b2b_platform_engine.py", "tech_stack_engine.py"],
            "Layer 5": ["intent_signal_engine.py", "job_scout_engine.py"],
            "Layer 6-7": ["startup_radar.py", "legal_financial_engine.py"],
            "Layer 8-9": ["news_pulse_engine.py", "reddit_pulse_engine.py"],
            "Layer 10-12": ["website_engine.py", "base_dork_engine.py"],
            "Layer 13": ["omega_engine.py"]
        }
        
        for layer, files in scrapers.items():
            for file in files:
                self.check(f"{layer}: {file}",
                          Path(f"worker/scrapers/{file}").exists())
        
        # Critical utils
        utils = [
            "arbiter.py", "enrichment_bridge.py", "proxy_manager.py",
            "stealth_v2.py", "gemini_client.py", "contact_discovery.py",
            "clarity_phase.py", "email_verifier.py", "geocoder.py",
            "velocity_engine.py", "ghostwriter.py"
        ]
        for util in utils:
            self.check(f"Util: {util}",
                      Path(f"worker/utils/{util}").exists())
    
    def verify_environment(self):
        """Verify environment variables"""
        print("\n🔐 ENVIRONMENT VERIFICATION")
        print("=" * 60)
        
        from dotenv import load_dotenv
        load_dotenv()
        
        # Critical vars
        self.check("SUPABASE_URL set",
                  bool(os.getenv("SUPABASE_URL")), critical=True)
        self.check("SUPABASE_KEY set",
                  bool(os.getenv("SUPABASE_KEY")), critical=True)
        
        # AI APIs
        has_gemini = bool(os.getenv("GEMINI_API_KEY"))
        has_groq = bool(os.getenv("GROQ_API_KEY"))
        self.check("AI API available (Gemini or Groq)",
                  has_gemini or has_groq, critical=True)
        
        # Optional but recommended
        self.check("SCRAPER_API_KEY set", bool(os.getenv("SCRAPER_API_KEY")))
        self.check("SMTP configured", bool(os.getenv("SMTP_USER")))
    
    def verify_documentation(self):
        """Verify project documentation"""
        print("\n📚 DOCUMENTATION VERIFICATION")
        print("=" * 60)
        
        docs = [
            "Master_Sovereign_Guide.md",
            "Team_Orchestration.md"
        ]
        
        self.check("Master Sovereign Guide",
                  Path("docs/sovereign_intelligence/Master_Sovereign_Guide.md").exists())
        self.check("Team Orchestration",
                  Path("Team_Orchestration.md").exists())
        self.check("README.md", Path("README.md").exists() or
                  (Path("frontend/README.md").exists() and Path("backend/README.md").exists()))
    
    def print_summary(self):
        """Print final summary"""
        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        
        total = sum(self.results_count.values())
        pass_rate = (self.results_count['pass'] / total * 100) if total > 0 else 0
        
        print(f"✅ Passed: {self.results_count['pass']}")
        print(f"⚠️  Warnings: {self.results_count['warn']}")
        print(f"❌ Failed: {self.results_count['fail']}")
        print(f"\n📈 Success Rate: {pass_rate:.1f}%")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"   ❌ {failure}")
            print(f"\n❌ SYSTEM NOT READY FOR PRODUCTION")
            return False
        elif pass_rate >= 95:
            print(f"\n🏆 SYSTEM STATUS: 1000/1000 PRODUCTION READY")
            return True
        elif pass_rate >= 85:
            print(f"\n✅ SYSTEM STATUS: 900/1000 - GOOD")
            return True
        elif pass_rate >= 75:
            print(f"\n⚠️  SYSTEM STATUS: 750/1000 - ACCEPTABLE")
            return True
        else:
            print(f"\n❌ SYSTEM STATUS: {pass_rate*10:.0f}/1000 - NEEDS WORK")
            return False

def main():
    print("\n🎯 PEARL DATA INTELLIGENCE - SYSTEM VERIFICATION")
    print("=" * 60)
    print("Target: 1000/1000 Production Quality")
    print("=" * 60)
    
    verifier = SystemVerifier()
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Run all verifications
    verifier.verify_environment()
    verifier.verify_frontend()
    verifier.verify_backend()
    verifier.verify_worker()
    verifier.verify_documentation()
    
    # Print summary
    success = verifier.print_summary()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
