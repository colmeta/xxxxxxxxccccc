"""
🔬 BACKEND TEST SUITE
Tests all critical endpoints to ensure API health
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def test_endpoint(method, path, expected_status=200, data=None, headers=None, description=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            print(f"{Colors.YELLOW}⚠ Unsupported method: {method}{Colors.RESET}")
            return False
        
        if response.status_code == expected_status:
            print(f"{Colors.GREEN}✅ {description or path}: {response.status_code}{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}❌ {description or path}: {response.status_code} (expected {expected_status}){Colors.RESET}")
            print(f"   Response: {response.text[:200]}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ {description or path}: CONNECTION REFUSED{Colors.RESET}")
        print(f"   Backend is not running on {BASE_URL}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ {description or path}: ERROR - {str(e)[:100]}{Colors.RESET}")
        return False

def main():
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'🔬 BACKEND API TEST SUITE'.center(70)}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")
    
    results = []
    
    # 1. Health Check
    print(f"\n{Colors.BOLD}1. CORE ENDPOINTS{Colors.RESET}")
    results.append(test_endpoint("GET", "/", description="Health Check"))
    results.append(test_endpoint("GET", "/api/diagnostics/health", description="Diagnostics Health"))
    
    # 2. Jobs API (w/o auth for basic check)
    print(f"\n{Colors.BOLD}2. JOBS API{Colors.RESET}")
    results.append(test_endpoint("GET", "/api/jobs", expected_status=401, description="Jobs List (Auth Required)"))
    
    # 3. Results API
    print(f"\n{Colors.BOLD}3. RESULTS API{Colors.RESET}")
    results.append(test_endpoint("GET", "/api/results", expected_status=401, description="Results List (Auth Required)"))
    
    # 4. Oracle API
    print(f"\n{Colors.BOLD}4. ORACLE CONTROL{Colors.RESET}")
    results.append(test_endpoint("POST", "/api/oracle/dispatch", expected_status=401, description="Oracle Dispatch (Auth Required)"))
    
    # 5. Organization API
    print(f"\n{Colors.BOLD}5. ORGANIZATION ONBOARDING{Colors.RESET}")
    results.append(test_endpoint("POST", "/api/organizations/auto-setup", expected_status=401, description="Org Auto-Setup (Auth Required)"))
    
    # 6. White-Label API
    print(f"\n{Colors.BOLD}6. WHITE-LABEL API v1{Colors.RESET}")
    results.append(test_endpoint("GET", "/api/v1/leads", expected_status=401, description="V1 Leads (API Key Required)"))
    
    # 7. Browser Extension Bridge
    print(f"\n{Colors.BOLD}7. EXTENSION BRIDGE{Colors.RESET}")
    results.append(test_endpoint("POST", "/api/extension/capture", expected_status=401, description="Extension Capture (Auth Required)"))
    
    # Summary
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    if success_rate >= 80:
        color = Colors.GREEN
        status = "EXCELLENT"
    elif success_rate >= 60:
        color = Colors.YELLOW
        status = "FAIR"
    else:
        color = Colors.RED
        status = "CRITICAL"
    
    print(f"{color}{Colors.BOLD}RESULTS: {passed}/{total} passed ({success_rate:.1f}%) - {status}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")
    
    if passed < total:
        print(f"{Colors.YELLOW}💡 TIP: Expected 401 errors are GOOD - they mean auth is working!{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 CONNECTION REFUSED means backend is not running.{Colors.RESET}\n")

if __name__ == "__main__":
    main()
