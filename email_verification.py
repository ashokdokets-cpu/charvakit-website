"""
Charvak Email Verification - Database-backed
"""
import logging
import secrets
from datetime import datetime, timedelta, timezone, timezone

logger = logging.getLogger("charvakit.email_verification")

class EmailVerification:
    def __init__(self):
        self._ensure_table()
        logger.info("Email Verification ready (database-backed)")
    
    def _ensure_table(self):
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_verification_tokens (
                    token TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    verified BOOLEAN DEFAULT FALSE
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
    
    def generate_token(self, email, name="User"):
        """Generate verification token in database."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=24)
        
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO email_verification_tokens (token, email, name, expires_at) VALUES (%s, %s, %s, %s)",
                (token, email, name, expires_at)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return token
        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            return None
    
    def send_verification_email(self, email, name, token):
        from email_engine import email_engine
        
        verification_url = f"https://charvakit-website.onrender.com/verify-email?token={token}"
        
        subject = "🎉 Welcome to Charvak - Verify Your Account"
        content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                <h1>Welcome to Charvak!</h1>
                <p>Hi {name}, verify your email</p>
            </div>
            <div style="background: #f8f9fa; padding: 30px;">
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background: #3ba591; color: white; padding: 15px 40px; text-decoration: none; border-radius: 50px; font-weight: bold;">✅ Verify Email</a>
                </div>
                <p>Link expires in 24 hours.</p>
            </div>
        </div>
        """
        
        result = email_engine.send_email(email, subject, content)
        return {"status": "success", "email_sent": result.get("status") == "success"}
    
    def verify_token(self, token):
        if not token:
            return {"status": "error", "message": "No token provided"}
        
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT email, expires_at, verified FROM email_verification_tokens WHERE token = %s",
                (token,)
            )
            row = cursor.fetchone()
            
            if not row:
                cursor.close()
                conn.close()
                return {"status": "error", "message": "Invalid verification link"}
            
            email, expires_at, verified = row
            
            if datetime.now(timezone.utc).replace(tzinfo=None) > expires_at:
                cursor.close()
                conn.close()
                return {"status": "error", "message": "Link expired"}
            
            # Mark as verified
            cursor.execute(
                "UPDATE email_verification_tokens SET verified = TRUE WHERE token = %s",
                (token,)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            return {"status": "success", "email": email, "message": "Email verified"}
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return {"status": "error", "message": "Verification failed"}
    
    def is_verified(self, email):
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT verified FROM email_verification_tokens WHERE email = %s AND verified = TRUE LIMIT 1",
                (email,)
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return row is not None
        except:
            return False

email_verification = EmailVerification()
