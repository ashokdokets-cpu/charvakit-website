"""
Charvak Password Reset System
"""
import logging
import secrets
import os
from datetime import datetime, timedelta

logger = logging.getLogger("charvakit.password_reset")

class PasswordReset:
    def __init__(self):
        self.reset_tokens = {}
        logger.info("Password Reset System ready")
    
    def generate_reset_token(self, email):
        """Generate password reset token."""
        token = secrets.token_urlsafe(32)
        self.reset_tokens[token] = {
            "email": email,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            "used": False
        }
        return token
    
    def send_reset_email(self, email, token):
        """Send password reset email."""
        from email_engine import email_engine
        
        reset_url = f"https://charvakit-website.onrender.com/reset-password?token={token}"
        
        subject = "Reset Your Charvak Password"
        content = f"""
        <h2>Password Reset Request</h2>
        <p>Click the link below to reset your password:</p>
        <p><a href="{reset_url}" style="background:#3ba591;color:white;padding:12px 25px;text-decoration:none;border-radius:50px;">Reset Password</a></p>
        <p>Or copy: {reset_url}</p>
        <p><strong>This link expires in 1 hour.</strong></p>
        <p>If you didn't request this, please ignore this email.</p>
        """
        
        result = email_engine.send_email(email, subject, content)
        return {"status": "success", "email_sent": result.get("status") == "success"}
    
    def verify_reset_token(self, token):
        """Verify reset token."""
        if token not in self.reset_tokens:
            return {"status": "error", "message": "Invalid token"}
        
        data = self.reset_tokens[token]
        
        if data["used"]:
            return {"status": "error", "message": "Token already used"}
        
        expires_at = datetime.fromisoformat(data["expires_at"])
        if datetime.now() > expires_at:
            del self.reset_tokens[token]
            return {"status": "error", "message": "Token expired"}
        
        return {"status": "success", "email": data["email"]}
    
    def reset_password(self, token, new_password):
        """Reset password with token."""
        result = self.verify_reset_token(token)
        if result["status"] != "success":
            return result
        
        email = result["email"]
        
        # Hash new password
        from auth import hash_password
        from database import db
        
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            hashed = hash_password(new_password)
            cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hashed, email))
            conn.commit()
            cursor.close()
            conn.close()
            
            self.reset_tokens[token]["used"] = True
            return {"status": "success", "message": "Password reset successfully"}
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return {"status": "error", "message": "Password reset failed"}

password_reset = PasswordReset()
