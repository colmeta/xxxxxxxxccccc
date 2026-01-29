import os
import json
import base64
import requests
from google import genai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# Robust .env search for parent directories (helpful for worker subdirs)
if not os.getenv("GEMINI_API_KEY"):
    load_dotenv("../../.env")
if not os.getenv("GEMINI_API_KEY"):
    load_dotenv("../.env")

class GeminiClient:
    """
    CLARITY PEARL ARBITER - MULTI-AI INTEGRATION
    Optimized for modern Google GenAI SDK and Groq.
    Now with persistent model fallback and detailed logging.
    """
    
    
    def __init__(self):
        # Load Zero-Cost Configuration explicitly
        load_dotenv("zero_cost.env")
        load_dotenv("../zero_cost.env") # Try parent dir if running from subdir
        
        self.ai_enabled_config = os.getenv("AI_VALIDATION_ENABLED", "true").lower() == "true"
        
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        
        # ZERO BUDGET / FREE TIER DETECTION
        if not self.ai_enabled_config:
            print("⚠️ Zero-Cost Mode Active: AI Validation Disabled via Configuration.")
            self.ai_available = False
            self.gemini_key = None
            self.groq_key = None
        else:
            # Normal key check
            self.ai_available = bool(
                (self.gemini_key and "YOUR_GEMINI" not in self.gemini_key) or 
                (self.groq_key and "gsk_" in self.groq_key)
            )
        
        if not self.ai_available:
            if self.ai_enabled_config:
                print("⚠️ Zero-Token Mode: AI keys missing. Swapping to Heuristic Intelligence (Free Tier).")
        else:
             print(f"AI Status: Gemini {'Active' if self.gemini_key else 'Missing'}, Groq {'Active' if self.groq_key else 'Missing'}")

        # MODEL HEALTH MAP (Dynamic failure tracking)
        self.health_map = {} 
        self.cooldown_period = 300 

        
        # Correct Gemini model IDs (Updated for GenAI SDK compatibility)
        # Correct Gemini model IDs (Updated for GenAI SDK compatibility)
        self.model_candidates = [
            'gemini-1.5-flash-latest',
            'gemini-1.5-flash-001',
            'gemini-1.5-flash', 
            'gemini-1.5-pro-latest',
            'gemini-1.5-pro-001',
            'gemini-1.5-pro',
            'gemini-pro' # Legacy fallback
        ]
        self.model_id = self.model_candidates[0]

        if self.gemini_key:
            try:
                self.client = genai.Client(api_key=self.gemini_key)
            except Exception as e:
                print(f"❌ Gemini SDK Init Error: {e}")
                self.gemini_key = None
        
        # Groq Fallback Tier (Multi-Model Rotation)
        self.groq_candidates = [
            'llama-3.3-70b-versatile',
            'llama-3.1-8b-instant',
            'mixtral-8x7b-32768'
        ]
        self.groq_model = self.groq_candidates[0]
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
        # Using RAW REST API to bypass SDK version/path issues
        url_base = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"
        
        for model in self.model_candidates:
            if not self._is_healthy(model):
                continue

            try:
                # Remove 'models/' prefix if present for raw URL construction
                clean_model = model.replace("models/", "")
                url = url_base.format(clean_model)
                headers = {"Content-Type": "application/json"}
                params = {"key": self.gemini_key}
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.1
                    }
                }

                if image_path and os.path.exists(image_path):
                     with open(image_path, "rb") as f:
                        image_data = base64.b64encode(f.read()).decode('utf-8')
                     payload["contents"][0]["parts"].append({
                        "inline_data": {
                            "mime_type": "image/png", 
                            "data": image_data
                        }
                     })

                response = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    # Parse response
                    try:
                        text = data['candidates'][0]['content']['parts'][0]['text']
                        if model in self.health_map: del self.health_map[model]
                        self.model_id = model
                        return text
                    except (KeyError, IndexError):
                         print(f"⚠️ Gemini Empty/Malformed Response: {data}")
                         continue
                else:
                    err_str = response.text.lower()
                    fail_type = "error"
                    if response.status_code == 404:
                         print(f"⚠️ Gemini '{model}' fallback: 404 Not Found.")
                         fail_type = "404"
                    elif response.status_code == 429:
                         print(f"⚠️ Gemini '{model}' fallback: 429 Quota Exceeded.")
                         fail_type = "429"
                    else:
                         print(f"[X] Gemini REST Error ({model}): {response.status_code} - {response.text[:200]}")
                    
                    self.health_map[model] = {"last_fail": datetime.now(), "fail_type": fail_type}
                    continue

            except Exception as e:
                print(f"[X] Gemini Request Error ({model}): {e}")
                continue
        
        return None

    def _call_groq(self, prompt):
        if not self.groq_key: 
            return None
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        
        for model in self.groq_candidates:
            print(f"DEBUG: Attempting Groq call with model {model}...")
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            try:
                resp = requests.post(self.groq_url, headers=headers, json=payload, timeout=20)
                if resp.status_code != 200:
                    print(f"[X] Groq '{model}' Status: {resp.status_code}")
                    continue
                content = resp.json()['choices'][0]['message']['content']
                if content:
                    self.groq_model = model
                    return content
            except Exception as e:
                print(f"[X] Groq Error ('{model}'): {e}")
                continue
        return None

    def _smart_call(self, prompt, image_path=None):
        """PRIMARY: Groq (faster, better free tier). BACKUP: Gemini."""
        
        # ZERO-BUDGET OPTIMIZATION: Fast fail if no AI available
        if not self.ai_available:
            return None
        
        # Images MUST use Gemini (Groq doesn't support vision)
        if image_path:
            print("🖼️ Vision request detected, using Gemini...")
            return self._call_gemini(prompt, image_path)
        
        # Text: Try Groq FIRST (Primary AI)
        if self.groq_key:
            res = self._call_groq(prompt)
            if res: 
                return res
        
        # Fallback to Gemini only if Groq unavailable/failed
        result = self._call_gemini(prompt)
        return result

    async def analyze_visuals(self, query, image_path):
        prompt = f"Analyze this screenshot for the query: {query}. Return ONLY a JSON object: {{\"truth_score\": int, \"verdict\": \"string\"}}"
        return self._call_gemini(prompt, image_path)

    async def verify_data(self, query, data_payload, search_context=""):
        prompt = f"Verify this data for query '{query}': {data_payload}. Context: {search_context}. Format: {{\"truth_score\": int, \"verdict\": \"string\", \"is_verified\": bool}}"
        resp = self._smart_call(prompt)
        try:
            return json.loads(self._clean_json(resp))
        except: 
            # Heuristic Fallback (Phase 6 persistence)
            is_valid = bool(data_payload.get('name') or data_payload.get('title'))
            return {
                "truth_score": 75 if is_valid else 20, 
                "verdict": "Heuristic match (AI Offline)", 
                "is_verified": is_valid
            }

    async def generate_outreach(self, lead_data, platform="email"):
        prompt = f"Draft elite outreach for {lead_data} on {platform}. Return ONLY message text."
        return self._smart_call(prompt) or "Arbiter Offline"

    async def dispatch_mission(self, user_prompt):
        """
        PHASE 6: THE ORACLE - SEMANTIC SWARM INTELLIGENCE
        Converts a single prompt into a cluster of high-intent search jobs.
        """
        prompt = f"""
        YOU ARE THE ORACLE (Phase 6 Strategic Intelligence).
        TASK: Decompose this user prompt into a SEMANTIC SWARM of search jobs: "{user_prompt}"
        
        STRATEGY:
        1. Identify the core Persona (e.g., Realtor).
        2. Generate 3-5 Semantic Variants (Synonyms, Acronyms, Related Job Titles).
        3. Localize queries if a location is mentioned.
        4. Match with the best Platform: 
           - 'linkedin' for people/roles.
           - 'google_maps' for physical businesses.
           - 'generic' for general web research.
        
        Return ONLY a JSON list of objects:
        [{{
            "query": "The optimized search string",
            "platform": "linkedin|google_maps|generic",
            "reasoning": "Brief explanation of why this synonym/variant was chosen"
        }}]
        """
        resp = self._smart_call(prompt)
        try:
            return json.loads(self._clean_json(resp))
        except: 
            print(f"⚠️ Oracle Parsing Error. Triggering AGGRESSIVE SWARM Fallback.")
            # Guerilla Warfare: Swarm ALL platforms with specialized pivots
            return [
                {"query": user_prompt, "platform": "linkedin", "reasoning": "Primary Dork (Aggressive)"},
                {"query": user_prompt, "platform": "google_maps", "reasoning": "Local Intel (Aggressive)"},
                {"query": f"{user_prompt} on twitter", "platform": "twitter", "reasoning": "Social Pulse (Aggressive)"},
                {"query": f"{user_prompt} on instagram", "platform": "instagram", "reasoning": "Visual Intel (Aggressive)"},
                {"query": f"{user_prompt} on tiktok", "platform": "tiktok", "reasoning": "Viral Intel (Aggressive)"},
                {"query": f"site:reddit.com {user_prompt}", "platform": "generic", "reasoning": "Community Intel (Aggressive)"}
            ]

    async def generate_content(self, prompt):
        """
        Compatibility method for ArbiterAgent.
        Returns the text content directly.
        """
        return self._smart_call(prompt) or ""

    def _clean_json(self, text):
        if not text: return None
        # Robust Regex-based JSON extraction
        import re
        # Try to find content between ```json ... ```
        code_block = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if code_block:
            return code_block.group(1).strip()
        
        # Try to find content between { ... } or [ ... ]
        json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()

        # Fallback to simple cleaning
        clean = text.strip().replace('```json', '').replace('```', '')
        return clean.strip()

gemini_client = GeminiClient()
