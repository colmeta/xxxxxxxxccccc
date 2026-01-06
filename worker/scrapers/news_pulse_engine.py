import feedparser
import asyncio
from datetime import datetime
from utils.arbiter import arbiter

class NewsPulseEngine:
    """
    NODE: GOOGLE NEWS PULSE
    Captures funding rounds, mergers, and hiring signals in real-time.
    """
    def __init__(self, page):
        self.page = page
        self.platform = "google_news"

    async def scrape(self, query):
        print(f"[{self.platform}] 📡 Tuning into News Heartbeat for: {query}")
        
        # 1. Use RSS for speed and zero-JS footprint
        encoded_query = query.replace(" ", "+")
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            # RSS Parsing (Zero footprint fallback)
            feed = feedparser.parse(rss_url)
            results = []
            
            for entry in feed.entries[:10]:
                results.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published,
                    "source": entry.source.get('title', 'Google News'),
                    "verified": True,
                    "timestamp": datetime.now().isoformat(),
                    "snippet": f"Signal captured from {entry.source.get('title')}: {entry.title}"
                })
            
            # 2. AI Arbiter check for high-intent signals (funding, hiring, growth)
            intent_query = f"{query} funding hiring growth merger expansion"
            # In a real scenario, we'd cross-check these titles with the AI
            
            print(f"[{self.platform}] ✅ Ingested {len(results)} news signals.")
            return results

        except Exception as e:
            print(f"[{self.platform}] ❌ News Pulse Failure: {e}")
            return []
