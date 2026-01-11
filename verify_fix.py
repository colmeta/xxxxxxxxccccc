import asyncio
from worker.utils.arbiter import arbiter
import sys

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

async def test():
    print("Testing Arbiter Fix...")
    
    lead_data = {
        "name": "Dr. Smith",
        "company": "Ohio Medical",
        "title": "Chief Surgeon",
        "metadata": {"signals": "Hiring now"}
    }
    
    print("Calling predict_intent...")
    result = await arbiter.predict_intent(lead_data)
    print(f"Result: {result}")
    
    if result.get("confidence", 0) > 0:
        print("SUCCESS: Valid response received.")
    elif result.get("reasoning") == "Error in predictive analysis":
        print("SUCCESS: Graceful fallback triggered (no crash).")
    else:
        print("FAILURE: Unexpected state.")

if __name__ == "__main__":
    asyncio.run(test())
