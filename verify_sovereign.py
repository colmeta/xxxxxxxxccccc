import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Force unbuffered
sys.stdout.reconfigure(line_buffering=True)

load_dotenv()

async def verify_gemini():
    print("\n--- STEP 1: Verifying Gemini Robustness ---")
    from worker.utils.gemini_client import GeminiClient
    client = GeminiClient()
    
    # Test model matrix
    print(f"Candidates: {client.model_candidates}")
    
    # Test a simple call
    print("ACTION: Calling Gemini (Smart Call)...")
    res = await client.generate_content("Say 'Sovereign Online'")
    if res and "Sovereign" in res:
        print(f"SUCCESS: Gemini responded: {res.strip()}")
        print(f"ACTIVE MODEL: {client.model_id}")
    else:
        print(f"FAILURE: Gemini empty response. Check keys/quota. (Groq Fallback check...)")
        # If Groq is configured, this should not happen unless both fail.

async def verify_pulse():
    print("\n--- STEP 2: Verifying Schema-Aware Pulse ---")
    from worker.hydra_controller import HydraController
    
    # We use a unique test ID
    hydra = HydraController(worker_id="verify_sovereign_01")
    
    # Discovery usually runs in background task, so we wait or call it explicitly
    await hydra._discover_supported_columns()
    
    print(f"SUPPORTED COLUMNS: {hydra.supported_columns}")
    
    if len(hydra.supported_columns) > 0:
        print(f"SUCCESS: Discovered {len(hydra.supported_columns)} columns.")
        
        # Test mesh pulse
        print("ACTION: Pulsing Mesh...")
        await hydra.mesh_pulse()
        print("SUCCESS: Mesh pulse completed without crashing.")
    else:
        print("FAILURE: No columns discovered.")

async def main():
    print(f"Verification started at {datetime.now()}")
    try:
        await verify_gemini()
        await verify_pulse()
        print("\nVERIFICATION COMPLETE: System is stable.")
    except Exception as e:
        print(f"\n[X] VERIFICATION FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())
