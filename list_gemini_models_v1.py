import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not found in .env")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"

try:
    resp = requests.get(url)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        models = resp.json().get('models', [])
        for m in models:
            print(f"- {m['name']}")
    else:
        print(f"Error: {resp.text}")
except Exception as e:
    print(f"Exception: {e}")
