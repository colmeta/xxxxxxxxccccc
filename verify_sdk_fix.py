import asyncio
import os
import sys
from dotenv import load_dotenv

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

load_dotenv()

async def test():
    print(">>> Testing Gemini SDK Fix...")
    from worker.utils.gemini_client import gemini_client
    print(f">>> Gemini Key Present: {bool(os.getenv('GEMINI_API_KEY'))}")
    
    prompt = "Return exactly 'SDK ONLINE' if you can read this."
    
    print(">>> Calling generate_content...")
    try:
        result = await gemini_client.generate_content(prompt)
        print(f">>> Result: {result}")
        
        if result and "SDK ONLINE" in result.upper():
            print(">>> SUCCESS: SDK IS WORKING.")
        else:
            print(">>> FAILURE: UNEXPECTED RESPONSE.")
    except Exception as e:
        print(f">>> CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
