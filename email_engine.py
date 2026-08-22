"""
Charvak Email Engine
Uses SendGrid API for reliable email delivery
"""
import os
import logging
from typing import Dict

logger = logging.getLogger("charvakit.email")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "charvakit@gmail.com")
FROM_EMAIL = "charvakit@gmail.com"

EMAIL_ENABLED = bool(SENDGRID_API_KEY)


class EmailEngine:
    """Email notifications via SendGrid."""

    def __init__(self):
        self.enabled = EMAIL_ENABLED
        self.sent_count = 0
        if self.enabled:
            logger.info("Email Engine: ENABLED (SendGrid)")
        else:
            logger.warning("Email Engine: DISABLED (set SENDGRID_API_KEY)")

    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> Dict:
        """Send email via SendGrid API."""
        if not self.enabled:
            return {"status": "disabled", "message": "SendGrid not configured"}

        try:
            import requests

            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {SENDGRID_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "personalizations": [{"to": [{"email": to_email}]}],
                    "from": {"email": FROM_EMAIL, "name": "Charvak IT Consulting"},
                    "subject": subject,
                    "content": [{"type": "text/plain", "value": body}]
                },
                timeout=10
            )

            if response.status_code in [200, 202]:
                self.sent_count += 1
                logger.info(f"Email sent to {to_email}")
                return {"status": "success", "message": "Email sent successfully", "to": to_email}
            else:
                logger.error(f"SendGrid error: {response.status_code}")
                return {"status": "error", "message": f"SendGrid error: {response.status_code}"}

        except Exception as e:
            logger.error(f"Email failed: {e}")
            return {"status": "error", "message": str(e)}

    def notify_admin(self, subject: str, message: str) -> Dict:
        return self.send_email(ADMIN_EMAIL, subject, message)

    def notify_new_message(self, recipient_email: str, recipient_name: str, sender_name: str, message_preview: str) -> Dict:
        subject = f"New Message from {sender_name} on Charvak"
        body = f"Hi {recipient_name},\n\n{sender_name} sent you a message on Charvak.\n\n{message_preview[:200]}\n\nLogin: https://charvakit.com"
        return self.send_email(recipient_email, subject, body)

    def notify_application_received(self, candidate_email: str, candidate_name: str, job_title: str, company: str) -> Dict:
        subject = f"Application Received - {job_title} at {company}"
        body = f"Hi {candidate_name},\n\nYour application for {job_title} at {company} has been received."
        return self.send_email(candidate_email, subject, body)

    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "enabled": self.enabled,
            "provider": "SendGrid",
            "sender": FROM_EMAIL,
            "total_sent": self.sent_count
        }


email_engine = EmailEngine()