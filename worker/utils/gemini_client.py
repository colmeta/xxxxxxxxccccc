import os
import json
import base64
import requests
from google import genai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    """
    CLARITY PEARL ARBITER - MULTI-AI INTEGRATION
    Optimized for modern Google GenAI SDK and Groq.
    """
    
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        
        if not self.gemini_key and not self.groq_key:
            print("Warning: Neither GEMINI_API_KEY nor GROQ_API_KEY found.")
        
        if self.gemini_key:
            self.client = genai.Client(api_key=self.gemini_key)
            self.model_id = 'gemini-1.5-flash'
        
        # Groq Fallback
        self.groq_model = 'llama-3.1-8b-instant'
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    def _call_gemini(self, prompt, image_path=None):
        if not self.gemini_key: return None
        try:
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    image_data = f.read()
                
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=[
                        prompt,
                        {"mime_type": "image/png", "data": base64.b64encode(image_data).decode('utf-8')}
                    ]
                )
            else:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt
                )
            
            return response.text
        except Exception as e:
            print(f"[X] Gemini SDK Error: {e}")
            return None

    def _call_groq(self, prompt):
        if not self.groq_key: return None
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.groq_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        try:
            resp = requests.post(self.groq_url, headers=headers, json=payload, timeout=20)
            if resp.status_code != 200:
                 print(f"[X] Groq Status: {resp.status_code} | {resp.text[:200]}")
            resp.raise_for_status()
            return resp.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"[X] Groq Error: {e}")
            return None

    def _smart_call(self, prompt, image_path=None):
        """Attempts Gemini first (if image), then Groq, then Gemini (if no image)."""
        if image_path:
            return self._call_gemini(prompt, image_path)
        
        # Try Groq first for text if key exists (often faster/more reliable free tier)
        if self.groq_key:
            res = self._call_groq(prompt)
            if res: return res
        
        return self._call_gemini(prompt)

    async def analyze_visuals(self, query, image_path):
        prompt = f"Analyze this screenshot for the query: {query}. Return ONLY a JSON object: {{\"truth_score\": int, \"verdict\": \"string\"}}"
        return self._call_gemini(prompt, image_path)

    async def verify_data(self, query, data_payload, search_context=""):
        prompt = f"Verify this data for query '{query}': {data_payload}. Context: {search_context}. Format: {{\"truth_score\": int, \"verdict\": \"string\", \"is_verified\": bool}}"
        resp = self._smart_call(prompt)
        try:
            return json.loads(self._clean_json(resp))
        except: return None

    async def generate_outreach(self, lead_data, platform="email"):
        prompt = f"Draft elite outreach for {lead_data} on {platform}. Return ONLY message text."
        return self._smart_call(prompt) or "Arbiter Offline"

    async def dispatch_mission(self, user_prompt):
        prompt = f"Decompose user prompt into JSON list of search jobs: '{user_prompt}'. Platforms: linkedin, google_maps, generic. Format: [{{'query': '...', 'platform': '...', 'reasoning': '...'}}]"
        resp = self._smart_call(prompt)
        try:
            return json.loads(self._clean_json(resp))
        except: return []

    async def generate_content(self, prompt):
        """
        Compatibility method for ArbiterAgent.
        Returns the text content directly.
        """
        return self._smart_call(prompt) or ""

    def _clean_json(self, text):
        if not text: return None
        clean = text.strip().replace('```json', '').replace('```', '')
        return clean.strip()

gemini_client = GeminiClient()
