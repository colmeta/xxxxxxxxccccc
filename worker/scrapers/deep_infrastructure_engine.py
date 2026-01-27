import asyncio
import aiohttp
import os
from scrapers.base_dork_engine import BaseDorkEngine

class DeepInfrastructureEngine:
    """
    LAYER 10: DEEP INFRASTRUCTURE
    Extracts security and network intelligence from VirusTotal and IPinfo.
    """
    
    def __init__(self, page=None):
        self.page = page
        self.dork_engine = BaseDorkEngine(page, "infra_diver")
        self.platform = "deep_infrastructure"

    async def log(self, msg):
        print(f"   [InfraEngine] {msg}")

    async def check_virustotal(self, domain):
        """
        Checks VirusTotal for domain safety and reputation using Public API v3 (Free).
        """
        await self.log(f"Scanning VirusTotal for: {domain}")
        
        # VirusTotal Public API (Free tier: 500 requests/day, 4/min)
        # Requires Key. If no key, we Fallback to Dorking.
        api_key = os.getenv("VIRUSTOTAL_API_KEY")
        
        if api_key:
            url = f"https://www.virustotal.com/api/v3/domains/{domain}"
            headers = {"x-apikey": api_key}
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url, headers=headers, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                            
                            malicious = stats.get('malicious', 0)
                            return {
                                "source": "VirusTotal (API)",
                                "malicious_score": malicious,
                                "is_safe": malicious == 0,
                                "reputation": data.get('data', {}).get('attributes', {}).get('reputation', 0),
                                "is_live_data": True
                            }
                except Exception as e:
                    await self.log(f"VT API Error: {e}")

        # Fallback: Dorking for VT Report
        # site:virustotal.com/gui/domain "example.com"
        await self.log("   -> No VT Key or API limit. Switching to Dorking...")
        results = await self.dork_engine.run_dork_search(f'site:virustotal.com/gui/domain "{domain}"', "")
        
        if results:
            return {
                "source": "VirusTotal (Dork)",
                "report_url": results[0].get('source_url'),
                "signal": "Report Found",
                "is_live_data": False
            }
            
        return None

    async def check_ipinfo(self, domain):
        """
        Resolves IP and checks IPinfo.io for ASN/Geo (Free Tier).
        """
        await self.log(f"Resolving Infrastructure for: {domain}")
        
        # IPinfo (Free token 50k/month, or generic free API 1k/day without auth?)
        # We'll use the IP lookup via python socket first, then IPinfo API
        import socket
        try:
            ip = socket.gethostbyname(domain)
        except:
            await self.log("   -> DNS Resolution Failed")
            return None
            
        token = os.getenv("IPINFO_TOKEN") # Optional
        url = f"https://ipinfo.io/{ip}/json"
        
        params = {}
        if token: params['token'] = token
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "source": "IPinfo",
                            "ip": ip,
                            "org": data.get('org', ''),
                            "country": data.get('country', ''),
                            "city": data.get('city', ''),
                            "asn": data.get('org', '').split(' ')[0], 
                            "is_live_data": True
                        }
            except Exception as e:
                await self.log(f"IPinfo Error: {e}")
                
        return None

    async def scrape(self, query):
        """
        Main entry point. Query is usually a DOMAIN (e.g. 'openai.com').
        """
        # Sanitization
        domain = query.replace("https://", "").replace("http://", "").split("/")[0]
        
        await self.log(f"Initiating Deep Infrastructure Scan for: {domain}")
        
        vt_data = await self.check_virustotal(domain)
        ip_data = await self.check_ipinfo(domain)
        
        results = []
        if vt_data: results.append(vt_data)
        if ip_data: results.append(ip_data)
        
        # Metadata
        for r in results:
            r['layer'] = "Layer 10: Infrastructure"
            r['sovereign_signal'] = "Network Security & Topology"
            
        await self.log(f"Mission verified. {len(results)} infra signals secured.")
        return results
