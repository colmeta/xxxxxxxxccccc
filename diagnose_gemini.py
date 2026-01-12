import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment.")
        return

    try:
        client = genai.Client(api_key=api_key)
        print("--- Available Models ---")
        models = client.models.list()
        for m in models:
            print(f"- ID: {m.name}, Name: {m.display_name}, Methods: {m.supported_generation_methods}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    list_models()
