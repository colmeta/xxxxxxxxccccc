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
    Now with persistent model fallback and detailed logging.
    """
    
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        
        # MODEL HEALTH MAP (Dynamic failure tracking)
        self.health_map = {} # {model_id: {"last_fail": timestamp, "fail_type": "429"|"404"|"error"}}
        self.cooldown_period = 300 # 5 minutes for 429s
        
        print(f"DEBUG: GeminiClient Init - Gemini Key: {bool(self.gemini_key)}, Groq Key: {bool(self.groq_key)}")
        
        # Comprehensive Matrix: covers all known variants to eliminate 404s
        self.model_candidates = [
            'gemini-1.5-flash-latest',
            'gemini-1.5-flash',
            'gemini-1.5-flash-002',
            'gemini-1.5-flash-8b',
            'gemini-2.0-flash-exp',
            'gemini-1.5-pro'
        ]
        self.model_id = self.model_candidates[0]

        if self.gemini_key:
            try:
                self.client = genai.Client(api_key=self.gemini_key)
            except Exception as e:
                print(f"❌ Gemini SDK Init Error: {e}")
                self.gemini_key = None
        
        # Groq Fallback (High Reliability Tier)
        self.groq_model = 'llama-3.1-8b-instant'
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    def _is_healthy(self, model):
        """Checks if a model is currently in cooldown."""
        if model not in self.health_map: return True
        fail_data = self.health_map[model]
        if fail_data['fail_type'] == "404": return False # Permanent failure for this session
        
        seconds_since = (datetime.now() - fail_data['last_fail']).total_seconds()
        if fail_data['fail_type'] == "429" and seconds_since < self.cooldown_period:
            return False
        return True

    def _call_gemini(self, prompt, image_path=None):
        if not self.gemini_key: return None
        
        # Try models in order, skipping unhealthy ones
        for model in self.model_candidates:
            if not self._is_healthy(model):
                continue

            try:
                if image_path and os.path.exists(image_path):
                    with open(image_path, "rb") as f:
                        image_data = f.read()
                    
                    response = self.client.models.generate_content(
                        model=model,
                        contents=[
                            prompt,
                            {"mime_type": "image/png", "data": base64.b64encode(image_data).decode('utf-8')}
                        ]
                    )
                else:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt
                    )
                
                if response and response.text:
                    # Successful call clears health record
                    if model in self.health_map: del self.health_map[model]
                    self.model_id = model
                    return response.text
                continue
            except Exception as e:
                err_str = str(e).lower()
                fail_type = "error"
                if "404" in err_str or "not found" in err_str:
                    print(f"⚠️ Gemini '{model}' fallback: 404 Not Found.")
                    fail_type = "404"
                elif "429" in err_str or "quota" in err_str:
                    print(f"⚠️ Gemini '{model}' fallback: 429 Quota Exceeded.")
                    fail_type = "429"
                else:
                    print(f"[X] Gemini SDK Error ({model}): {e}")
                
                self.health_map[model] = {"last_fail": datetime.now(), "fail_type": fail_type}
                continue
        
        return None

    def _call_groq(self, prompt):
        if not self.groq_key: 
            print("DEBUG: Groq Key missing, skipping Groq.")
            return None
            
        print(f"DEBUG: Attempting Groq call with model {self.groq_model}...")
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
                 return None
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
        
        # If Groq fails or no key, try Gemini
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
