import asyncio
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict

class Ghostwriter:
    """
    CLARITY PEARL: GHOSTWRITER v2
    Autonomous Outreach & Engagement Engine.
    Handles sequence logic, personalization, and automated sending.
    """
    def __init__(self, supabase=None):
        self.supabase = supabase

    async def generate_personalized_content(self, lead_data: Dict, template: str) -> str:
        """
        Uses AI (via Arbiter) or Heuristics to personalize a sequence step.
        """
        # Simple placeholder for now - we'll integrate Arbiter for deep personalization later
        company = lead_data.get('company', 'your company')
        name = lead_data.get('name', 'there')
        
        personalized = template.replace("{{name}}", name).replace("{{company}}", company)
        return personalized

    async def process_outreach_queue(self):
        """
        Scans the database for scheduled outreach tasks and executes them.
        Ideally run by the Swarm on a cron or interval.
        """
        if not self.supabase: return
        
        print("✍️ Ghostwriter: Scanning for engagement opportunities...")
        
        # 1. Fetch 'pending' logs from outreach_logs
        try:
            res = self.supabase.table('outreach_logs').select("*").eq('status', 'pending').lt('scheduled_at', datetime.now().isoformat()).execute()
            
            for log in res.data:
                await self.execute_step(log)
        except Exception as e:
            print(f"❌ Ghostwriter Queue Error: {e}")

    async def execute_step(self, log_entry: Dict):
        """
        Executes a single step in a sequence (Email, LinkedIn DM, etc.)
        """
        log_id = log_entry.get('id')
        lead_id = log_entry.get('lead_id')
        sequence_step_id = log_entry.get('sequence_step_id')
        
        print(f"✍️ Ghostwriter: Executing Step {sequence_step_id} for Lead {lead_id}...")
        
        try:
            # 1. Fetch Lead Data
            lead_res = self.supabase.table('results').select("*").eq('id', lead_id).execute()
            if not lead_res.data:
                raise Exception("Lead not found")
            lead = lead_res.data[0]
            
            # 2. Fetch Sequence Step Content
            step_res = self.supabase.table('outreach_sequences').select("*").eq('id', sequence_step_id).execute()
            if not step_res.data:
                raise Exception("Sequence step not found")
            step = step_res.data[0]
            
            # 3. Personalize
            content = await self.generate_personalized_content(lead.get('data_payload', {}), step.get('template_body'))
            
            # 4. SEND (Simulated for Now, SMTP in Phase 17b)
            # In production, this calls Mailgun/SendGrid or SMTP
            print(f"📧 SENDING EMAIL TO {lead.get('data_payload', {}).get('email') or 'target'}")
            print(f"Subject: {step.get('template_subject')}")
            print(f"Body: {content[:100]}...")
            
            # 5. Update Log
            self.supabase.table('outreach_logs').update({
                'status': 'sent',
                'sent_at': datetime.now().isoformat(),
                'actual_content': content
            }).eq('id', log_id).execute()
            
            # 6. Schedule Next Step
            await self.schedule_next_step(lead_id, sequence_step_id)
            
        except Exception as e:
            print(f"⚠️ Ghostwriter Execution Failed: {e}")
            self.supabase.table('outreach_logs').update({'status': 'failed'}).eq('id', log_id).execute()

    async def schedule_next_step(self, lead_id: str, current_step_id: str):
        """
        Finds the next step in the campaign sequence and schedules it.
        """
        # Logic to find next step in sequences table with same campaign_id but higher order
        step_res = self.supabase.table('outreach_sequences').select("*").eq('id', current_step_id).execute()
        if not step_res.data: return
        
        curr = step_res.data[0]
        campaign_id = curr.get('campaign_id')
        curr_order = curr.get('step_order')
        
        next_step_res = self.supabase.table('outreach_sequences')\
            .select("*")\
            .eq('campaign_id', campaign_id)\
            .gt('step_order', curr_order)\
            .order('step_order')\
            .limit(1).execute()
            
        if next_step_res.data:
            next_step = next_step_res.data[0]
            delay_days = next_step.get('delay_days', 2)
            scheduled_at = datetime.now() + timedelta(days=delay_days)
            
            self.supabase.table('outreach_logs').insert({
                "lead_id": lead_id,
                "sequence_step_id": next_step['id'],
                "status": "pending",
                "scheduled_at": scheduled_at.isoformat()
            }).execute()
            print(f"🗓️ Ghostwriter: Scheduled Next Step in {delay_days} days.")

# Singleton
ghostwriter = Ghostwriter()
