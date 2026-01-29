
import asyncio
import os
import sys
import codecs

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Ensure current directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hydra_controller import HydraController

async def verify_fix():
    print("🧪 Starting Verification Test...")
    
    # Mock HydraController
    controller = HydraController(worker_id="test_worker")
    # Force supabase to None to avoid connection attempts if env vars are present but invalid
    # controller.supabase = None 
    
    # Mock Job Data
    import uuid
    job_data = {
        "id": str(uuid.uuid4()),
        "target_query": "Roofing Companies in Austin",
        "target_platform": "google_maps",
        "search_metadata": {"category": "Construction"},
        "compliance": {"ab_test_group": "A"}
    }
    
    print(f"🚀 Launching test job: {job_data['target_query']} (ID: {job_data['id']})")
    
    try:
        await controller.process_job_with_browser(job_data, launch_args=["--headless"])
        print("✅ Test execution completed without crashing.")
    except Exception as e:
        print(f"❌ Test Failed with Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(verify_fix())
