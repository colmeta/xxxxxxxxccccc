import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def test_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found.")
        return

    client = genai.Client(api_key=api_key)
    
    # Try these name formats
    candidates = [
        "gemini-1.5-flash",
        "models/gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-2.0-flash-exp"
    ]
    
    for model_name in candidates:
        print(f"Testing model: {model_name}...")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Hi"
            )
            print(f"✅ Success with {model_name}")
        except Exception as e:
            err = str(e).lower()
            if "404" in err:
                print(f"❌ 404 Not Found for {model_name}")
            elif "429" in err:
                print(f"⚠️ 429 Quota Exceeded for {model_name}")
            else:
                print(f"❓ Other error for {model_name}: {e}")

if __name__ == "__main__":
    test_models()
