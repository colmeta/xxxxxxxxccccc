import httpx
import os
import asyncio
from typing import Optional, Tuple

class Geocoder:
    def __init__(self, supabase=None):
        self.supabase = supabase
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.user_agent = "ClarityPearl/1.0 (B2B Sales Intelligence Platform)"

    async def get_coordinates(self, address_string: str) -> Optional[Tuple[float, float]]:
        """
        Converts an address string into Latitude and Longitude.
        Implements persistent caching via Supabase to minimize external API calls.
        """
        if not address_string or address_string in ["Global / Remote", "Unknown", "n/a", "N/A"]:
            return None

        # 1. Check Cache
        if self.supabase:
            try:
                cached = self.supabase.table('geocoding_cache').select('lat', 'lng').eq('address_string', address_string).execute()
                if cached.data:
                    return cached.data[0]['lat'], cached.data[0]['lng']
            except Exception as e:
                print(f"⚠️ GeoCache Lookup failed: {e}")

        # 2. External Request (Nominatim)
        try:
            params = {
                "q": address_string,
                "format": "json",
                "limit": 1
            }
            headers = {"User-Agent": self.user_agent}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(self.base_url, params=params, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    if data:
                        lat, lng = float(data[0]['lat']), float(data[0]['lon'])
                        
                        # Save to Cache
                        if self.supabase:
                            try:
                                self.supabase.table('geocoding_cache').upsert({
                                    "address_string": address_string,
                                    "lat": lat,
                                    "lng": lng
                                }).execute()
                            except: pass
                        
                        return lat, lng
        except Exception as e:
            print(f"⚠️ Geocoding failed for '{address_string}': {e}")
            
        return None

# Singleton instance
geocoder = Geocoder()
