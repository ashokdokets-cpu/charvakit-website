"""
Admin Access Control - charvakit@gmail.com bypasses payment
"""
import logging

logger = logging.getLogger("charvakit.admin_access")

ADMIN_EMAILS = ["charvakit@gmail.com", "admin@charvakit.com"]

def is_admin(email):
    """Check if email has admin access."""
    return email in ADMIN_EMAILS

def admin_bypass_payment(email):
    """Admin bypasses payment requirement."""
    return is_admin(email)

def admin_full_access(email):
    """Check if admin has full access."""
    return {
        "status": "success",
        "email": email,
        "is_admin": is_admin(email),
        "payment_required": not is_admin(email),
        "access_level": "FULL_ACCESS" if is_admin(email) else "PAYMENT_REQUIRED"
    }
