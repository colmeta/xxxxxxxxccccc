import os
import sys
from google import genai
from dotenv import load_dotenv

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

load_dotenv()

def test():
    print(">>> Testing Gemini SDK Fix (SYNC)...")
    api_key = os.getenv("GEMINI_API_KEY")
    print(f">>> Gemini Key Present: {bool(api_key)}")
    
    client = genai.Client(api_key=api_key)
    
    print(">>> Calling generate_content (blocking)...")
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash-8b',
            contents='Return exactamente "SDK SYNC ONLINE" si puedes leer esto.'
        )
        print(f">>> Response: {response.text}")
        
        if response.text and "SDK SYNC ONLINE" in response.text.upper():
            print(">>> SUCCESS: SDK SYNC IS WORKING.")
        else:
            print(">>> FAILURE: UNEXPECTED RESPONSE.")
    except Exception as e:
        print(f">>> CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test()
