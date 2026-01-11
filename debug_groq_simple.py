import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print(f"Groq Key: {bool(GROQ_API_KEY)}")

if not GROQ_API_KEY:
    print("No Groq Key found.")
    exit(1)

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}
data = {
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "Hello Groq!"}]
}

try:
    print(f"Sending request to {url}...")
    resp = requests.post(url, headers=headers, json=data, timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
