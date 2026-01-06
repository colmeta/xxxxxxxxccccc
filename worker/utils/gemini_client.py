import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    """
    NEXUS ARBITER - GEMINI INTEGRATION
    Optimized for Gemini 1.5 Flash-8B to maintain near-zero costs.
    """
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ Warning: GEMINI_API_KEY not found in environment.")
        
        genai.configure(api_key=api_key)
        self.api_key = api_key
        # Use flash-8b for maximum speed and minimum cost (FREE on many tiers)
        self.model = genai.GenerativeModel('gemini-1.5-flash-8b')

    async def analyze_visuals(self, query, image_path):
        """
        VISION-X: Analyze a screenshot using Gemini Vision.
        """
        if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY":
             return None

        try:
            # Upload the file to Gemini
            with open(image_path, "rb") as f:
                img_data = f.read()
            
            # Simple prompt for vision-based data extraction
            prompt = f"""
            Analyze this screenshot for the query: {query}.
            CURRENT TIME (REFERENCE): {datetime.now().strftime('%Y-%m-%d')}
            Extract the primary data point (name, price, or social handle).
            TEMPORAL CHECK: If this is an offer/news, check for dates. Is it stale?
            Determine the 'truth_score' (0-100) based on how well it matches the query AND how fresh it is.
            Provide a short 'verdict'.
            Return ONLY a JSON object: {{"truth_score": int, "verdict": "string"}}
            """
            
            # Note: This assumes the library supports simple image content in generate_content
            # Based on standard google-generativeai usage:
            response = self.model.generate_content([prompt, {"mime_type": "image/png", "data": img_data}])
            return response.text
        except Exception as e:
            print(f"❌ Gemini Vision Error: {e}")
            return None

    async def verify_data(self, query, data_payload, search_context=""):
        """
        Ask the AI to verify if the scraped data matches the query and feels 'Truthful'.
        """
        prompt = f"""
        You are the NEXUS ARBITER, a supreme data verification agent.
        
        TARGET SEARCH QUERY: {query}
        CURRENT TIME (REFERENCE): {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        SCRAPED DATA (JSON): {data_payload}
        SEARCH RESULTS CONTEXT: {search_context}
        
        TASK:
        1. Compare the scraped data against the query and search context.
        2. Identify any hallucinations or stale information.
        3. Assign a 'Truth Score' from 0 to 100.
        4. Provide a brief 'Verdict' explaining the score.
        
        FORMAT YOUR RESPONSE AS JSON:
        {{
            "truth_score": int,
            "verdict": "string",
            "is_verified": bool (true if score > 75)
        }}
        """
        
    async def generate_outreach(self, lead_data, platform="email"):
        """
        GHOSTWRITER: Draft personalized outreach based on verified data.
        """
        prompt = f"""
        You are THE GHOSTWRITER, a elite corporate negotiator.
        LEAD DATA: {lead_data}
        PLATFORM: {platform}
        
        TASK:
        Draft a high-conversion, hyper-personalized outreach message. 
        Refer to their specific title, company, and any signals (hiring, news, location).
        Keep it brief, professional, and slightly provocative.
        
        Return ONLY the text of the message.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"❌ Ghostwriter Error: {e}")
            return "Failed to generate personalization."

    async def dispatch_mission(self, user_prompt):
        """
        THE ORACLE: Convert NL prompt into structured mission steps.
        """
        prompt = f"""
        You are THE ORACLE, the supreme intelligence of the DATAVAULT.
        USER PROMPT: "{user_prompt}"
        
        TASK:
        Decompose this prompt into a search MISSION.
        Each mission can have multiple JOBS.
        Supported Platforms: linkedin, google_news, amazon, real_estate, job_scout, reddit, tiktok, facebook, google_maps, generic.
        Supported Compliance Modes: standard, strict.
        
        RETURN ONLY A JSON LIST OF JOBS:
        [
            {{
                "query": "string",
                "platform": "string",
                "compliance_mode": "string",
                "boost": boolean
            }}
        ]
        
        Example: "Find me 5 AI startups in London and check their news"
        -> [
            {{"query": "AI startups London", "platform": "generic", "compliance_mode": "standard", "boost": false}},
            {{"query": "AI startups London news", "platform": "google_news", "compliance_mode": "strict", "boost": true}}
        ]
        """
        try:
            response = self.model.generate_content(prompt)
            # Remove any markdown formatting if Gemini includes it
            text = response.text.strip().replace('```json', '').replace('```', '')
            import json
            return json.loads(text)
        except Exception as e:
            print(f"❌ Oracle Dispatch Error: {e}")
            return []

gemini_client = GeminiClient()
