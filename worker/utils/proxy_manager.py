import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProxyManager:
    """
    Manages a list of proxies, handling rotation and failure reporting.
    """
    def __init__(self, proxy_list_path=None):
        self.proxies = []
        self.bad_proxies = set()
        self.current_index = 0
        
        if proxy_list_path:
            self.load_proxies(proxy_list_path)
        else:
            # Default to some placeholder "direct" or mock proxies if no file provided
            self.proxies = ["direct"] 
            logger.info("No proxy list provided. Using 'direct' mode.")

    def load_proxies(self, path):
        """Loads proxies from a file (one per line)."""
        try:
            with open(path, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            logger.info(f"Loaded {len(self.proxies)} proxies from {path}")
        except FileNotFoundError:
            logger.warning(f"Proxy file {path} not found. Defaulting to direct.")
            self.proxies = ["direct"]

    def get_proxy(self):
        """Returns the next available proxy."""
        if not self.proxies:
            return None
        
        # Simple Round Robin for now
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        # Skip if marked bad (simple retry logic could be added)
        if proxy in self.bad_proxies and len(self.proxies) > len(self.bad_proxies):
            return self.get_proxy()
            
        return proxy

    def report_failure(self, proxy):
        """Marks a proxy as bad."""
        if proxy != "direct":
            logger.warning(f"Marking proxy {proxy} as bad.")
            self.bad_proxies.add(proxy)

    def report_success(self, proxy):
        """Optional: Clears bad status if we want to implement forgiveness."""
        if proxy in self.bad_proxies:
            self.bad_proxies.remove(proxy)

# Singleton instance for easy import if needed
# proxy_manager = ProxyManager()
