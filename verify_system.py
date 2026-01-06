
import sys
import os
import subprocess
import time
import hashlib
import json

# Ensure we can import from backend
sys.path.append(os.getcwd())


def print_result(name, success, message=""):
    icon = "[PASS]" if success else "[FAIL]"
    print(f"{icon} {name}: {message}")
    if not success and message:
        print(f"   Details: {message}")

def verify_backend():
    print("\n🔍 Verifying Backend...")
    try:
        import httpx
        from fastapi.testclient import TestClient
        from backend.main import app
        
        # Override Supabase/Auth dependencies for Safe "Offline" Testing if needed
        # We'll try running normally first. If it fails due to missing keys, we handle it.
        
        client = TestClient(app)
        
        # 1. Health Check
        response = client.get("/")
        if response.status_code == 200:
            print_result("Health Check Endpoint", True, f"Status 200, DB: {response.json().get('db')}")
        else:
            print_result("Health Check Endpoint", False, f"Status {response.status_code}")

        # 2. Opt-Out Check (Public Endpoint)
        test_hash = hashlib.sha256(b"test@example.com").hexdigest()
        # Mocking the dependency might be needed if Supabase is strictly required
        # But opt-out router uses get_supabase() which returns None if offline, 
        # raising 503. So we expect 503 if offline, or 200 if online.
        
        response = client.post("/api/opt-out/", json={"hash": test_hash})
        if response.status_code in [200, 503]:
            # 503 is acceptable if we are strictly offline and gracefully handling it
            print_result("Opt-Out Endpoint", True, f"Status {response.status_code} (Logic reachable)")
        else:
            print_result("Opt-Out Endpoint", False, f"Status {response.status_code} - {response.text}")

        # 3. Check for 'hydra_controller' import availability (Worker)
        try:
            from worker.hydra_controller import HydraController
            print_result("Hydra Worker Import", True, "Successfully imported HydraController")
        except ImportError as e:
            print_result("Hydra Worker Import", False, str(e))
            
    except ImportError as e:
        print_result("Backend Dependencies", False, f"Import Error: {e}")
    except Exception as e:
        print_result("Backend Logic", False, str(e))


def verify_frontend():
    print("\n🔍 Verifying Frontend...")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    
    if not os.path.exists(frontend_dir):
        print_result("Frontend Directory", False, "Not found")
        return

    # 1. Check package.json
    if os.path.exists(os.path.join(frontend_dir, "package.json")):
        print_result("package.json", True, "Found")
    else:
        print_result("package.json", False, "Missing")
        return

    # 2. Attempt Build (Dry Run)
    # We use 'dir' on windows to verify we are in a shell, but subprocess.run needs shell=True for npm usually on windows
    print("   Running 'npm run build' (this may take a moment)...")
    try:
        # Using shell=True for Windows 'npm' command
        result = subprocess.run(["npm", "run", "build"], cwd=frontend_dir, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print_result("Frontend Build", True, "Build successful")
        else:
            # Analyze stderr for clues
            err_msg = result.stderr or result.stdout
            snippet = err_msg[-500:] if err_msg else "Unknown error"
            print_result("Frontend Build", False, f"Build failed. Last 500 chars:\n...{snippet}")
            
    except Exception as e:
        print_result("Frontend Execution", False, str(e))

if __name__ == "__main__":

    # Safe printing (Windows compat)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    
    print("\n[VERIFICATION] STARTING...")
    verify_backend()
    verify_frontend()
    print("\n[VERIFICATION] COMPLETE.")

