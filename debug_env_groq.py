import os
from dotenv import load_dotenv

# Try loading from various locations to match GeminiClient logic
load_dotenv()
load_dotenv(".env")
load_dotenv("worker/.env")
load_dotenv("../.env")

print("--- Environment Check ---")
print(f"Current Working Directory: {os.getcwd()}")
print(f"GEMINI_API_KEY present: {bool(os.getenv('GEMINI_API_KEY'))}")
print(f"GROQ_API_KEY present: {bool(os.getenv('GROQ_API_KEY'))}")
print(f"SCRAPER_API_KEY present: {bool(os.getenv('SCRAPER_API_KEY'))}")
print(f"PROXY_LIST_PATH: {os.getenv('PROXY_LIST_PATH')}")
print(f"SUPABASE_URL present: {bool(os.getenv('SUPABASE_URL'))}")

print("\n--- Groq Connectivity Check ---")
if os.getenv("GROQ_API_KEY"):
    try:
        import requests
        key = os.getenv("GROQ_API_KEY")
        url = "https://api.groq.com/openai/v1/models"
        headers = {"Authorization": f"Bearer {key}"}
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Groq API Valid: {resp.status_code == 200}")
        if resp.status_code != 200:
            print(f"Groq Error: {resp.text}")
    except Exception as e:
        print(f"Groq Connectivity Failed: {e}")
else:
    print("Skipping Groq check (Key missing)")
