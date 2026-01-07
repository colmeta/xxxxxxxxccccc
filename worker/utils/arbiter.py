import json
import re
import asyncio
from .gemini_client import gemini_client

class ArbiterAgent:
    """
    The Arbiter Agent is responsible for "Sense-Checking" scraped data.
    Assigned to Workstream B: THE JUDGE.
    """
    
    def __init__(self):
        self.verdict_log = []

    async def score_lead(self, target_query, lead_data, search_context=""):
        """
        AI-Powered scoring engine with Temporal Awareness.
        Factors in 'Current Time' to detect stale news or offers.
        """
        """
        AI-Powered scoring engine using Gemini 1.5 Flash.
        Falls back to heuristics if AI fails.
        """
        # Attempt AI Verification
        try:
            ai_response_raw = await gemini_client.verify_data(target_query, lead_data, search_context)
            
            if ai_response_raw:
                # Basic JSON sanitization (remove markdown blocks if Gemini added them)
                clean_json = re.sub(r'```json\n?|\n?```', '', ai_response_raw).strip()
                ai_data = json.loads(clean_json)
                return ai_data.get('truth_score', 0), ai_data.get('verdict', "AI Verdict Unavailable")
        except Exception as e:
            print(f"⚠️ Arbiter AI Fallback Triggered: {e}")

    async def score_visual_lead(self, target_query, screenshot_path):
        """
        VISION-X: Analyze product images or social posts via Gemini Vision.
        Used for Instagram (OCR) and E-Commerce (Visual Match).
        """
        try:
            print(f"⚖️ Arbiter Vision-X: Analyzing sensory evidence {screenshot_path}...")
            ai_response = await gemini_client.analyze_visuals(target_query, screenshot_path)
            if ai_response:
                clean_json = re.sub(r'```json\n?|\n?```', '', ai_response).strip()
                ai_data = json.loads(clean_json)
                return ai_data.get('truth_score', 0), ai_data.get('verdict', "Vision Verdict Unvailable")
        except Exception as e:
            print(f"❌ Vision-X Failure: {e}")
            return 0, "Visual Truth Verification Failed"

        # --- HEURISTIC FALLBACK (Hardened) ---
        score = 0
        rules_applied = []
        
        query_terms = set(re.findall(r'\w+', target_query.lower()))
        lead_text = json.dumps(lead_data).lower()
        
        matches = sum(1 for term in query_terms if term in lead_text)
        relevance_score = (matches / len(query_terms)) * 40 if query_terms else 0
        score += relevance_score
        rules_applied.append(f"Relevance: +{int(relevance_score)}")

        # Completeness Check (Hardened)
        critical_fields = ['name', 'title', 'company']
        present_fields = [f for f in critical_fields if lead_data.get(f) and len(str(lead_data.get(f))) > 1]
        completeness_score = (len(present_fields) / len(critical_fields)) * 40
        score += completeness_score
        rules_applied.append(f"Completeness: +{int(completeness_score)}")

        # Trust Signals
        if lead_data.get('verified') or 'http' in str(lead_data.get('source_url', '')):
            score += 20
            rules_applied.append("Trust: +20 (Source Signal)")
        
        # --- NEW: TEMPORAL FRESHNESS CHECK (Heuristic) ---
        # Look for "ago" or year markers
        current_year = "2026"
        stale_markers = ["2022", "2021", "2020", "2019", "2018", "years ago"]
        signal_text = json.dumps(lead_data).lower()
        
        for marker in stale_markers:
            if marker in signal_text:
                score -= 30
                rules_applied.append(f"Decay: -30 (Stale Signal: {marker})")
                break
        
        if "hours ago" in signal_text or "minutes ago" in signal_text or "today" in signal_text:
            score += 15
            rules_applied.append("Freshness: +15 (Near-Live Signal)")

        final_score = max(0, min(int(score), 100))
        verdict = f"H-Score {final_score}/100 (Fallback) | {', '.join(rules_applied)}"
        
        return final_score, verdict

    async def predict_intent(self, lead_data):
        """
        THE ORACLE ENGINE: Identify future-looking intent and growth signals.
        Analyzes data for 'Velocity' and 'Scaling' indicators.
        """
        try:
            prompt = f"""
            Analyze this lead data for PREDICTIVE AGITATORS (signals of future change).
            LEAD DATA: {lead_data}
            
            SCORING CRITERIA:
            1. Intent Score (0-100): Immediate need for outreach.
            2. Predictive Growth Score (0-100): Likelihood of massive scaling, hiring, or funding in next 6 months.
            
            LOOK FOR:
            - Growth hiring (e.g., 'We are hiring', 'Team expansion')
            - New product launches or expansion markers.
            - Funding rumors or recent rounds.
            - Tech stack upgrades or adoption of mature tools.
            
            Return ONLY a JSON object: 
            {{
                "intent_score": int,
                "predictive_growth_score": int,
                "oracle_signal": "string (The narrative signal, e.g., 'Viral Growth Spike')",
                "confidence": float,
                "reasoning": "string (Why did you give these scores?)"
            }}
            """
            ai_response = await gemini_client.model.generate_content(prompt)
            clean_json = re.sub(r'```json\n?|\n?```', '', ai_response.text).strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"❌ Oracle Predictive Error: {e}")
            return {
                "intent_score": 0, 
                "predictive_growth_score": 0, 
                "oracle_signal": "Baseline Intelligence", 
                "confidence": 0.5,
                "reasoning": "Error in predictive analysis"
            }

    async def recursive_verdict(self, lead_data):
        """
        THE SLEUTH: Generate a follow-up verification query.
        If we found them on LinkedIn, maybe check for a recent News event or a Website mention.
        """
        prompt = f"""
        LEAD DATA: {lead_data}
        
        TASK:
        Generate a SINGLE follow-up search query to verify this lead's current activity or role 
        on a DIFFERENT platform (e.g., Google News, Website, or Twitter).
        
        Return ONLY the query string.
        """
        try:
             # We reuse the same model for speed/cost
             response = await self.gemini_client.model.generate_content(prompt)
             return response.text.strip()
        except:
             return f"verify {lead_data.get('name')} {lead_data.get('company')}"

arbiter = ArbiterAgent()
