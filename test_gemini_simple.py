"""Simple Gemini Model Test"""
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Gemini API...")
gemini_key = os.getenv("GEMINI_API_KEY")

if not gemini_key:
    print("ERROR: GEMINI_API_KEY not found in environment")
    exit(1)

print(f"API Key found: {gemini_key[:10]}...")

try:
    from google import genai
    print("Genai module imported successfully")
    
    client = genai.Client(api_key=gemini_key)
    print("Client created successfully")
    
    # Test models one by one
    test_models = [
        'gemini-1.5-flash-latest',
        'gemini-1.5-flash',
        'gemini-1.5-flash-8b-latest',
        'gemini-2.0-flash-exp',
        'gemini-1.5-pro-latest',
        'gemini-1.5-pro'
    ]
    
    print("\nTesting models:")
    for model_name in test_models:
        try:
            print(f"\n  Testing: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents="Say OK"
            )
            if response and response.text:
                print(f"    SUCCESS: {response.text[:20]}")
            else:
                print(f"    FAIL: Empty response")
        except Exception as e:
            error_str = str(e)
            if "404" in error_str:
                print(f"    FAIL: 404 - Model not found")
            elif "429" in error_str:
                print(f"    FAIL: 429 - Quota exceeded")
            else:
                print(f"    FAIL: {error_str[:100]}")
                
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
