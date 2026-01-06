import asyncio
from datetime import datetime, timedelta
from backend.services.supabase_client import get_supabase

class HiveSentry:
    """
    THE SELF-HEALING HIVE
    Monitors missions and ensures that no job is left behind.
    If a worker fails, the Hive re-queues the mission automatically.
    """
    
    def __init__(self):
        self.supabase = get_supabase()
        self.check_interval = 60 # Check every minute
    
    async def start(self):
        print("🕊️ Hive Sentry: Initializing Eternal Persistence...")
        while True:
            try:
                await self.heal_dead_jobs()
                await self.purge_stale_workers()
            except Exception as e:
                print(f"⚠️ Hive Sentry Error: {e}")
            await asyncio.sleep(self.check_interval)

    async def heal_dead_jobs(self):
        """
        Finds jobs marked as 'running' but whose workers haven't pulsed recently.
        """
        # 1. Get all active workers
        res_workers = self.supabase.table('worker_status').select('worker_id').execute()
        active_worker_ids = [w['worker_id'] for w in res_workers.data] if res_workers.data else []

        # 2. Find jobs marked 'running'
        # A job is 'dead' if it's been running for more than 10 minutes OR its worker is gone
        res_jobs = self.supabase.table('jobs').select('id, worker_id, target_query').eq('status', 'running').execute()
        
        if res_jobs.data:
            to_heal = []
            for job in res_jobs.data:
                # Check if worker is gone or job is too old
                # (For simplicity here, we focus on the 'worker gone' case as the primary self-healing trigger)
                if job['worker_id'] not in active_worker_ids:
                    to_heal.append(job)
            
            if to_heal:
                print(f"🛡️ Hive Sentry: Healing {len(to_heal)} missions from vanished workers...")
                for job in to_heal:
                    self.supabase.table('jobs').update({
                        "status": "queued",
                        "started_at": None,
                        "worker_id": None,
                        "error_log": f"Healed by Hive Sentry: Worker {job['worker_id']} vanished."
                    }).eq('id', job['id']).execute()

    async def purge_stale_workers(self):
        """
        Removes workers from the active pool if they haven't pulsed for 5 minutes.
        """
        stale_threshold = datetime.now() - timedelta(minutes=5)
        self.supabase.table('worker_status').delete().lt('last_pulse', stale_threshold.isoformat()).execute()

hive_sentry = HiveSentry()
