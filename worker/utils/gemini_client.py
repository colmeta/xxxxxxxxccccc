from google import genai
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    """
    CLARITY PEARL ARBITER - GEMINI INTEGRATION
    Optimized for Gemini 1.5 Flash to maintain near-zero costs.
    """
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ Warning: GEMINI_API_KEY not found in environment.")
        
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model_id = 'gemini-1.5-flash-8b'

    async def analyze_visuals(self, query, image_path):
        """
        VISION-X: Analyze a screenshot using Gemini Vision.
        """
        if not self.client:
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
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt, genai.types.Part.from_bytes(data=img_data, mime_type="image/png")]
            )
            return response.text
        except Exception as e:
            print(f"❌ Gemini Vision Error: {e}")
            return None

    async def verify_data(self, query, data_payload, search_context=""):
        """
        Ask the AI to verify if the scraped data matches the query and feels 'Truthful'.
        """
        prompt = f"""
        You are the CLARITY PEARL ARBITER, a supreme data verification agent.
        
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
        if not self.client:
            return "Arbiter Offline"
            
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
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"❌ Ghostwriter Error: {e}")
            return "Failed to generate personalization."

    async def dispatch_mission(self, user_prompt):
        """
        THE ORACLE: Convert NL prompt into structured mission steps.
        """
        if not self.client:
            return []
            
        prompt = f"""
        You are THE ORACLE, the supreme intelligence of the CLARITY PEARL.
        CURRENT TIME: {datetime.now().strftime('%Y-%m-%d')}
        USER PROMPT: "{user_prompt}"
        
        TASK:
        Decompose this prompt into a search MISSION. A perfect mission uses multiple platforms 
        in synergy to verify and enrich data.
        
        SYNERGY RULES:
        1. For B2B/People: Start with 'linkedin', verify with 'google_news'.
        2. For Local/Physical: Start with 'google_maps', enrich with 'facebook' or 'tiktok'.
        3. For Technical: Use 'reddit' and 'generic'.
        
        Supported Platforms: linkedin, google_news, amazon, real_estate, job_scout, reddit, tiktok, facebook, google_maps, generic.
        Supported Compliance Modes: standard, strict, gdpr.
        
        RETURN ONLY A JSON LIST OF JOBS:
        [
            {{
                "query": "Full search query for this step",
                "platform": "platform_name",
                "compliance_mode": "standard|strict|gdpr",
                "boost": boolean (true for high priority/initial steps),
                "reasoning": "Briefly why this platform was chosen"
            }}
        ]
        
        Mission Example: "Researching autonomous drone companies in SF"
        -> [
            {{"query": "autonomous drone startups San Francisco", "platform": "generic", "compliance_mode": "standard", "boost": true, "reasoning": "Broad discovery"}},
            {{"query": "autonomous drone startups San Francisco hiring", "platform": "job_scout", "compliance_mode": "standard", "boost": false, "reasoning": "Verify scaling"}},
            {{"query": "drone startup founders San Francisco", "platform": "linkedin", "compliance_mode": "strict", "boost": false, "reasoning": "Target identification"}}
        ]
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            # Remove any markdown formatting if Gemini includes it
            text = response.text.strip().replace('```json', '').replace('```', '')
            import json
            return json.loads(text)
        except Exception as e:
            print(f"❌ Oracle Dispatch Error: {e}")
            return []

gemini_client = GeminiClient()
