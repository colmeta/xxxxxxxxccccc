import asyncio
import os
import sys

# Ensure we can import from the root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

try:
    from worker.utils.arbiter import arbiter
    print("[OK] Arbiter imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import Arbiter: {e}")
    sys.exit(1)

def test_normalization():
    print("\n--- Testing Data Normalization ---")
    test_leads = [
        {
            "name": "JANE DOE",
            "company": "ACME MARKETING LLC",
            "title": "CHIEF EXECUTIVE OFFICER"
        },
        {
            "name": "john smith",
            "company": "Global Solutions Inc.",
            "title": "founder and ceo"
        }
    ]
    
    for lead in test_leads:
        try:
            polished = arbiter.polish_lead(lead)
            print(f"Original: {lead['name']} | {lead['company']} | {lead['title']}")
            print(f"Polished: {polished['name']} | {polished['company']} | {polished['title']}")
            print("-" * 30)
        except Exception as e:
            print(f"[ERROR] Error polishing lead: {e}")

async def test_triple_verification_logic():
    print("\n--- Testing Triple-Verification Logic Simulation ---")
    lead = {
        "name": "Jane Doe",
        "company": "Acme",
        "email": "jane@acme.com",
        "website": "https://acme.com",
        "verified": True
    }
    
    clarity_score = 90
    
    is_verified = lead.get('verified', False)
    has_site = bool(lead.get('website'))
    has_email = bool(lead.get('email'))
    
    if is_verified and has_site and has_email and clarity_score > 85:
        lead['triple_verified'] = True
        print(f"[PASSED] Lead marked as Triple-Verified")
    else:
        print(f"[FAILED] Lead not marked")

if __name__ == "__main__":
    test_normalization()
    try:
        asyncio.run(test_triple_verification_logic())
    except Exception as e:
        print(f"[ERROR] Async error: {e}")
