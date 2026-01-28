import re
import asyncio

class OfflineContactDiscovery:
    """
    ZERO-COST CONTACT DISCOVERY
    No APIs required - pure HTML parsing and pattern matching.
    """
    
    def __init__(self, page):
        self.page = page
    
    async def extract_emails_from_html(self, url):
        """Extract emails directly from website HTML"""
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2)
            
            # Get page content
            content = await self.page.content()
            
            # Email regex pattern
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            
            # Find all emails
            emails = re.findall(email_pattern, content.lower())
            
            # Filter out common false positives
            exclude_patterns = ['example.com', 'domain.com', 'email.com', 'test.com', 'jpg', 'png', 'svg']
            filtered = [e for e in emails if not any(ex in e for ex in exclude_patterns)]
            
            return list(set(filtered))  # Deduplicate
        except:
            return []
    
    async def generate_email_patterns(self, name, domain):
        """Generate common email format guesses"""
        if not name or not domain:
            return []
        
        try:
            parts = name.lower().strip().split()
            if len(parts) < 2:
                first = parts[0] if parts else ""
                last = ""
            else:
                first = parts[0]
                last = parts[-1]
            
            # Remove common titles
            titles = ['mr', 'mrs', 'ms', 'dr', 'prof', 'ceo', 'founder']
            first = first if first not in titles else (parts[1] if len(parts) > 1 else "")
            
            domain = domain.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]
            
            patterns = [
                f"{first}.{last}@{domain}",
                f"{first[0]}{last}@{domain}" if first and last else None,
                f"{first}@{domain}" if first else None,
                f"{last}@{domain}" if last else None,
                f"{first}{last}@{domain}" if first and last else None,
            ]
            
            return [p for p in patterns if p]
        except:
            return []
    
    def validate_email_format(self, email):
        """Simple regex validation - no API calls"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone_format(self, phone):
        """Validate phone number format"""
        # Remove common formatting
        clean = re.sub(r'[^0-9+]', '', str(phone))
        
        # Must be 10-15 digits
        if len(clean) < 10 or len(clean) > 15:
            return False
        
        return True
    
    def filter_junk_company_name(self, name):
        """
        OFFLINE BOUNCER: Filter out junk company names
        Returns True if name is valid, False if junk
        """
        if not name or len(name) < 2:
            return False
        
        # Too long = probably description not name
        if len(name) > 60:
            return False
        
        # Too many hyphens = Google Maps description
        if name.count('-') > 2:
            return False
        
        # Generic/placeholder names
        junk_keywords = [
            'click here', 'read more', 'learn more', 'view more',
            'loading', 'advertisement', 'sponsored', 'google maps'
        ]
        
        name_lower = name.lower()
        if any(keyword in name_lower for keyword in junk_keywords):
            return False
        
        return True

offline_contact_discovery = OfflineContactDiscovery
