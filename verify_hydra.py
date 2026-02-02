
import asyncio
import os
import sys

# Add worker to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'worker'))

from worker.utils.hydra_client import hydra_client

async def test_hydra():
    print("🧪 Testing Hydra Protocol Connectivity...")
    
    # Test 1: Check Keys
    print("\n🔑 key Status:")
    for provider, key in hydra_client.api_keys.items():
        status = "✅ Loaded" if key else "❌ Missing (Will skip)"
        print(f"   - {provider}: {status}")

    # Test 2: Dry Run Search (Should fail gracefully if no keys)
    print("\n🔍 Executing Dry Run Search ('test')...")
    try:
        results = await hydra_client.search("test query", type="search", num=1)
        if results:
            print(f"   ✅ Success! Provider returned {len(results)} results.")
        else:
            print("   ⚠️ No API results (Expected if no keys are set). Fallback logic in BaseDorkEngine will trigger.")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_hydra())
