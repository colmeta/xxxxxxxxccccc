from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import jobs, results
import os

app = FastAPI(
    title="Clarity Pearl API",
    description="The Sensory Nervous System for the AI Economy",
    version="1.0.0"
)

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Must be False if using allow_origins=["*"]
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
from backend.routers import crm, outreach, bulk
app.include_router(crm.router)
app.include_router(outreach.router)
app.include_router(bulk.router)

# --- ROOT ENDPOINT ---
@app.get("/")
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

