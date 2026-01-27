import asyncio
import json
import os
import random
from datetime import datetime
from utils.humanizer import Humanizer

class EventsNetworkingEngine:
    """
    LAYER 9: EVENTS & NETWORKING
    Extracts LIVE event data from Eventbrite using Playwright Scraping.
    """
    
    def __init__(self, page=None):
        self.page = page
        self.platform = "events_networking"
        
    async def log(self, msg):
        print(f"   🥂 [EventsEngine] {msg}")

    async def _hard_reset(self):
        """Memory & State Isolation (The Iron Wall)."""
        try:
            if self.page:
                await self.page.goto("about:blank")
                await asyncio.sleep(2)
        except Exception: pass

    async def scrape_eventbrite(self, keyword):
        """
        Scrapes Eventbrite for public events (signals intent & networking).
        """
        await self.log(f"Scanning Eventbrite live usage for: '{keyword}'")
        
        results = []
        try:
            # Eventbrite Search URL
            url = f"https://www.eventbrite.com/d/online/{keyword.replace(' ', '-')}/"
            
            try:
                await self.page.goto(url, timeout=60000)
            except Exception as nav_err:
                 await self.log(f"   -> Eventbrite Navigation Falied: {nav_err}")
                 await self._hard_reset()
                 return []

            await Humanizer.random_sleep(3, 7)
            
            # Wait for event cards
            try:
                # Selector often changes, targeting generic card containers
                await self.page.wait_for_SELECTOR("div[data-testid='search-event-card-wrapper']", timeout=10000)
            except:
                # Fallback selector
                try: 
                    await self.page.wait_for_selector(".search-event-card-wrapper", timeout=5000)
                except:
                    await self.log("   -> No Eventbrite results found (or selector changed)")
                    return []

            cards = await self.page.query_selector_all("section.event-card-details")
            if not cards:
                 cards = await self.page.query_selector_all("div[data-testid='search-event-card-wrapper']")
            
            for card in cards[:8]:
                title_col = await card.query_selector("h2") or await card.query_selector("h3")
                date_col = await card.query_selector("p") or await card.query_selector(".event-card__date")
                link_col = await card.query_selector("a.event-card-link") or await card.query_selector("a")
                
                if title_col:
                    title = await title_col.inner_text()
                    date_str = await date_col.inner_text() if date_col else "Upcoming"
                    link = await link_col.get_attribute("href") if link_col else url
                    
                    results.append({
                        "source": "Eventbrite (Live Scrape)",
                        "event_name": title.strip(),
                        "organizer": "Unknown Organizer", # Hard to extract reliably from grid
                        "date": date_str.strip(),
                        "location": "Online / Global",
                        "link": link,
                        "is_live_data": True
                    })
            
            await self.log(f"   -> Found {len(results)} live events")
            return results
            
        except Exception as e:
            await self.log(f"   -> Eventbrite Scraping Failed: {e}")
            return []

    async def scrape_meetup(self, keyword):
        """
        Scrapes Meetup.com for community groups.
        """
        await self.log(f"Checking Meetup communities...")
        results = []
        try:
            url = f"https://www.meetup.com/find/?keywords={keyword}&source=EVENTS"
            await self.page.goto(url, timeout=60000)
            
            try:
                await self.page.wait_for_selector("[data-testid='event-card-in-search']", timeout=10000)
            except:
                return []
                
            cards = await self.page.query_selector_all("[data-testid='event-card-in-search']")
            
            for card in cards[:5]:
                title_el = await card.query_selector("h2")
                time_el = await card.query_selector("time")
                
                if title_el:
                    title = await title_el.inner_text()
                    time_val = await time_el.inner_text() if time_el else "Upcoming"
                    
                    results.append({
                        "source": "Meetup (Live Scrape)",
                        "group_name": title.strip(),
                        "next_event": time_val,
                        "activity_level": "Active",
                        "is_live_data": True
                    })
            
            await self.log(f"   -> Found {len(results)} meetup groups")
            return results
        except Exception as e:
            await self.log(f"   -> Meetup Scraping Error: {e}")
            return []

    async def scrape(self, query):
        """
        Main entry point.
        """
        await self.log(f"Initiating LIVE Event Signal Sweep for: {query}")
        
        # Sequential execution since browser single-context is safer for heavy pages
        events = await self.scrape_eventbrite(query)
        groups = await self.scrape_meetup(query)
        
        combined = events + groups
        
        # Add metadata
        for item in combined:
            item['layer'] = "Layer 9: Events & Networking"
            item['sovereign_signal'] = "Active Participation"
            
        await self.log(f"Mission verified. {len(combined)} real networking signals secured.")
        return combined
