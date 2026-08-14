"""
Charvak Email Notification Engine
Sends email alerts via GoDaddy SMTP
"""
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger("charvakit.email")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtpout.secureserver.net")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "hr@charvakit.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "hr@charvakit.com")

EMAIL_ENABLED = bool(SMTP_PASSWORD)


class EmailEngine:
    """Handles all email notifications."""

    def __init__(self):
        self.enabled = EMAIL_ENABLED
        self.sent_count = 0
        if self.enabled:
            logger.info("✅ Email Engine: ENABLED")
        else:
            logger.warning("⚠️ Email Engine: DISABLED (set SMTP_PASSWORD to enable)")

    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> Dict:
        """Send an email via GoDaddy SMTP."""
        if not self.enabled:
            logger.info(f"[EMAIL DISABLED] To: {to_email} | Subject: {subject}")
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

            try:
                with smtplib.SMTP(SMTP_SERVER, 587) as server:
                    server.starttls()
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                    server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
            except Exception:
                with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                    server.sendmail(SMTP_USERNAME, to_email, msg.as_string())

            self.sent_count += 1
            logger.info(f"✅ Email sent to {to_email}: {subject}")

            return {
                "status": "success",
                "message": "Email sent successfully",
                "to": to_email,
                "subject": subject
            }
        except Exception as e:
            logger.error(f"Email failed to {to_email}: {e}")
            return {"status": "error", "message": f"Email failed: {str(e)}"}

    def notify_new_message(self, recipient_email: str, recipient_name: str, sender_name: str, message_preview: str) -> Dict:
        """Notify user of a new message."""
        subject = f"💬 New Message from {sender_name} on Charvak"
        body = f"""
Hi {recipient_name},

{sender_name} sent you a message on Charvak:

"{message_preview[:200]}"

Log in to read and reply: https://charvakit.com

— Charvak IT Consulting
"""
        return self.send_email(recipient_email, subject, body)

    def notify_application_received(self, candidate_email: str, candidate_name: str, job_title: str, company: str) -> Dict:
        """Notify candidate that application was received."""
        subject = f"✅ Application Received — {job_title} at {company}"
        body = f"""
Hi {candidate_name},

Your application for {job_title} at {company} has been received.

Track your application: https://charvakit.com/application-dashboard

— Charvak IT Consulting
"""
        return self.send_email(candidate_email, subject, body)

    def notify_rsvp_confirmed(self, attendee_email: str, attendee_name: str, event_title: str, event_date: str) -> Dict:
        """Notify attendee of RSVP confirmation."""
        subject = f"🎟️ RSVP Confirmed — {event_title}"
        body = f"""
Hi {attendee_name},

Your RSVP for "{event_title}" on {event_date} is confirmed!

Event details: https://charvakit.com

— Charvak IT Consulting
"""
        return self.send_email(attendee_email, subject, body)

    def notify_payment_received(self, client_email: str, client_name: str, amount: float, service: str) -> Dict:
        """Notify client of payment received."""
        subject = f"💰 Payment Received — {service}"
        body = f"""
Hi {client_name},

We've received your payment of ₹{amount:,.2f} for {service}.

Receipt: https://charvakit.com/invoice

— Charvak IT Consulting
"""
        return self.send_email(client_email, subject, body)

    def notify_admin(self, subject: str, message: str) -> Dict:
        """Send notification to admin."""
        return self.send_email(ADMIN_EMAIL, subject, message)

    def get_stats(self) -> Dict:
        """Get email engine statistics."""
        return {
            "status": "success",
            "enabled": self.enabled,
            "smtp_server": SMTP_SERVER,
            "sender": SMTP_USERNAME,
            "total_sent": self.sent_count
        }


email_engine = EmailEngine()