import asyncio
import json
import os
import aiohttp
import xml.etree.ElementTree as ET
from datetime import datetime

class AcademicResearchEngine:
    """
    LAYER 13: ACADEMIC FRONTIER
    Extracts LIVE research data from FREE Public APIs (PubMed, arXiv).
    """
    
    def __init__(self, page=None):
        self.page = page
        
    async def log(self, msg):
        print(f"   🔬 [AcademicEngine] {msg}")

    async def scrape_pubmed(self, keyword):
        """
        Queries PubMed (NCBI) for biomedical research using E-utilities API.
        """
        await self.log(f"Querying PubMed live database for: '{keyword}'")
        
        # 1. Search for IDs
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": keyword,
            "retmode": "json",
            "retmax": 5
        }
        
        results = []
        async with aiohttp.ClientSession() as session:
            try:
                # Step 1: Get IDs
                async with session.get(search_url, params=params, timeout=10) as resp:
                    if resp.status != 200:
                        return []
                    data = await resp.json()
                    ids = data.get('esearchresult', {}).get('idlist', [])
                    
                if not ids:
                    return []

                # Step 2: Get Summaries
                summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                sum_params = {
                    "db": "pubmed",
                    "id": ",".join(ids),
                    "retmode": "json"
                }
                
                async with session.get(summary_url, params=sum_params, timeout=10) as resp:
                    if resp.status == 200:
                        sum_data = await resp.json()
                        uid_data = sum_data.get('result', {})
                        
                        for uid in ids:
                            doc = uid_data.get(uid)
                            if doc:
                                results.append({
                                    "source": "PubMed (NIH)",
                                    "title": doc.get('title', 'Unknown Title'),
                                    "journal": doc.get('fulljournalname', 'Unknown Journal'),
                                    "authors": [a['name'] for a in doc.get('authors', [])],
                                    "pub_date": doc.get('pubdate', ''),
                                    "pmid": uid,
                                    "link": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                                    "is_live_data": True
                                })
                                
                await self.log(f"   -> Found {len(results)} PubMed citations")
                return results
            except Exception as e:
                await self.log(f"   -> PubMed Connection Failed: {e}")
                return []

    async def scrape_arxiv(self, keyword):
        """
        Queries arXiv for CS/Physics preprints using standard API.
        """
        await self.log(f"Querying arXiv live index for: '{keyword}'")
        
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{keyword}",
            "start": 0,
            "max_results": 5
        }
        
        results = []
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        xml_data = await resp.text()
                        # Simple XML parsing (namespace aware)
                        root = ET.fromstring(xml_data)
                        ns = {'atom': 'http://www.w3.org/2005/Atom'}
                        
                        for entry in root.findall('atom:entry', ns):
                            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
                            published = entry.find('atom:published', ns).text
                            link = entry.find('atom:id', ns).text
                            
                            authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
                            
                            results.append({
                                "source": "arXiv (Live)",
                                "title": title,
                                "summary": summary[:200] + "...",
                                "authors": authors,
                                "published": published[:10],
                                "link": link,
                                "is_live_data": True
                            })
                            
                await self.log(f"   -> Found {len(results)} arXiv papers")
                return results
                
            except Exception as e:
                await self.log(f"   -> arXiv Connection Failed: {e}")
                return []

    async def scrape(self, query):
        """
        Main entry point.
        """
        await self.log(f"Initiating LIVE Academic Sweep for: {query}")
        
        # Parallel Execution
        results = await asyncio.gather(
            self.scrape_pubmed(query),
            self.scrape_arxiv(query)
        )
        
        combined = results[0] + results[1]
        
        # Add metadata
        for item in combined:
            item['layer'] = "Layer 13: Academic Frontier"
            item['sovereign_signal'] = "Deep Tech R&D"
            
        await self.log(f"Mission verified. {len(combined)} real research papers secured.")
        return combined
