import asyncio
import random
import math

class Humanizer:
    @staticmethod
    async def natural_scroll(page):
        """
        Simulates human-like scrolling with acceleration, pauses, and back-scrolling.
        """
        total_height = await page.evaluate("document.body.scrollHeight")
        viewport_height = await page.evaluate("window.innerHeight")
        current_scroll = 0
        
        while current_scroll < total_height:
            # Random scroll amount
            distance = random.randint(100, 600)
            
            # 10% chance to scroll UP slightly (reading behavior)
            if random.random() < 0.1:
                distance = -1 * random.randint(50, 150)
            
            await page.mouse.wheel(0, distance)
            current_scroll += distance
            
            # Wait for scroll to settle
            await asyncio.sleep(random.uniform(0.2, 1.5))
            
            # Check if we hit bottom
            new_height = await page.evaluate("document.body.scrollHeight")
            if current_scroll > new_height:
                break
                
            # Random long pause (reading)
            if random.random() < 0.15:
                await asyncio.sleep(random.uniform(1.0, 3.0))

    @staticmethod
    async def random_sleep(min_seconds=1, max_seconds=3):
        """Jittered sleep."""
        await asyncio.sleep(random.uniform(min_seconds, max_seconds))

    @staticmethod
    async def mouse_jitter(page):
        """
        Moves the mouse in a localized random pattern to simulate 'thinking' or reading.
        """
        try:
             # Get current position (mock, as Playwright doesn't expose it directly easily without tracking)
             # We start from center if unknown
             x = 600
             y = 400
             for _ in range(random.randint(3, 8)):
                 x += random.randint(-50, 50)
                 y += random.randint(-50, 50)
                 # Clamp to viewport
                 x = max(0, min(x, 1280))
                 y = max(0, min(y, 720))
                 
                 await page.mouse.move(x, y, steps=random.randint(5, 10))
                 await asyncio.sleep(random.uniform(0.1, 0.3))
        except:
            pass # Fail gracefully if page closed

    @staticmethod
    async def type_like_human(page, selector, text):
        """
        Types text into a selector with varied keystroke delays.
        """
        await page.focus(selector)
        for char in text:
            await page.keyboard.type(char)
            # Normal typing speed distribution 
            await asyncio.sleep(random.uniform(0.05, 0.2))
            
            # Occasional pause
            if random.random() < 0.05:
                await asyncio.sleep(random.uniform(0.3, 0.8))
