import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not found in .env")
    exit(1)

models = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-flash-8b", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
endpoints = ["v1", "v1beta"]

for endpoint in endpoints:
    for model in models:
        url = f"https://generativelanguage.googleapis.com/{endpoint}/models/{model}:generateContent?key={api_key}"
        data = {"contents": [{"parts": [{"text": "hi"}]}]}
        try:
            resp = requests.post(url, json=data, timeout=5)
            print(f"[{endpoint}][{model}] Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"   -> SUCCESS!")
                exit(0)
        except Exception as e:
            print(f"[{endpoint}][{model}] Error: {e}")
