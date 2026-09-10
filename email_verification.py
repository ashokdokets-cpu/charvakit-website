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
        
        subject = "🎉 Welcome to Charvak - Verify Your Account"
        content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0;">Welcome to Charvak!</h1>
                <p style="margin: 10px 0 0 0;">Hi {name}, let's get you started</p>
            </div>
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <h3>Verify Your Email Address</h3>
                <p>Thanks for signing up! Please click the button below to verify your email and activate your account.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background: #3ba591; color: white; padding: 15px 40px; text-decoration: none; border-radius: 50px; font-weight: bold; display: inline-block;">✅ Verify Email</a>
                </div>
                
                <p style="color: #666; font-size: 14px;">Or copy this link:<br>
                <a href="{verification_url}" style="color: #3ba591; word-break: break-all;">{verification_url}</a></p>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <strong>⏰ Important:</strong> This link expires in 24 hours.
                </div>
                
                <hr style="margin: 30px 0;">
                
                <p><strong>What you get with Charvak:</strong></p>
                <ul>
                    <li>🤖 25 AI-Driven Courses with personal tutor</li>
                    <li>📝 AI-Powered Assessments (Versant, MCQ)</li>
                    <li>🏢 Company Mock Drives (18 companies)</li>
                    <li>🎯 Career Guidance with AI analysis</li>
                    <li>💼 C2C Placement Platform</li>
                </ul>
                
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    If you didn't create this account, please ignore this email.<br>
                    Questions? Contact us at hr@charvakit.com
                </p>
            </div>
        </div>
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
