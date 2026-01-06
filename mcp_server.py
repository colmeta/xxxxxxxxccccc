import asyncio
import os
import json
from mcp.server.fastmcp import FastMCP
from backend.services.supabase_client import get_supabase
from worker.utils.gemini_client import GeminiClient

# Initialize FastMCP for CLARIDATA
mcp = FastMCP("CLARIDATA")
gemini = GeminiClient()

@mcp.tool()
async def query_vault(query: str, limit: int = 5):
    """
    Query the CLARIDATA Intelligence Vault for existing lead data.
    """
    supabase = get_supabase()
    res = supabase.table('results').select('*').ilike('data_payload->>name', f'%{query}%').limit(limit).execute()
    return res.data if res.data else "No results found in the vault."

@mcp.tool()
async def dispatch_mission(mission_prompt: str):
    """
    Dispatch a new autonomous research mission to the CLARIDATA mesh.
    Supports complex intents like 'Find 10 marketing managers in SF'.
    """
    # Use the existing Oracle logic via GeminiClient
    mission_steps = await gemini.dispatch_mission(mission_prompt)
    
    # In a production MCP, we'd actually insert into the DB here.
    # For now, we return the plan for confirmation.
    return {
        "status": "Plan Generated",
        "plan": mission_steps,
        "instructions": "Execute these steps via the CLARIDATA dashboard to begin extraction."
    }

@mcp.tool()
async def mesh_status():
    """
    Get the current health and performance of the CLARIDATA Global Mesh.
    """
    supabase = get_supabase()
    res = supabase.table('worker_status').select('*').execute()
    active_count = len(res.data) if res.data else 0
    return {
        "active_nodes": active_count,
        "status": "optimal" if active_count > 0 else "degraded",
        "mesh_type": "P2P Sovereign Cloud"
    }

if __name__ == "__main__":
    mcp.run()
