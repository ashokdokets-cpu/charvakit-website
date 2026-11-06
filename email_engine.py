"""
Charvak Email Engine
Uses Brevo (primary) or SendGrid (fallback) for reliable email delivery
"""
import os
import logging
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("charvakit.email")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "charvakit@gmail.com")
FROM_EMAIL = "charvakit@gmail.com"

EMAIL_ENABLED = bool(BREVO_API_KEY or SENDGRID_API_KEY)


class EmailEngine:
    """Email notifications via Brevo / SendGrid."""

    def __init__(self):
        self.enabled = EMAIL_ENABLED
        self.sent_count = 0
        if self.enabled:
            provider = "Brevo" if BREVO_API_KEY else "SendGrid"
            logger.info(f"Email Engine: ENABLED ({provider})")
        else:
            logger.warning("Email Engine: DISABLED (set BREVO_API_KEY or SENDGRID_API_KEY)")

    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = True,
                   attachment_bytes=None, attachment_filename=None,
                   from_email: str = None, from_name: str = None,
                   reply_to: str = None) -> Dict:
        """
        Send email via Brevo (primary) or SendGrid (fallback).

        Optional from_email/from_name/reply_to override the default sender.
        When None, defaults to hr@charvakit.com / Charvak IT Consulting.
        """
        if not self.enabled:
            logger.warning(f"Email disabled - would send to {to_email}: {subject}")
            return {"status": "disabled", "message": "Email not configured"}

        if BREVO_API_KEY:
            return self._send_via_brevo(
                to_email, subject, body, is_html, attachment_bytes, attachment_filename,
                from_email=from_email, from_name=from_name, reply_to=reply_to
            )
        else:
            return self._send_via_sendgrid(
                to_email, subject, body, is_html, attachment_bytes, attachment_filename,
                from_email=from_email, from_name=from_name, reply_to=reply_to
            )

    def _send_via_brevo(self, to_email, subject, body, is_html,
                        attachment_bytes, attachment_filename,
                        from_email=None, from_name=None, reply_to=None) -> Dict:
        """Send email via Brevo REST API (v3)."""
        try:
            import requests
            import json
            import base64

            # Resolve sender — explicit override wins, otherwise defaults
            _sender_email = from_email or "hr@charvakit.com"
            _sender_name = from_name or "Charvak IT Consulting"
            _reply_email = reply_to or _sender_email
            _reply_name = from_name if (reply_to and from_name) else _sender_name

            payload = {
                "sender": {
                    "email": _sender_email,
                    "name": _sender_name
                },
                "to": [{"email": to_email}],
                "replyTo": {
                    "email": _reply_email,
                    "name": _reply_name
                },
                "subject": subject,
                "htmlContent": body if is_html else f"<pre>{body}</pre>"
            }

            if attachment_bytes and attachment_filename:
                payload["attachment"] = [
                    {
                        "content": base64.b64encode(attachment_bytes).decode("ascii"),
                        "name": attachment_filename,
                    }
                ]

            response = requests.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "accept": "application/json",
                    "api-key": BREVO_API_KEY,
                    "content-type": "application/json"
                },
                data=json.dumps(payload),
                timeout=15
            )

            if response.status_code in (201, 202):
                self.sent_count += 1
                try:
                    message_id = response.json().get("messageId", "")
                except Exception:
                    message_id = ""
                logger.info(f"Email sent via Brevo to {to_email}: {subject} (msg_id={message_id[:20]})")
                return {"status": "success", "message": "Email sent via Brevo", "to": to_email, "provider": "brevo"}
            else:
                logger.error(f"Brevo error: {response.status_code} - {response.text[:200]}")
                if SENDGRID_API_KEY:
                    logger.info("Falling back to SendGrid")
                    return self._send_via_sendgrid(
                        to_email, subject, body, is_html, attachment_bytes, attachment_filename,
                        from_email=from_email, from_name=from_name, reply_to=reply_to
                    )
                return {"status": "error", "message": f"Brevo error: {response.status_code}", "provider": "brevo"}

        except Exception as e:
            logger.error(f"Brevo send failed: {e}")
            if SENDGRID_API_KEY:
                logger.info("Falling back to SendGrid")
                return self._send_via_sendgrid(
                    to_email, subject, body, is_html, attachment_bytes, attachment_filename,
                    from_email=from_email, from_name=from_name, reply_to=reply_to
                )
            return {"status": "error", "message": str(e), "provider": "brevo"}

    def _send_via_sendgrid(self, to_email, subject, body, is_html,
                           attachment_bytes, attachment_filename,
                           from_email=None, from_name=None, reply_to=None) -> Dict:
        """Send email via SendGrid v3 (fallback provider)."""
        try:
            import requests
            import json
            import base64

            _sender_email = from_email or "charvakit@gmail.com"
            _sender_name = from_name or "Charvak IT Consulting"
            _reply_email = reply_to or _sender_email

            payload = {
                "personalizations": [
                    {
                        "to": [{"email": to_email}],
                        "subject": subject
                    }
                ],
                "from": {
                    "email": _sender_email,
                    "name": _sender_name
                },
                "reply_to": {
                    "email": _reply_email,
                    "name": _sender_name
                },
                "content": [
                    {
                        "type": "text/html" if is_html else "text/plain",
                        "value": body
                    }
                ]
            }

            if attachment_bytes and attachment_filename:
                payload["attachments"] = [
                    {
                        "content": base64.b64encode(attachment_bytes).decode("ascii"),
                        "filename": attachment_filename,
                        "type": "application/pdf",
                        "disposition": "attachment",
                    }
                ]

            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {SENDGRID_API_KEY}",
                    "Content-Type": "application/json"
                },
                data=json.dumps(payload),
                timeout=10
            )

            if response.status_code == 202:
                self.sent_count += 1
                logger.info(f"Email sent via SendGrid to {to_email}: {subject}")
                return {"status": "success", "message": "Email sent via SendGrid", "to": to_email, "provider": "sendgrid"}
            else:
                logger.error(f"SendGrid error: {response.status_code} - {response.text[:200]}")
                return {"status": "error", "message": f"SendGrid error: {response.status_code}", "provider": "sendgrid"}

        except Exception as e:
            logger.error(f"SendGrid send failed: {e}")
            return {"status": "error", "message": str(e), "provider": "sendgrid"}

    def notify_admin(self, subject: str, message: str) -> Dict:
        return self.send_email(ADMIN_EMAIL, subject, message)

    def notify_new_message(self, recipient_email: str, recipient_name: str,
                           sender_name: str, message_preview: str) -> Dict:
        subject = f"New Message from {sender_name} on Charvak"
        body = f"Hi {recipient_name},\n\n{sender_name} sent you a message on Charvak.\n\n{message_preview[:200]}\n\nLogin: https://charvakit.com"
        return self.send_email(recipient_email, subject, body)

    def notify_application_received(self, candidate_email: str, candidate_name: str,
                                    job_title: str, company: str) -> Dict:
        subject = f"Application Received - {job_title} at {company}"
        body = f"Hi {candidate_name},\n\nYour application for {job_title} at {company} has been received."
        return self.send_email(candidate_email, subject, body)

    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "enabled": self.enabled,
            "provider": "Brevo" if BREVO_API_KEY else "SendGrid",
            "sender": FROM_EMAIL,
            "total_sent": self.sent_count
        }


email_engine = EmailEngine()


def send_engagement_nudge(to_email: str, subject: str, html_body: str) -> dict:
    """Send engagement-related email (nudges, milestones, weekly summaries)."""
    return email_engine.send_email(to_email, subject, html_body, is_html=True)