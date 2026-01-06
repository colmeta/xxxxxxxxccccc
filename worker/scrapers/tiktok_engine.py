import asyncio
from datetime import datetime

class TikTokEngine:
    """
    NEXUS SCOUT - TIKTOK GUEST ENGINE
    Mission: Extract trends and product discovery without login.
    """
    
    def __init__(self, page):
        self.page = page

    async def scrape(self, query):
        """
        Uses the Guest Web Interface to find trending videos/products.
        """
        print(f"📡 Scout-01: Infiltrating TikTok for '{query}'...")
        
        # 1. Target URL (Search)
        search_url = f"https://www.tiktok.com/search?q={query}"
        
        try:
            await self.page.goto(search_url, timeout=30000)
            await asyncio.sleep(2) # Allow hydration
            
            # 2. Extract Video Metadata
            # Note: Selectors change weekly, we use broad attribute matching
            videos = await self.page.evaluate("""
                () => {
                    const results = [];
                    const posts = document.querySelectorAll('div[data-e2e="search-item-list"] > div');
                    posts.forEach((post, index) => {
                        if (index > 10) return; // Top 10 only for V1
                        const title = post.querySelector('div[data-e2e="search-card-desc"]')?.innerText || '';
                        const author = post.querySelector('a[data-e2e="search-card-user-link"]')?.innerText || '';
                        const link = post.querySelector('a')?.href || '';
                        const views = post.querySelector('strong')? post.querySelector('strong').innerText : '0';
                        
                        results.append({
                            "title": title,
                            "author": author,
                            "url": link,
                            "metrics": {"views": views},
                            "timestamp": new Date().toISOString()
                        });
                    });
                    return results;
                }
            """)
            
            print(f"✅ Scout-01: Found {len(videos)} TikTok signals.")
            
            # 3. Format for Vault
            return [{
                "source": "tiktok",
                "target_query": query,
                "data": videos,
                "verified": True if len(videos) > 0 else False,
                "truth_score": 90 if len(videos) > 0 else 0
            }]

        except Exception as e:
            print(f"❌ Scout-01: TikTok Infiltration Failed: {e}")
            return []
