import asyncio
import os
from datetime import datetime
from backend.services.supabase_client import get_supabase
from worker.utils.gemini_client import gemini_client

class Watchtower:
    """
    THE WATCHTOWER: Passive Signal Intelligence.
    Scans the Vault for high-intent signals and triggers alerts.
    """
    def __init__(self):
        self.supabase = get_supabase()
        self.active = True

    async def scan_for_signals(self):
        print("📡 Watchtower: Scanning for high-intent signals...")
        while self.active:
            try:
                # 1. Fetch un-alerted results with high truth scores
                res = self.supabase.table('results') \
                    .select('*, jobs(target_query)') \
                    .gt('truth_score', 85) \
                    .is_('alerted_at', 'null') \
                    .limit(10) \
                    .execute()

                for record in res.data:
                    payload = record['data_payload']
                    query = record['jobs']['target_query']
                    
                    # 2. AI Reasoning: Is this a "Mission Critical" signal?
                    # We check for keywords like 'hiring', 'funded', 'moving', 'problem'
                    signal_text = str(payload).lower()
                    high_intent_keywords = ['hiring', 'funded', 'series a', 'series b', 'layoff', 'expansion']
                    
                    if any(k in signal_text for k in high_intent_keywords):
                        print(f"🔥 SIGNAL DETECTED: {query} -> {payload.get('name', 'Unknown')}")
                        
                        # 3. Mark as alerted
                        self.supabase.table('results').update({
                            "alerted_at": datetime.now().isoformat(),
                            "is_high_intent": True
                        }).eq('id', record['id']).execute()
                        
                        # Here we would trigger Slack/Telegram/Webhook alerts
                        # For Phase 4, we maintain it in the DB for the UI to show.
                
            except Exception as e:
                print(f"⚠️ Watchtower Error: {e}")
            
            await asyncio.sleep(60) # Scan every minute

if __name__ == "__main__":
    tower = Watchtower()
    asyncio.run(tower.scan_for_signals())
