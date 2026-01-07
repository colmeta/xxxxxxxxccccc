from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import jobs, results
import os

app = FastAPI(
    title="CLARITY PEARL API",
    description="Cognitive Lattice & Autonomous Research Intelligence Data",
    version="1.0.0"
)

if __name__ == "__main__":
    import uvicorn
    # OPTIMIZED FOR RENDER FREE TIER (512MB RAM)
    # 1 worker, limited concurrency to keep memory < 400MB
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1, limit_concurrency=20)

# --- DIVINE SERVICES (Phase 7) ---
from backend.services.hive_sentry import hive_sentry
import asyncio

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(hive_sentry.start())

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Required when origins are ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTERS ---
app.include_router(jobs.router)
app.include_router(results.router)

# Compliance Router
from backend.routers import opt_out
app.include_router(opt_out.router)

# CRM & Outreach Routers (Production)
from backend.routers import crm, outreach, bulk, oracle, clarity_pearl, slack_relay
app.include_router(crm.router)
app.include_router(outreach.router)
app.include_router(bulk.router)
app.include_router(oracle.router)
app.include_router(clarity_pearl.router)
app.include_router(slack_relay.router)

# White-Label API (Phase 6)
from backend.routers import v1
app.include_router(v1.router)

# --- ROOT ENDPOINT ---
@app.get("/")
@app.head("/")
def health_check():
    # We can check DB status via the service if we want, but keeping it simple for now
    from backend.services.supabase_client import get_supabase
    
    supabase = get_supabase()
    db_status = "connected" if supabase else "disconnected"
    
    return {
        "status": "operational", 
        "db": db_status, 
        "system": "Clarity Pearl Brain", 
        "version": "1.0.1 (Modular)"
    }

