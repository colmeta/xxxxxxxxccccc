"""
DIAGNOSTIC SCRIPT - AI API Root Cause Analysis
This script will:
1. Test Gemini API key and list available models
2. Test Groq API key and list available models
3. Make actual test calls to verify functionality
4. Report EXACTLY what's wrong
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("AI API DIAGNOSTIC - ROOT CAUSE ANALYSIS")
print("="*60)

# 1. CHECK ENVIRONMENT VARIABLES
print("\n[1] CHECKING ENVIRONMENT VARIABLES...")
gemini_key = os.getenv("GEMINI_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

print(f"   GEMINI_API_KEY: {'[OK] Found' if gemini_key else '[!!] MISSING'}")
print(f"   GROQ_API_KEY:   {'[OK] Found' if groq_key else '[!!] MISSING'}")

# 2. TEST GEMINI API
print("\n[2] TESTING GEMINI API...")
if gemini_key:
    try:
        from google import genai
        client = genai.Client(api_key=gemini_key)
        
        # Try to list models
        try:
            print("   Attempting to list available models...")
            models = client.models.list()
            print(f"   ✓ Successfully connected to Gemini API")
            print(f"   Available models:")
            for model in models:
                print(f"      - {model.name}")
        except Exception as list_err:
            print(f"   ⚠ Could not list models: {list_err}")
        
        # Test each model name from our config
        test_models = [
            'gemini-1.5-flash-latest',
            'gemini-1.5-flash',
            'gemini-1.5-flash-8b-latest',
            'gemini-2.0-flash-exp'
        ]
        
        print("\n   Testing model names:")
        for model_name in test_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents="Say 'OK'"
                )
                if response and response.text:
                    print(f"      ✓ {model_name}: WORKS")
                else:
                    print(f"      ✗ {model_name}: Empty response")
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg or "not found" in error_msg.lower():
                    print(f"      ✗ {model_name}: 404 NOT FOUND")
                elif "429" in error_msg or "quota" in error_msg.lower():
                    print(f"      ⚠ {model_name}: 429 QUOTA EXCEEDED")
                else:
                    print(f"      ✗ {model_name}: {error_msg[:80]}")
                    
    except Exception as sdk_err:
        print(f"   ✗ Gemini SDK Error: {sdk_err}")
else:
    print("   ✗ Skipping - API key not found")

# 3. TEST GROQ API
print("\n[3] TESTING GROQ API...")
if groq_key:
    test_models = [
        'llama-3.3-70b-versatile',
        'llama-3.1-8b-instant',
        'mixtral-8x7b-32768'
    ]
    
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }
    
    # List models
    try:
        list_resp = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=10)
        if list_resp.status_code == 200:
            print(f"   ✓ Successfully connected to Groq API")
            models = list_resp.json()
            print(f"   Available models:")
            for model in models.get('data', []):
                print(f"      - {model.get('id')}")
        else:
            print(f"   ⚠ Could not list models: HTTP {list_resp.status_code}")
    except Exception as list_err:
        print(f"   ⚠ Could not list models: {list_err}")
    
    print("\n   Testing model names:")
    for model_name in test_models:
        try:
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Say 'OK'"}],
                "temperature": 0.1
            }
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                               headers=headers, json=payload, timeout=10)
            
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content']
                print(f"      ✓ {model_name}: WORKS (response: {content[:20]})")
            else:
                print(f"      ✗ {model_name}: HTTP {resp.status_code} - {resp.text[:80]}")
        except Exception as e:
            print(f"      ✗ {model_name}: {str(e)[:80]}")
else:
    print("   ✗ Skipping - API key not found")

# 4. RECOMMENDATIONS
print("\n[4] RECOMMENDATIONS:")
print("="*60)

if not gemini_key and not groq_key:
    print("   ✗ CRITICAL: Both API keys are missing!")
    print("   → Add GEMINI_API_KEY and/or GROQ_API_KEY to your .env file")
elif not gemini_key:
    print("   ⚠ Gemini API key missing - fallback to Groq only")
elif not groq_key:
    print("   ⚠ Groq API key missing - fallback to Gemini only")
else:
    print("   ✓ Both API keys are present")
    print("   → Check the test results above to see which models work")

print("\n" + "="*60)
print("DIAGNOSIS COMPLETE")
print("="*60)
