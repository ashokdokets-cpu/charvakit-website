"""
Charvak Password Reset - UTC-based, database-backed
"""
import logging
import secrets
from datetime import datetime, timedelta, timezone

logger = logging.getLogger("charvakit.password_reset")

class PasswordReset:
    def __init__(self):
        self._ensure_table()
        logger.info("Password Reset ready")
    
    def _ensure_table(self):
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    token TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
    
    def generate_reset_token(self, email):
        """Generate token with UTC expiration."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        
        # Convert to naive UTC (remove tzinfo for PostgreSQL TIMESTAMP)
        expires_at_naive = expires_at.replace(tzinfo=None)
        
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Delete old tokens for this email
            cursor.execute("DELETE FROM password_reset_tokens WHERE email = %s", (email,))
            
            # Insert new token
            cursor.execute(
                "INSERT INTO password_reset_tokens (token, email, expires_at) VALUES (%s, %s, %s)",
                (token, email, expires_at_naive)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Token generated for {email}, expires at {expires_at_naive} UTC")
            return token
        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            return None
    
    def send_reset_email(self, email, token):
        from email_engine import email_engine
        
        import os as _os
        _base = _os.getenv("SITE_URL", "https://www.charvakit.com").rstrip("/")
        reset_url = f"{_base}/reset-password?token={token}"
        
        subject = "Reset Your Charvak Password"
        content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>🔐 Password Reset</h1>
            </div>
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <p>Click below to reset your password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background: #3ba591; color: white; padding: 15px 40px; text-decoration: none; border-radius: 50px; font-weight: bold; display: inline-block;">Reset Password</a>
                </div>
                <p style="color: #666; font-size: 14px;">Or copy: <a href="{reset_url}">{reset_url}</a></p>
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <strong>⏰ Link expires in 30 minutes.</strong>
                </div>
            </div>
        </div>
        """
        
        result = email_engine.send_email(email, subject, content)
        return {"status": "success", "email_sent": result.get("status") == "success"}
    
    def verify_reset_token(self, token):
        """Verify token - use UTC comparison."""
        if not token:
            return {"status": "error", "message": "No token provided"}
        
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT email, expires_at, used FROM password_reset_tokens WHERE token = %s",
                (token,)
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not row:
                logger.warning(f"Token not found: {token[:20]}...")
                return {"status": "error", "message": "Invalid reset link. Please request a new one."}
            
            email, expires_at, used = row
            
            if used:
                return {"status": "error", "message": "This reset link has already been used"}
            
            # Use UTC now
            now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
            
            logger.info(f"Token check: now={now_utc}, expires={expires_at}")
            
            if now_utc > expires_at:
                return {"status": "error", "message": "Reset link expired. Please request a new one."}
            
            return {"status": "success", "email": email}
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return {"status": "error", "message": "Verification failed"}
    
    def reset_password(self, token, new_password):
        result = self.verify_reset_token(token)
        if result["status"] != "success":
            return result
        
        email = result["email"]
        
        try:
            from auth import hash_password
            from database import db
            
            hashed = hash_password(new_password)
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE email = %s",
                (hashed, email)
            )
            
            cursor.execute(
                "UPDATE password_reset_tokens SET used = TRUE WHERE token = %s",
                (token,)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Password reset successful for {email}")
            return {"status": "success", "message": "Password reset successfully"}
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return {"status": "error", "message": "Password reset failed"}

password_reset = PasswordReset()
