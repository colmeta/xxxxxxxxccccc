import hashlib
import os
import re
from typing import List, Union

def normalize_phone(phone: str) -> str:
    """
    Normalize phone number to digits only.
    In a real system, you might use python-phonenumbers for E.164.
    Here we strip all non-digit characters.
    """
    if not phone:
        return ""
    return re.sub(r'\D', '', phone)

def normalize_email(email: str) -> str:
    """Normalize email to lowercase and stripped."""
    if not email:
        return ""
    return email.strip().lower()

def hash_identifier(identifier: str, is_phone: bool = False) -> str:
    """
    One-way hash an email or phone number for the Opt-Out Registry.
    Uses a SALT from environment variable if available.
    """
    salt = os.getenv("PEARL_Recruiter_SALT", "")
    
    if is_phone:
        clean_id = normalize_phone(identifier)
    else:
        clean_id = normalize_email(identifier)
        
    if not clean_id:
        return ""
        
    payload = f"{clean_id}{salt}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def hash_batch(identifiers: List[str], is_phone: bool = False) -> List[str]:
    """
    Process a list of identifiers and return their hashes.
    """
    return [hash_identifier(uid, is_phone) for uid in identifiers if uid]

if __name__ == "__main__":
    # Test cases
    test_email = " CEO@Example.com "
    test_phone = "+1 (555) 123-4567"
    
    print(f"Original Email: '{test_email}'")
    print(f"Hashed Email:   {hash_identifier(test_email)}")
    
    print(f"Original Phone: '{test_phone}'")
    print(f"Hashed Phone:   {hash_identifier(test_phone, is_phone=True)}")
    
    print("-" * 40)
    print("Store ONLY the hash in the DB.")
