"""
Charvak Login Notifications
"""
import logging
from datetime import datetime

logger = logging.getLogger("charvakit.login_notifications")

class LoginNotifications:
    def send_login_alert(self, email, ip_address, user_agent):
        """Send login notification email."""
        from email_engine import email_engine
        
        subject = "New Login to Your Charvak Account"
        content = f"""
        <h2>New Login Detected</h2>
        <p>Your Charvak account was accessed:</p>
        <ul>
            <li><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
            <li><strong>IP Address:</strong> {ip_address}</li>
            <li><strong>Device:</strong> {user_agent[:100]}</li>
        </ul>
        <p>If this wasn't you, please reset your password immediately:</p>
        <p><a href="https://charvakit-website.onrender.com/forgot-password" style="background:#e94d65;color:white;padding:12px 25px;text-decoration:none;border-radius:50px;">Reset Password</a></p>
        """
        
        try:
            result = email_engine.send_email(email, subject, content)
            return {"status": "success", "sent": result.get("status") == "success"}
        except Exception as e:
            logger.error(f"Login notification failed: {e}")
            return {"status": "error", "message": str(e)}

login_notifications = LoginNotifications()
