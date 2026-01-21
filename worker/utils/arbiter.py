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
        Falls back to heuristics if AI fails.
        """
        try:
            ai_data = await gemini_client.verify_data(target_query, lead_data, search_context)
            if ai_data and isinstance(ai_data, dict):
                return ai_data.get('truth_score', 0), ai_data.get('verdict', "AI Verified")
        except Exception as e:
            print(f"Arbiter AI Fallback Triggered: {e}")
            
        return self._calculate_heuristic_score(target_query, lead_data)

    async def score_visual_lead(self, target_query, screenshot_path):
        """
        VISION-X: Analyze product images or social posts via Gemini Vision.
        """
        try:
            print(f"Arbiter Vision-X: Analyzing sensory evidence {screenshot_path}...")
            ai_response = await gemini_client.analyze_visuals(target_query, screenshot_path)
            if ai_response:
                clean_json = gemini_client._clean_json(ai_response)
                ai_data = json.loads(clean_json)
                return ai_data.get('truth_score', 0), ai_data.get('verdict', "Vision Verdict")
        except Exception as e:
            print(f"Arbiter Vision-X Failure: {e}")

        return 0, "Visual Truth Verification Failed"

    def _calculate_heuristic_score(self, target_query, lead_data):
        """Standard fallback heuristic engine."""
        score = 0
        rules_applied = []
        
        if not lead_data:
            return 0, "No data to score"

        query_terms = set(re.findall(r'\w+', target_query.lower()))
        lead_text = json.dumps(lead_data).lower()
        
        matches = sum(1 for term in query_terms if term in lead_text)
        relevance_score = (matches / len(query_terms)) * 40 if query_terms else 0
        score += relevance_score
        rules_applied.append(f"Relevance: +{int(relevance_score)}")

        # Completeness Check
        critical_fields = ['name', 'title', 'company']
        present_fields = [f for f in critical_fields if lead_data.get(f) and len(str(lead_data.get(f))) > 1]
        completeness_score = (len(present_fields) / len(critical_fields)) * 40
        score += completeness_score
        rules_applied.append(f"Completeness: +{int(completeness_score)}")

        # Trust Signals
        if lead_data.get('verified') or 'http' in str(lead_data.get('source_url', '')):
            score += 20
            rules_applied.append("Trust: +20 (Source Signal)")
        
        # Temporal Freshness
        stale_markers = ["2022", "2021", "2020", "years ago"]
        signal_text = json.dumps(lead_data).lower()
        
        for marker in stale_markers:
            if marker in signal_text:
                score -= 30
                rules_applied.append(f"Decay: -30 (Stale Signal: {marker})")
                break
        
        if any(m in signal_text for m in ["hours ago", "minutes ago", "today"]):
            score += 15
            rules_applied.append("Freshness: +15 (Near-Live Signal)")

        final_score = max(0, min(int(score), 100))
        verdict = f"H-Score {final_score}/100 (Fallback) | {', '.join(rules_applied)}"
        return final_score, verdict

    def polish_lead(self, lead_data):
        """
        CLARITY PEARL: DATA POLISHER
        Standardizes names, titles, and companies for a 'Pure' outreach experience.
        """
        cleaned = lead_data.copy()
        
        # 1. Clean Person Name
        if cleaned.get('name'):
            name = cleaned['name'].strip()
            # Remove emojis and special chars
            name = re.sub(r'[^\w\s-]', '', name)
            cleaned['name'] = name.title()
            
        # 2. Clean Company Name (The 'Pearl' Polish)
        if cleaned.get('company'):
            comp = cleaned['company'].strip()
            # Common junk suffixes that ruin outreach logic
            suffixes = [
                r'\bL\.?L\.?C\.?\b', r'\bInc\.?\b', r'\bCorp\.?(\b|oration)', 
                r'\bLtd\.?\b', r'\bGmbH\b', r'\bS\.?A\.?S\.?\b', r'\bPty\b'
            ]
            for suffix in suffixes:
                comp = re.sub(suffix, '', comp, flags=re.IGNORECASE).strip()
            
            # Remove trailing commas/dashes
            comp = re.sub(r'[,\-]$', '', comp).strip()
            cleaned['company'] = comp.title()
            
        # 3. Clean Job Title
        if cleaned.get('title'):
            title = cleaned['title'].strip()
            # Standardize common acronyms
            mappings = {
                "Chief Executive Officer": "CEO",
                "Chief Technology Officer": "CTO",
                "Chief Operating Officer": "COO",
                "Chief Marketing Officer": "CMO",
                "Founder and CEO": "Founder & CEO"
            }
            for full, short in mappings.items():
                title = title.replace(full, short)
            
            cleaned['title'] = title.title() if len(title) > 5 else title # Keep acronyms short
            
        return cleaned


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
            ai_response_text = await gemini_client.generate_content(prompt)
            if not ai_response_text:
                raise ValueError("Empty response from AI")
            
            clean_json = gemini_client._clean_json(ai_response_text)
            return json.loads(clean_json)
        except Exception as e:
            # Guerilla Pivot: Logging the transition to Baseline Intelligence
            print(f"   ⚖️  Oracle Predictive Signal: AI Offline ({e}). Engaging Baseline Intelligence...")
            return self._calculate_heuristic_intent(lead_data)

    def _calculate_heuristic_intent(self, lead_data):
        """Baseline intent prediction when AI is offline."""
        snippet = str(lead_data).lower()
        intent_score = 50
        growth_score = 40
        
        # High intent keywords
        if any(w in snippet for m, w in [("hire", "hiring"), ("expansion", "expanding"), ("new", "launch")]):
            intent_score += 20
            growth_score += 20
        
        # Seniority boost
        if any(r in snippet for r in ["ceo", "founder", "director", "cto"]):
            intent_score += 15
        
        return {
            "intent_score": min(intent_score, 100), 
            "predictive_growth_score": min(growth_score, 100), 
            "oracle_signal": "Heuristic Intent (Baseline)", 
            "confidence": 0.6,
            "reasoning": "Heuristic fallback analysis performed due to AI downtime."
        }

    async def recursive_verdict(self, lead_data):
        """
        THE SLEUTH: Generate a follow-up verification query.
        """
        prompt = f"""
        LEAD DATA: {lead_data}
        
        TASK:
        Generate a SINGLE follow-up search query to verify this lead's current activity or role 
        on a DIFFERENT platform (e.g., Google News, Website, or Twitter).
        
        Return ONLY the query string.
        """
        try:
             response_text = await gemini_client.generate_content(prompt)
             if not response_text: raise ValueError("Empty response")
             return response_text.strip()
        except:
             name = lead_data.get('name', 'Company')
             company = lead_data.get('company', '')
             return f"recent news {name} {company}".strip()

    async def _pearl_01_debate(self, context_prompt: str, initial_script: str) -> str:
        """
        PEARL-01: Multi-Agent Debate Flow.
        Refines a script by running a 'Critic' agent against a 'Creative' agent.
        """
        print("🏛️ PEARL-01: Initiating internal debate flow...")
        
        critic_prompt = f"""
        {context_prompt}
        
        YOU ARE THE CRITIC (PEARL-01-SKEPTIC).
        Analyze the following outreach script and find 3 reasons why it might be ignored or seen as spam.
        Be brutal. Identify weak language, lack of specific value, or poor timing.
        
        SCRIPT: "{initial_script}"
        
        Return ONLY your bulleted critique.
        """
        try:
            critic_res_text = await gemini_client.generate_content(critic_prompt)
            critique = critic_res_text.strip()
            print(f"🧐 Critic Signal: {critique[:100]}...")

            refinement_prompt = f"""
            {context_prompt}
            
            YOU ARE THE ARCHITECT (PEARL-01-FINAL).
            We have an initial script and a critical review.
            
            INITIAL SCRIPT: "{initial_script}"
            CRITIQUE: "{critique}"
            
            TASK: Re-forge the script to address all criticisms while maintaining high authority and conversion-focus.
            Make it tighter, more 'Sovereign', and undeniable.
            
            Return ONLY the final refined script.
            """
            final_res_text = await gemini_client.generate_content(refinement_prompt)
            return final_res_text.strip()
        except Exception as e:
            print(f"⚠️ Pearl-01 Debate Interrupted: {e}")
            return initial_script

    async def generate_sovereign_displacement(self, lead_data: dict, growth_velocity: dict) -> dict:
        """
        CLARITY PEARL: SOVEREIGN INTELLIGENCE - PEARL-01 ENHANCED
        Generates a displacement script, then runs a Pearl-01 Debate to refine it.
        """
        print(f"🧠 Sovereign Intelligence: Analyzing displacement for {lead_data.get('name')}...")
        
        metadata = lead_data.get('metadata', {})
        tech_signals = str(metadata).lower()
        
        competitors = []
        if "shopify" in tech_signals: competitors.append("Shopify")
        if "hubspot" in tech_signals: competitors.append("HubSpot")
        if "salesforce" in tech_signals: competitors.append("Salesforce")
        if "stripe" in tech_signals: competitors.append("Stripe")
        
        if not competitors:
            return {"status": "no_competitor_detected", "script": ""}

        context_prompt = f"""
        CLARITY PEARL: SOVEREIGN INTELLIGENCE - DISPLACEMENT MISSION
        LEAD: {lead_data.get('name')} from {lead_data.get('company')}
        COMPETITORS DETECTED: {', '.join(competitors)}
        GROWTH VELOCITY: {growth_velocity.get('scaling_signal', 'Steady')}
        """

        prompt = f"""
        {context_prompt}
        
        TASK:
        Generate a high-authority, non-spammy outreach script that points out a friction point 
        with their current stack (the competitors) and suggests how our solution solves it.
        Use their growth velocity as a 'Growth Agitator'.
        
        Return ONLY a JSON object:
        {{
            "displacement_target": "The competitor to target",
            "friction_point": "Why the competitor is failing them during growth",
            "sovereign_script": "The draft outreach message"
        }}
        """
        try:
            response_text = await gemini_client.generate_content(prompt)
            if not response_text:
                return {"status": "error", "message": "No AI response"}

            clean_json = gemini_client._clean_json(response_text)
            data = json.loads(clean_json)
            
            # PEARL-01 DEBATE: Refine the script
            refined_script = await self._pearl_01_debate(context_prompt, data.get('sovereign_script', ''))
            data['sovereign_script'] = refined_script
            
            return data
        except Exception as e:
            print(f"[X] Sovereign Displacement Error: {e}")
            # Baseline Displacement (Heuristic)
            target = competitors[0] if competitors else "Stack"
            return {
                "displacement_target": target,
                "friction_point": "Scaling friction and manual overhead.",
                "sovereign_script": f"Hi {lead_data.get('name', 'there')}, saw your growth at {lead_data.get('company', 'your firm')}. Most teams hit a wall with {target} at this stage. Worth a quick look at how we automate that friction away?",
                "status": "baseline_fallback"
            }

arbiter = ArbiterAgent()
