"""
Charvak Email Verification System
Prevents bot registrations, verifies real users
"""
import logging
import secrets
import os
from datetime import datetime, timedelta

logger = logging.getLogger("charvakit.email_verification")

class EmailVerification:
    def __init__(self):
        self.verification_tokens = {}
        logger.info("Email Verification ready")
    
    def generate_token(self, email):
        """Generate verification token."""
        token = secrets.token_urlsafe(32)
        self.verification_tokens[token] = {
            "email": email,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "verified": False
        }
        return token
    
    def send_verification_email(self, email, name, token):
        """Send verification email via SendGrid."""
        from email_engine import email_engine
        
        verification_url = f"https://charvakit-website.onrender.com/verify-email?token={token}"
        
        subject = "Verify Your Charvak Account"
        content = f"""
        <h2>Welcome to Charvak, {name}!</h2>
        <p>Please verify your email address to activate your account.</p>
        <p><a href="{verification_url}" style="background:#3ba591;color:white;padding:12px 25px;text-decoration:none;border-radius:50px;">Verify Email</a></p>
        <p>Or copy this link: {verification_url}</p>
        <p>This link expires in 24 hours.</p>
        <p>If you didn't create this account, please ignore this email.</p>
        """
        
        result = email_engine.send_email(email, subject, content)
        return {"status": "success", "email_sent": result.get("status") == "success"}
    
    def verify_token(self, token):
        """Verify email token."""
        if token not in self.verification_tokens:
            return {"status": "error", "message": "Invalid or expired token"}
        
        data = self.verification_tokens[token]
        
        # Check expiry
        expires_at = datetime.fromisoformat(data["expires_at"])
        if datetime.now() > expires_at:
            del self.verification_tokens[token]
            return {"status": "error", "message": "Token expired"}
        
        # Mark verified
        data["verified"] = True
        email = data["email"]
        
        return {"status": "success", "email": email, "message": "Email verified successfully"}
    
    def is_verified(self, email):
        """Check if email is verified."""
        for token, data in self.verification_tokens.items():
            if data["email"] == email and data["verified"]:
                return True
        return False

email_verification = EmailVerification()
