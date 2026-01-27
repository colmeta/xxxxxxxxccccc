import asyncio
import random
from scrapers.base_dork_engine import BaseDorkEngine
from utils.humanizer import Humanizer

class JobScoutEngine(BaseDorkEngine):
    """
    LAYER 5: INTENT SIGNALS (EXPANDED)
    Tracks hiring signals across Google Jobs, RemoteOK, Greenhouse, and LinkedIn.
    """
    def __init__(self, page):
        super().__init__(page, "job_scout")
        self.platform = "job_scout"

    async def _hard_reset(self):
        """Memory & State Isolation."""
        try:
            if self.page:
                await self.page.goto("about:blank")
                await asyncio.sleep(2)
        except Exception: pass

    async def scrape_google_jobs(self, keyword):
        """
        Direct scrape of Google Jobs widget.
        """
        print(f"   💼 [JobScout] Checking Google Jobs for: {keyword}")
        results = []
        try:
            # Google Jobs specific URL parameter
            url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}+jobs&ibp=htl;jobs"
            
            try:
                await self.page.goto(url, timeout=30000)
            except Exception as nav_err:
                print(f"   -> Google Jobs Nav Failed: {nav_err}")
                await self._hard_reset()
                return []
                
            await Humanizer.random_sleep(3, 6) # Patience
            
            # Selector for job cards in the widget
            # Common classes: .iFjolb (container), .BjJfJf (title) - heavily obfuscated
            # We use generic attributes or text checks
            
            # Wait for generic list container
            try:
                await self.page.wait_for_selector("ul li", timeout=10000)
            except:
                return []

            # Extract via JS to handle obfuscation better
            job_data = await self.page.evaluate('''() => {
                const jobs = [];
                document.querySelectorAll('li').forEach(li => {
                    const title = li.querySelector('[role="heading"]')?.innerText;
                    const company = li.querySelector('div[style*="font-size"]')?.innerText; 
                    if (title && company) {
                        jobs.push({title, company});
                    }
                });
                return jobs.slice(0, 5);
            }''')
            
            for job in job_data:
                results.append({
                    "source": "Google Jobs (Live)",
                    "role": job.get('title'),
                    "company": job.get('company'),
                    "is_hiring_signal": True
                })
                
            print(f"   -> Found {len(results)} from Google Jobs")
            return results
        except Exception as e:
            print(f"   -> Google Jobs Error: {e}")
            await self._hard_reset()
            return []

    async def scrape_remoteok(self, keyword):
        """
        Direct scrape of RemoteOK.
        """
        print(f"   💼 [JobScout] Checking RemoteOK for: {keyword}")
        results = []
        try:
            url = f"https://remoteok.com/remote-{keyword.replace(' ', '-')}-jobs"
            
            try:
                await self.page.goto(url, timeout=45000)
            except:
                return []
            
            await Humanizer.random_sleep(2, 4)
            
            rows = await self.page.query_selector_all("tr.job")
            for row in rows[:5]:
                company_el = await row.query_selector("h3")
                role_el = await row.query_selector("h2")
                
                if company_el and role_el:
                    company = await company_el.inner_text()
                    role = await role_el.inner_text()
                    results.append({
                        "source": "RemoteOK (Live)",
                        "role": role.strip(),
                        "company": company.strip(),
                        "is_hiring_signal": True
                    })
            
            print(f"   -> Found {len(results)} from RemoteOK")
            return results
        except Exception as e:
            print(f"   -> RemoteOK Error: {e}")
            return []

    async def scrape(self, query):
        """
        Main entry point.
        """
        print(f"[{self.platform}] 💼 Scouring for hiring signals: {query}")
        
        # 1. Direct Scrapes
        g_jobs = await self.scrape_google_jobs(query)
        remote_jobs = await self.scrape_remoteok(query)
        
        # 2. Dorking (Greenhouse & Lever are best dorked)
        # site:boards.greenhouse.io "software engineer"
        gh_jobs = await self.run_dork_search(f'site:boards.greenhouse.io "{query}"', "")
        
        # Transform dork results
        for r in gh_jobs:
            r['source'] = "Greenhouse (Dork)"
            r['is_hiring_signal'] = True

        all_results = g_jobs + remote_jobs + gh_jobs
        
        print(f"[{self.platform}] ✅ Captured {len(all_results)} job signals.")
        return all_results
