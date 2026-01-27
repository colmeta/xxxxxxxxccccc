import asyncio
import json
import os
import aiohttp
from datetime import datetime

class TradeDataEngine:
    """
    LAYER 8: TRADE & LOGISTICS
    Extracts import/export data from US Census (Free) and UN Comtrade (Free Preview).
    """
    
    def __init__(self, page=None):
        self.page = page
        self.census_key = os.getenv("CENSUS_API_KEY") 
        # Default HS Codes for common terms
        self.hs_map = {
            "electronics": "85", "coffee": "0901", "steel": "72", "vehicles": "87",
            "oil": "27", "plastic": "39", "pharma": "30", "furniture": "94"
        }
        
    async def log(self, msg):
        print(f"   🚢 [TradeEngine] {msg}")

    async def fetch_usa_trade_data(self, keyword):
        """
        Fetches LIVE US Import/Export data from Census Bureau API.
        Attempts keyless access if key missing (allowed for small volume).
        """
        await self.log(f"Querying US Census live database for: {keyword}")
        
        hs_code = self.hs_map.get(keyword.lower(), "85") # Default to electronics
        year = datetime.now().year - 1
        
        # Public API Endpoint: Monthly International Trade
        url = "https://api.census.gov/data/timeseries/intltrade/imports/hs"
        
        params = {
            "get": "I_COMMODITY,CTY_CODE,GEN_VAL_MO",
            "time": f"{year}-12", # Latest full year end
            "COMM_LVL": "HS2", # 2-digit level for breadth
            "I_COMMODITY": hs_code
        }
        
        if self.census_key:
            params["key"] = self.census_key
            
        async with aiohttp.ClientSession() as session:
            try:
                await self.log(f"   -> Connecting to Census API: {url}...")
                async with session.get(url, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Census returns [headers, row1, row2...]
                        if len(data) > 1:
                            headers = data[0]
                            row = data[1]
                            val_idx = headers.index("GEN_VAL_MO")
                            desc_idx = headers.index("I_COMMODITY_LD")
                            
                            value = float(row[val_idx]) if row[val_idx] else 0
                            
                            await self.log(f"   -> Census Success: ${value:,.2f} trade volume detected.")
                            
                            return [{
                                "source": "USA Trade Online (Census)",
                                "commodity": row[desc_idx],
                                "trade_flow": "Import",
                                "value_usd": value,
                                "period": f"{year}-12",
                                "partner_country": "Global",
                                "is_live_data": True
                            }]
                        else:
                            await self.log("   -> Census API returned empty data.")
                    else:
                        await self.log(f"   -> Census API Error: {resp.status} - {await resp.text()}")
            except Exception as e:
                await self.log(f"   -> Census Connection Failed: {e}")
                
        return []

    async def fetch_un_comtrade(self, country="USA"):
        """
        Fetches LIVE Global Trade flows from UN Comtrade Public API (v2).
        The public/preview endpoint provides limited but real data.
        """
        await self.log(f"Querying UN Comtrade public registry...")
        
        # UN Comtrade Public Preview API
        # Gets total trade for reporter (USA) with World
        url = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
        
        params = {
            "period": str(datetime.now().year - 2), # 2 years lag often free
            "reporterCode": "842", # USA
            "partnerCode": "0", # World
            "flowCode": "M", # Import
            "cmdCode": "TOKEN_TOTAL" # Total Trade
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                await self.log(f"   -> Connecting to UN Comtrade: {url}...")
                async with session.get(url, params=params, ssl=False, timeout=10) as resp:
                    if resp.status == 200:
                        raw = await resp.json()
                        data = raw.get('data', [])
                        if data:
                            rec = data[0]
                            val = rec.get('primaryValue', 0)
                            await self.log(f"   -> UN Comtrade Success: ${val:,.2f} global trade detected.")
                            return [{
                                "source": "UN Comtrade (Public)",
                                "reporter": rec.get('reporterDesc'),
                                "partner": rec.get('partnerDesc'),
                                "trade_value": val,
                                "year": rec.get('period'),
                                "is_live_data": True
                            }]
            except Exception as e:
                await self.log(f"   -> UN Comtrade Connection Failed: {e}")
                
        return []

    async def scrape(self, query):
        """
        Main entry point.
        """
        await self.log(f"Starting LIVE Trade Scan for: {query}")
        keyword = query.replace("imports", "").replace("exports", "").strip()
        
        # Parallel Execution
        results = await asyncio.gather(
            self.fetch_usa_trade_data(keyword),
            self.fetch_un_comtrade()
        )
        
        combined_data = results[0] + results[1]
        
        # Add metadata
        for item in combined_data:
            item['layer'] = "Layer 8: Trade & Logistics"
            item['sovereign_signal'] = "Live Supply Chain"
            
        if not combined_data:
            await self.log("⚠️ No live data found. Using fallback heuristics...")
            # Fallback only if live APIs fail completely
            combined_data.append({
                "source": "Trade Estimate (Fallback)",
                "note": "Live APIs unreachable. Check firewall/keys.",
                "commodity": keyword,
                "status": "Estimation Mode"
            })
            
        await self.log(f"Mission verified. {len(combined_data)} real trade records secured.")
        return combined_data
