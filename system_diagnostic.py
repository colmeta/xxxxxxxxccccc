"""
🔍 COMPREHENSIVE SYSTEM DIAGNOSTIC
Audits the entire Pearl Data Intelligence codebase for issues
"""

import os
import sys
import json
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

# ========================================================================
# 1. ENVIRONMENT VARIABLES CHECK
# ========================================================================
def check_environment():
    print_header("1. ENVIRONMENT VARIABLES AUDIT")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_ROLE_KEY',
        'GEMINI_API_KEY',
        'GROQ_API_KEY',
    ]
    
    optional_vars = [
        'SCRAPER_API_KEY',
        'HUNTER_API_KEY',
        'VERIFALIA_API_KEY',
        'FLUTTERWAVE_SECRET_KEY',
    ]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." + value[-4:] if len(value) > 14 else value
            print_success(f"{var}: {masked}")
        else:
            print_error(f"{var}: MISSING (CRITICAL)")
    
    print()
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." + value[-4:] if len(value) > 14 else value
            print_success(f"{var}: {masked}")
        else:
            print_warning(f"{var}: Not set (optional)")

# ========================================================================
# 2. DATABASE SCHEMA CHECK
# ========================================================================
def check_database_schema():
    print_header("2. DATABASE SCHEMA VALIDATION")
    
    try:
        from backend.services.supabase_client import get_supabase
        supabase = get_supabase()
        
        # Test connection
        result = supabase.table('jobs').select('id').limit(1).execute()
        print_success("Database connection established")
        
        # Check critical tables
        tables_to_check = [
            'jobs',
            'lead_vault',
            'worker_status',
            'organizations',
            'campaigns',
            'mega_profiles',
        ]
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print_success(f"Table '{table}' exists and accessible")
            except Exception as e:
                print_error(f"Table '{table}' issue: {str(e)[:80]}")
                
    except Exception as e:
        print_error(f"Database check failed: {str(e)}")

# ========================================================================
# 3. AI API CHECK
# ========================================================================
def check_ai_apis():
    print_header("3. AI API INTEGRATION STATUS")
    
    # Check Gemini
    try:
        import google.generativeai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Test")
            print_success("Gemini API: OPERATIONAL")
        else:
            print_warning("Gemini API: Key not found")
    except Exception as e:
        print_error(f"Gemini API: FAILED - {str(e)[:80]}")
    
    # Check Groq
    try:
        from groq import Groq
        api_key = os.getenv('GROQ_API_KEY')
        if api_key:
            client = Groq(api_key=api_key)
            # Just test instantiation for now
            print_success("Groq API: Key present and client initialized")
        else:
            print_warning("Groq API: Key not found")
    except Exception as e:
        print_error(f"Groq API: FAILED - {str(e)[:80]}")

# ========================================================================
# 4. SCRAPER ENGINE CHECK
# ========================================================================
def check_scraper_engines():
    print_header("4. SCRAPER ENGINE AUDIT")
    
    scrapers = [
        'worker/scrapers/linkedin_engine.py',
        'worker/scrapers/google_maps_engine.py',
        'worker/scrapers/organic_search_engine.py',
        'worker/scrapers/vertical_niche_engine.py',
        'worker/scrapers/tiktok_scout.py',
        'worker/scrapers/product_hunt_tracker.py',
        'worker/scrapers/instagram_hunter.py',
       'worker/scrapers/amazon_scanner.py',
    ]
    
    for scraper in scrapers:
        path = Path(scraper)
        if path.exists():
            print_success(f"{path.name}: Found")
        else:
            print_error(f"{scraper}: MISSING")

# ========================================================================
# 5. FRONTEND BUILD CHECK
# ========================================================================
def check_frontend():
    print_header("5. FRONTEND BUILD STATUS")
    
    frontend_path = Path('frontend')
    
    # Check package.json
    package_json = frontend_path / 'package.json'
    if package_json.exists():
        print_success("package.json: Found")
        with open(package_json) as f:
            data = json.load(f)
            print_info(f"Project: {data.get('name', 'Unknown')}")
            print_info(f"Version: {data.get('version', 'Unknown')}")
    else:
        print_error("package.json: MISSING")
    
    # Check node_modules
    node_modules = frontend_path / 'node_modules'
    if node_modules.exists():
        print_success("node_modules: Installed")
    else:
        print_error("node_modules: MISSING - Run 'npm install'")
    
    # Check .env
    env_file = frontend_path / '.env'
    if env_file.exists():
        print_success(".env: Found")
        with open(env_file) as f:
            lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
            for line in lines:
                if '=' in line:
                    key, _ = line.split('=', 1)
                    print_info(f"  {key}: Set")
    else:
        print_error(".env: MISSING")
    
    # Check critical components
    components = [
        'frontend/src/App.jsx',
        'frontend/src/components/Layout.jsx',
        'frontend/src/components/OracleControl.jsx',
        'frontend/src/components/SovereignHub.jsx',
        'frontend/src/lib/supabase.js',
    ]
    
    for comp in components:
        path = Path(comp)
        if path.exists():
            print_success(f"{path.name}: Found")
        else:
            print_error(f"{comp}: MISSING")

# ========================================================================
# 6. WORKER STATUS CHECK
# ========================================================================
def check_worker():
    print_header("6. WORKER INFRASTRUCTURE")
    
    worker_files = [
        'worker/core/hydra_controller.py',
        'worker/core/proxy_manager.py',
        'worker/utils/gemini_client.py',
        'worker/utils/contact_discovery.py',
        'worker/utils/enrichment_bridge.py',
        'worker/utils/clarity_phase.py',
    ]
    
    for wf in worker_files:
        path = Path(wf)
        if path.exists():
            print_success(f"{path.name}: Found")
        else:
            print_error(f"{wf}: MISSING")

# ========================================================================
# 7. BACKEND ROUTERS CHECK
# ========================================================================
def check_backend():
    print_header("7. BACKEND API ROUTERS")
    
    routers = [
        'backend/routers/jobs.py',
        'backend/routers/results.py',
        'backend/routers/oracle.py',
        'backend/routers/crm.py',
        'backend/routers/campaigns.py',
        'backend/routers/bulk.py',
        'backend/routers/extension_bridge.py',
        'backend/routers/diagnostics.py',
    ]
    
    for router in routers:
        path = Path(router)
        if path.exists():
            print_success(f"{path.name}: Found")
        else:
            print_error(f"{router}: MISSING")

# ========================================================================
# MAIN EXECUTION
# ========================================================================
if __name__ == "__main__":
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║         🎯 PEARL DATA INTELLIGENCE - SYSTEM DIAGNOSTIC            ║")
    print("║                   Comprehensive Codebase Audit                    ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    try:
        check_environment()
        check_database_schema()
        check_ai_apis()
        check_scraper_engines()
        check_frontend()
        check_worker()
        check_backend()
        
        print_header("✨ DIAGNOSTIC COMPLETE")
        print_info("Review the output above for any ❌ errors or ⚠️  warnings")
        print_info("Address critical (❌) issues first, then warnings (⚠️ )")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Diagnostic interrupted by user{Colors.RESET}")
    except Exception as e:
        print_error(f"Diagnostic failed: {str(e)}")
        import traceback
        traceback.print_exc()
