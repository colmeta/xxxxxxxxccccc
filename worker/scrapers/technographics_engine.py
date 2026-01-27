import asyncio
import aiohttp
import os
from scrapers.base_dork_engine import BaseDorkEngine

class TechnographicsEngine:
    """
    LAYER 4: TECHNOGRAPHICS
    Extracts tech stack and infrastructure signals from Shodan and SecurityTrails.
    """
    
    def __init__(self, page=None):
        self.page = page
        self.dork_engine = BaseDorkEngine(page, "technographics")
        self.platform = "technographics"

    async def log(self, msg):
        print(f"   [TechEngine] {msg}")

    async def check_shodan_free(self, ip=None, domain=None):
        """
        Checks Shodan for open ports/vulns.
        Free Tier: limited API. Logic: Try API, Fallback to Dork.
        """
        target = ip or domain
        await self.log(f"Scanning Shodan for: {target}")
        
        api_key = os.getenv("SHODAN_API_KEY") # Optional
        
        if api_key and ip:
            url = f"https://api.shodan.io/shodan/host/{ip}?key={api_key}"
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return {
                                "source": "Shodan (API)",
                                "ports": data.get('ports', []),
                                "os": data.get('os', 'Unknown'),
                                "tags": data.get('tags', []),
                                "is_live_data": True
                            }
                except Exception as e:
                    await self.log(f"Shodan API Error: {e}")

        # Fallback: Dorking
        query = f'site:shodan.io/host "{target}"'
        results = await self.dork_engine.run_dork_search(query, "")
        
        if results:
            return {
                "source": "Shodan (Dork)",
                "report_url": results[0].get('source_url'),
                "signal": "Exposure Found",
                "is_live_data": False
            }
            
        return None

    async def check_securitytrails_free(self, domain):
        """
        Checks SecurityTrails for DNS history / subdomains.
        """
        await self.log(f"Scanning SecurityTrails for: {domain}")
        
        # Free API limit is strict. Dorking is safer for 'Zero Budget'.
        # site:securitytrails.com/domain/example.com
        
        query = f'site:securitytrails.com/domain/{domain}'
        results = await self.dork_engine.run_dork_search(query, "")
        
        if results:
            best = results[0]
            snippet = best.get('snippet', '')
            
            return {
                "source": "SecurityTrails (Dork)",
                "report_url": best.get('source_url'),
                "snippet_signal": snippet[:100],
                "is_live_data": False
            }
            
        return None

    async def scrape(self, query):
        """
        Main entry point.
        """
        # Sanitization
        domain = query.replace("https://", "").replace("http://", "").split("/")[0]
        
        await self.log(f"Initiating Technographics Scan for: {domain}")
        
        # Resolve IP for Shodan if possible
        import socket
        try:
            ip = socket.gethostbyname(domain)
        except:
            ip = None
            
        shodan_data = await self.check_shodan_free(ip, domain)
        st_data = await self.check_securitytrails_free(domain)
        
        results = []
        if shodan_data: results.append(shodan_data)
        if st_data: results.append(st_data)
        
        # Metadata
        for r in results:
            r['layer'] = "Layer 4: Technographics"
            
        await self.log(f"Mission verified. {len(results)} tech signals secured.")
        return results
