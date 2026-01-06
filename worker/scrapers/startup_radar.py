from scrapers.base_dork_engine import BaseDorkEngine
from utils.humanizer import Humanizer

class CrunchbaseEngine(BaseDorkEngine):
    def __init__(self, page):
        super().__init__(page, "crunchbase")

    async def scrape(self, query):
        return await self.run_dork_search(query, "crunchbase.com/organization")

class ProductHuntEngine(BaseDorkEngine):
    def __init__(self, page):
        super().__init__(page, "producthunt")

    async def scrape(self, query):
        return await self.run_dork_search(query, "producthunt.com/posts")

class RedditEngine(BaseDorkEngine):
    def __init__(self, page):
        super().__init__(page, "reddit")

    async def scrape(self, query):
        # Focus on subreddits or user discussions
        return await self.run_dork_search(query, "reddit.com/r")

class YCombinatorEngine:
    """
    Direct scraper for YC directory (public).
    Does NOT use Dorking because YC has a clean directory structure.
    """
    def __init__(self, page):
        self.page = page
        self.platform = "ycombinator"
        
    async def scrape(self, query):
        print(f"[{self.platform}] 🚀 Scouring YC Directory for: {query}")
        # YC doesn't have a simple query param for their public launch list easily accessible via GET 
        # without Algolia JS, but we can search via Google Dork if we want specific companies, 
        # OR we can try to hit the standard lists. 
        # For robustness and "unshakable" nature, we will actually fall back to Dorking 
        # for YC companies specifically, as the directory page heavily relies on client-side JS/Algolia.
        
        # Strategy: site:ycombinator.com/companies "query"
        engine = BaseDorkEngine(self.page, "ycombinator")
        return await engine.run_dork_search(query, "ycombinator.com/companies")
