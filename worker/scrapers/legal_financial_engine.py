import asyncio
import re
from scrapers.base_dork_engine import BaseDorkEngine

class LegalFinancialEngine:
    """
    CLARITY PEARL - LEGAL & FINANCIAL INTELLIGENCE
    Mission: Access the "Source Truth" of business filings.
    Layer 3 & 6: SEC Growth Signals, USPTO Patents, Justia Entities.
    """
    def __init__(self, page):
        self.page = page
        self.dork_engine = BaseDorkEngine(page, "legal_oracle")

    async def probe_sec_growth(self, company_name):
        """
        Dorks SEC EDGAR for growth indicators.
        Signal: Quarterly revenue or headcount mentions in 10-K/10-Q.
        """
        print(f"[Legal Oracle] 📈 Probing SEC filings for '{company_name}'...")
        query = f'site:sec.gov/Archives/edgar/data "{company_name}" (revenue | growth | "increase in headcount")'
        results = await self.dork_engine.run_dork_search(query, "")
        
        if not results: return None
        
        best = results[0]
        snippet = best.get('snippet', '')
        
        revenue_mention = re.search(r'\$(\d+[\.,]?\d*\s*[MB])', snippet, re.I)
        growth_keyword = any(k in snippet.lower() for k in ["surpassed", "expanded", "exponential", "growth"])

        return {
            "sec_filing_url": best.get('source_url'),
            "reported_revenue_hint": revenue_mention.group(1) if revenue_mention else "SME/Private",
            "growth_sentiment_filing": "Bullish" if growth_keyword else "Stable",
            "financial_layer": "Public Record Growth"
        }

    async def probe_patents_innovation(self, company_name):
        """
        Checks USPTO / Google Patents for R&D status.
        Signal: Active patent filing = Significant R&D budget.
        """
        print(f"[Legal Oracle] 💡 Probing Patents for '{company_name}'...")
        query = f'site:patents.google.com "assignee:{company_name}"'
        results = await self.dork_engine.run_dork_search(query, "")
        
        has_patents = len(results) > 0
        patent_count = len(results) if has_patents else 0
        
        top_tech_area = "Mixed"
        if has_patents:
            # Simple heuristic for tech area from snippet
            if "software" in str(results).lower(): top_tech_area = "Software/AI"
            elif "medical" in str(results).lower(): top_tech_area = "Biotech"

        return {
            "patent_record_found": has_patents,
            "patent_volume_indicator": "High" if patent_count > 10 else ("Low" if has_patents else "None"),
            "innovation_tech_focus": top_tech_area,
            "layer": "Innovation & R&D"
        }

    async def unified_legal_enrich(self, lead):
        """
        Full legal/financial profile build.
        """
        name = lead.get('name')
        if not name: return lead
        
        tasks = [
            self.probe_sec_growth(name),
            self.probe_patents_innovation(name)
        ]
        
        intel = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in intel:
            if res and isinstance(res, dict):
                lead.update(res)
                
        return lead
