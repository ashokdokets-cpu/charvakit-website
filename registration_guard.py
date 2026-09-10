"""
Block suspicious registration patterns
"""
import re

def is_suspicious_email(email):
    """Check if email looks suspicious (bot-generated)."""
    if not email:
        return True
    
    email_lower = email.lower()
    
    # Suspicious patterns
    suspicious_patterns = [
        r'^[a-z]\.[a-z]\.[a-z]',  # f.o.xuyufir
        r'[0-9]\.[0-9]\.[0-9]',   # 7.1.5
        r'^charvak\d+@',           # charvak123456
        r'[bcdfghjklmnpqrstvwxz]{8,}',  # Long consonant strings
        r'^[a-z]{1,2}\.[a-z]{1,2}\.[a-z]{1,2}',
    ]
    
    for pattern in suspicious_patterns:
        if re.match(pattern, email_lower):
            return True
    
    # Check if name looks random (all consonants/caps)
    return False

def is_suspicious_name(name):
    """Check if name looks bot-generated."""
    if not name:
        return True
    
    # Random-looking names (like "vWDYkiHhJuhTmbcXGP")
    if len(name) > 15 and not ' ' in name:
        return True
    
    # All consonants (no vowels)
    vowels = set('aeiouAEIOU')
    if len(name) > 5 and not any(c in vowels for c in name):
        return True
    
    return False

def validate_registration(email, name, password):
    """Validate registration data."""
    if is_suspicious_email(email):
        return {"status": "error", "message": "Invalid email format"}
    
    if is_suspicious_name(name):
        return {"status": "error", "message": "Please provide your real name"}
    
    if len(password) < 8:
        return {"status": "error", "message": "Password must be at least 8 characters"}
    
    return {"status": "success"}
