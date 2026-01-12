import os
import sys
from google import genai
from dotenv import load_dotenv

load_dotenv()

def test_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment.")
        # Check if it exists but is named differently? No, the code uses GEMINI_API_KEY.
        # Print all env keys to see what's there (excluding values)
        print("Available Env Keys:", list(os.environ.keys()))
        return

    print(f"DEBUG: Found API Key (Length: {len(api_key)})")

    try:
        client = genai.Client(api_key=api_key)
        
        # Comprehensive list of potential names
        candidates = [
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash-001",
            "gemini-1.5-flash-002",
            "gemini-1.5-flash-8b",
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
            "gemini-2.0-flash-exp"
        ]
        
        for model_name in candidates:
            try:
                # Smallest possible request
                response = client.models.generate_content(
                    model=model_name,
                    contents="Hi"
                )
                print(f"SUCCESS: {model_name} is active.")
            except Exception as e:
                err = str(e).lower()
                if "404" in err:
                    print(f"404: {model_name} not found.")
                elif "429" in err:
                    print(f"429: {model_name} quota exceeded.")
                else:
                    print(f"ERROR: {model_name} failed with: {e}")
                    
    except Exception as e:
        print(f"CRITICAL: SDK Init/Listing failed: {e}")

if __name__ == "__main__":
    test_models()
