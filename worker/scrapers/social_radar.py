from scrapers.base_dork_engine import BaseDorkEngine

class TwitterEngine(BaseDorkEngine):
    def __init__(self, page):
        super().__init__(page, "twitter")

    async def scrape(self, query):
        # Twitter Dork: site:twitter.com "query" -site:twitter.com/hashtag
        return await self.run_dork_search(query, "twitter.com")

class InstagramEngine(BaseDorkEngine):
    def __init__(self, page):
        super().__init__(page, "instagram")

    async def scrape(self, query):
        # Instagram Dork: site:instagram.com "query"
        return await self.run_dork_search(query, "instagram.com")
