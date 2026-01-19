import os
from dotenv import load_dotenv

def diagnose():
    print("--- Environment Diagnosis ---")
    # Try loading from various locations
    load_dotenv()
    print(f"Current Dir: {os.getcwd()}")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    print(f"GEMINI_API_KEY: {'Found (starts with ' + gemini_key[:5] + '...)' if gemini_key else 'MISSING'}")
    print(f"GROQ_API_KEY: {'Found (starts with ' + groq_key[:5] + '...)' if groq_key else 'MISSING'}")
    print(f"SUPABASE_KEY: {'Found' if supabase_key else 'MISSING'}")
    
    if not gemini_key:
        print("\nSearching for .env in parent directories...")
        load_dotenv("../.env")
        gemini_key = os.getenv("GEMINI_API_KEY")
        print(f"After ../.env load - GEMINI_API_KEY: {'Found' if gemini_key else 'MISSING'}")
        
    if not gemini_key:
        load_dotenv("../../.env")
        gemini_key = os.getenv("GEMINI_API_KEY")
        print(f"After ../../.env load - GEMINI_API_KEY: {'Found' if gemini_key else 'MISSING'}")

    if gemini_key:
        print("\nTesting Gemini connectivity...")
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            # Try to list models instead of calling one
            print("Listing models...")
            for m in client.models.list():
                print(f" - {m.name}")
        except Exception as e:
            print(f"Gemini Error: {e}")

    if groq_key:
        print("\nTesting Groq connectivity...")
        try:
            import requests
            url = "https://api.groq.com/openai/v1/models"
            headers = {"Authorization": f"Bearer {groq_key}"}
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                print("Groq Connection SUCCESS")
                models = resp.json().get('data', [])
                print(f"Available Groq Models: {[m['id'] for m in models[:3]]}")
            else:
                print(f"Groq Error: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Groq Error: {e}")

if __name__ == "__main__":
    diagnose()
