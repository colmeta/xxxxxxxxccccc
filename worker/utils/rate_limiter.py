"""
CLARITY PEARL - RATE LIMITING SERVICE
Prevents burning through API credits and implements smart throttling.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import os

class RateLimiter:
    """
    Tracks API usage and enforces limits to prevent credit exhaustion.
    """
    
    def __init__(self):
        self.limits = {
            # Daily limits (resets at midnight)
            'groq': {'daily_limit': 14400, 'used': 0, 'reset_at': self._get_next_midnight()},  # 14.4k requests/day free tier
            'gemini': {'daily_limit': 1500, 'used': 0, 'reset_at': self._get_next_midnight()},  # Conservative limit
            'scraper_api': {'daily_limit': 1000, 'used': 0, 'reset_at': self._get_next_midnight()},  # 1k credits/day free
            
            # Per-minute limits (burst protection)
            'groq_rpm': {'limit': 30, 'used': 0, 'reset_at': datetime.now() + timedelta(minutes=1)},
            'gemini_rpm': {'limit': 15, 'used': 0, 'reset_at': datetime.now() + timedelta(minutes=1)},
        }
        
        # Load persisted state if available
        self._load_state()
    
    def _get_next_midnight(self) -> datetime:
        """Get next midnight for daily reset."""
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def _load_state(self):
        """Load rate limit state from file."""
        state_file = 'rate_limit_state.json'
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    for service, data in state.items():
                        if service in self.limits:
                            self.limits[service]['used'] = data.get('used', 0)
            except Exception as e:
                print(f"⚠️ Failed to load rate limit state: {e}")
    
    def _save_state(self):
        """Persist rate limit state to file."""
        state_file = 'rate_limit_state.json'
        try:
            state = {k: {'used': v['used']} for k, v in self.limits.items()}
            with open(state_file, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            print(f"⚠️ Failed to save rate limit state: {e}")
    
    def check_limit(self, service: str) -> bool:
        """
        Check if service is within rate limit.
        
        Args:
            service: Service name ('groq', 'gemini', 'scraper_api')
        
        Returns:
            True if allowed, False if limit exceeded
        """
        if service not in self.limits:
            return True  # Unknown service, allow
        
        limit_data = self.limits[service]
        
        # Check if reset needed
        if datetime.now() >= limit_data['reset_at']:
            limit_data['used'] = 0
            if 'daily' in service or service in ['groq', 'gemini', 'scraper_api']:
                limit_data['reset_at'] = self._get_next_midnight()
            else:
                limit_data['reset_at'] = datetime.now() + timedelta(minutes=1)
        
        # Check limit
        if limit_data['used'] >= limit_data.get('daily_limit', limit_data.get('limit', 999999)):
            remaining_time = (limit_data['reset_at'] - datetime.now()).total_seconds()
            print(f"🚫 Rate limit exceeded for {service}. Resets in {int(remaining_time/60)} minutes")
            return False
        
        return True
    
    def increment(self, service: str, count: int = 1):
        """
        Record API usage.
        
        Args:
            service: Service name
            count: Number of calls to add
        """
        if service in self.limits:
            self.limits[service]['used'] += count
            self._save_state()
            
            # Log warning if approaching limit
            limit_data = self.limits[service]
            usage_pct = (limit_data['used'] / limit_data.get('daily_limit', limit_data.get('limit', 1))) * 100
            
            if usage_pct >= 80:
                print(f"⚠️ WARNING: {service} at {usage_pct:.1f}% of daily limit!")
    
    def get_status(self) -> Dict:
        """Get current rate limit status for all services."""
        status = {}
        for service, data in self.limits.items():
            limit = data.get('daily_limit', data.get('limit', 0))
            used = data['used']
            remaining = max(0, limit - used)
            reset_in = (data['reset_at'] - datetime.now()).total_seconds()
            
            status[service] = {
                'used': used,
                'limit': limit,
                'remaining': remaining,
                'usage_percent': (used / limit * 100) if limit > 0 else 0,
                'reset_in_minutes': int(reset_in / 60)
            }
        
        return status
    
    def can_proceed_with_mission(self) -> tuple[bool, str]:
        """
        Check if system has enough credits to proceed with a mission.
        
        Returns:
            Tuple of (can_proceed, reason)
        """
        # Check critical services
        if not self.check_limit('groq') and not self.check_limit('gemini'):
            return False, "Both AI services (Groq & Gemini) have exceeded daily limits"
        
        if not self.check_limit('scraper_api'):
            groq_ok = self.check_limit('groq')
            if not groq_ok:
                return False, "ScraperAPI and Groq both exhausted - cannot bypass blocks"
        
        return True, "Sufficient credits available"
    
    def reset_all(self):
        """Emergency reset of all counters (admin only)."""
        for service in self.limits:
            self.limits[service]['used'] = 0
        self._save_state()
        print("🔄 All rate limits reset")


# Singleton instance
_rate_limiter = None

def get_rate_limiter() -> RateLimiter:
    """Get or create rate limiter singleton."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
