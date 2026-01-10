
import asyncio
from worker.utils.gemini_client import gemini_client

async def main():
    print("Testing Gemini Client Fix...")
    try:
        # Test 1: Check attribute
        print(f"Model ID: {gemini_client.gemini_model}")
        
        # Test 2: Check new method existence
        if not hasattr(gemini_client, 'generate_content'):
            print("❌ FAILURE: Method 'generate_content' missing.")
            return

        # Test 3: Attempt call (optional, but good)
        # We catch the error in case of API Key failure, but we want to know if the CALL itself works (no AttributeError)
        try:
            print("Sending test prompt...")
            res = await gemini_client.generate_content("Hello, say 'Verified' if you hear me.")
            print(f"Gemini Response: {res}")
        except Exception as e:
            # If it's a 401/403 (Keys), that's fine for code verification. 
            # If it's AttributeError again, that's bad.
            print(f"API Call Result: {e}")

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
