"""
Charvak Email Engine
Sends email via GoDaddy SMTP
"""
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict

logger = logging.getLogger("charvakit.email")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtpout.secureserver.net")
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "hr@charvakit.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "hr@charvakit.com")

EMAIL_ENABLED = bool(SMTP_PASSWORD)


class EmailEngine:
    """Email notifications."""

    def __init__(self):
        self.enabled = EMAIL_ENABLED
        self.sent_count = 0
        if self.enabled:
            logger.info("Email Engine: ENABLED")
        else:
            logger.warning("Email Engine: DISABLED")

    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> Dict:
        """Send email via SMTP."""
        if not self.enabled:
            return {"status": "disabled", "message": "Email engine not configured"}

        try:
            msg = MIMEMultipart()
            msg["From"] = f"Charvak IT Consulting <{SMTP_USERNAME}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            if is_html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))

            smtp_success = False

            try:
                with smtplib.SMTP(SMTP_SERVER, 587) as server:
                    server.starttls()
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                    server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
                smtp_success = True
            except Exception:
                pass

            if not smtp_success:
                try:
                    with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
                        server.login(SMTP_USERNAME, SMTP_PASSWORD)
                        server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
                    smtp_success = True
                except Exception:
                    pass

            if not smtp_success:
                return {"status": "error", "message": "SMTP connection failed"}

            self.sent_count += 1
            logger.info(f"Email sent to {to_email}")
            return {"status": "success", "message": "Email sent successfully", "to": to_email}

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
            "smtp_server": SMTP_SERVER,
            "sender": SMTP_USERNAME,
            "total_sent": self.sent_count
        }


email_engine = EmailEngine()