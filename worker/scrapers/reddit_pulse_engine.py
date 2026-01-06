from scrapers.base_dork_engine import BaseDorkEngine

class RedditPulseEngine(BaseDorkEngine):
    """
    NODE: REDDIT PULSE
    Analyzes deep social discussions, sentiments, and "hidden" market trends.
    """
    def __init__(self, page):
        super().__init__(page, "reddit")

    async def scrape(self, query):
        """
        Specialized scraping for Reddit.
        Focuses on 'site:reddit.com/r/' to target subreddits.
        """
        print(f"[{self.platform}] 🗨️ Tuning into the Reddit Hivemind for: {query}")
        
        # 1. Broad Search (via Dorking)
        results = await self.run_dork_search(query, "reddit.com")
        
        # 2. Targeted Subreddit Search
        # Examples: "query" in /r/startups, /r/realestate, /r/ecommerce
        sub_results = await self.run_dork_search(f'"{query}"', "reddit.com/r")
        
        # Tag signals as "Crowd Sentiment"
        for r in all_results:
            r['sentiment_signal'] = True
            # Detect relative time in snippet
            if "ago" in r['snippet'].lower() or "today" in r['snippet'].lower():
                r['freshness_cue'] = "LIVE"
            r['snippet'] += " | SOCIAL SENTIMENT CAPTURED"

        print(f"[{self.platform}] ✅ Ingested {len(all_results)} reddit signals.")
        return all_results
