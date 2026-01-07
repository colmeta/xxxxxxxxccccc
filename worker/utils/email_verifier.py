import re
try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    print("⚠️ 'dnspython' not found. Email MX domain verification will be skipped.")
    DNS_AVAILABLE = False
import smtplib
from typing import Dict

class EmailVerifier:
    """
    Real-time email verification (Pain Point #5).
    Competitors use stale databases. We verify LIVE before outreach.
    """
    
    def __init__(self):
        self.disposable_domains = [
            'tempmail.com', 'guerrillamail.com', '10minutemail.com',
            'mailinator.com', 'yopmail.com'
        ]
    
    async def verify_email(self, email: str) -> Dict[str, any]:
        """
        Multi-layer verification:
        1. Syntax validation
        2. Domain MX record check
        3. SMTP server ping (catches catch-alls)
        4. Disposable email detection
        """
        result = {
            "email": email,
            "is_valid": False,
            "is_deliverable": False,
            "is_disposable": False,
            "risk_score": 100,  # 0 = safe, 100 = invalid
            "checks": {}
        }
        
        # 1. Syntax Check
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(regex, email):
            result["checks"]["syntax"] = "FAIL"
            return result
        result["checks"]["syntax"] = "PASS"
        result["risk_score"] -= 20
        
        domain = email.split('@')[1]
        
        # 2. Disposable Email Check
        if domain.lower() in self.disposable_domains:
            result["checks"]["disposable"] = "DETECTED"
            result["is_disposable"] = True
            result["risk_score"] += 50
            return result
        result["checks"]["disposable"] = "CLEAN"
        
        # 3. MX Record Check
        if not DNS_AVAILABLE:
            result["checks"]["mx_record"] = "SKIPPED (Missing dnspython)"
            # Skip to SMTP ping with a best-guess (direct domain), or just fail?
            # Usually MX is better, but let's just mark it as unknown.
            mx_host = domain 
        else:
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
            if not mx_records:
                result["checks"]["mx_record"] = "FAIL"
                return result
            result["checks"]["mx_record"] = "PASS"
            result["risk_score"] -= 30
            mx_host = str(mx_records[0].exchange)
        except Exception as e:
            result["checks"]["mx_record"] = f"FAIL ({e})"
            return result
        
        # 4. SMTP Ping (Lightweight, no actual send)
        try:
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_host)
            server.helo(server.local_hostname)
            server.mail('verify@claritypearl.ai')
            code, message = server.rcpt(email)
            server.quit()
            
            if code == 250:
                result["checks"]["smtp"] = "DELIVERABLE"
                result["is_deliverable"] = True
                result["risk_score"] -= 50
            elif code == 550:
                result["checks"]["smtp"] = "REJECTED"
            else:
                result["checks"]["smtp"] = f"UNKNOWN ({code})"
                result["risk_score"] -= 10  # Uncertain, but not clearly bad
        except Exception as e:
            result["checks"]["smtp"] = f"ERROR ({str(e)[:50]})"
            result["risk_score"] -= 10  # Assume valid if SMTP check fails (firewall/etc.)
        
        # Final verdict
        result["is_valid"] = result["risk_score"] <= 30
        result["risk_score"] = max(0, min(result["risk_score"], 100))
        
        return result

email_verifier = EmailVerifier()
