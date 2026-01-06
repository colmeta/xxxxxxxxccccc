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
        THE PREDICTIVE ENGINE: Identify future-looking intent signals.
        Returns an 'Intent Score' (0-100) and an 'Oracle Signal'.
        """
        try:
            prompt = f"""
            Analyze this verified lead data for PREDICTIVE INTENT.
            LEAD DATA: {lead_data}
            
            Identify hidden patterns:
            - Is the company scaling? (Recent hiring, repo spikes, office expansion)
            - Are they likely to fund soon?
            - Are they exploring new markets?
            
            Return ONLY a JSON object: 
            {{
                "intent_score": int, 
                "oracle_signal": "string (e.g., 'Expansion Imminent', 'Funding Signal')",
                "confidence": float
            }}
            """
            ai_response = await gemini_client.model.generate_content(prompt)
            clean_json = re.sub(r'```json\n?|\n?```', '', ai_response.text).strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"❌ Predictive Error: {e}")
            return {"intent_score": 0, "oracle_signal": "Baseline Intelligence", "confidence": 0.5}

arbiter = ArbiterAgent()
