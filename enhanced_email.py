"""
Charvak Enhanced Email - Wraps existing email_engine
Adds: Templates, Tracking, Bulk
"""
import logging
from datetime import datetime

logger = logging.getLogger("charvakit.enhanced_email")

class EnhancedEmailSystem:
    def __init__(self):
        from email_engine import email_engine
        from notification_engine import notification_engine
        self.email_engine = email_engine
        self.notification_engine = notification_engine
        self.sent_emails = []
        logger.info("Enhanced Email ready")
    
    def send_welcome(self, email, name):
        """Send welcome email using existing engine."""
        result = self.email_engine.send_email(
            email,
            f"Welcome to Charvak, {name}!",
            f"Hello {name}, welcome to Charvak IT Consulting."
        )
        self.sent_emails.append({"type": "welcome", "email": email, "time": datetime.now().isoformat()})
        return result
    
    def send_payment_confirmation(self, email, amount):
        """Send payment confirmation."""
        result = self.email_engine.send_email(
            email,
            "Payment Confirmed",
            f"Your payment of {amount} has been received."
        )
        self.sent_emails.append({"type": "payment", "email": email, "amount": amount})
        return result

    def send_internship_enrollment(self, email, name, program_name, tier_name,
                                   amount_inr, enrollment_id, duration_weeks, total_days):
        """Send internship enrollment confirmation with next steps."""
        name = (name or "there").strip() or "there"
        subject = f"You're enrolled: {program_name} ({tier_name})"
        body = (
            f"<h2>Welcome aboard, {name}!</h2>"
            f"<p>Your enrollment is confirmed.</p>"
            f"<table style='border-collapse:collapse'>"
            f"<tr><td style='padding:4px 12px 4px 0'><strong>Program</strong></td><td>{program_name}</td></tr>"
            f"<tr><td style='padding:4px 12px 4px 0'><strong>Plan</strong></td><td>{tier_name}</td></tr>"
            f"<tr><td style='padding:4px 12px 4px 0'><strong>Duration</strong></td><td>{duration_weeks} weeks ({total_days} business days)</td></tr>"
            f"<tr><td style='padding:4px 12px 4px 0'><strong>Amount paid</strong></td><td>Rs {amount_inr}</td></tr>"
            f"<tr><td style='padding:4px 12px 4px 0'><strong>Enrollment ID</strong></td><td><code>{enrollment_id}</code></td></tr>"
            f"</table>"
            f"<h3>What happens next</h3>"
            f"<ol>"
            f"<li><strong>Day 1 unlocks immediately</strong> at <a href='https://www.charvakit.com/ai-internship'>charvakit.com/ai-internship</a></li>"
            f"<li><strong>AI mentor available 24/7</strong> \u2014 ask questions, get feedback on submissions</li>"
            f"<li><strong>Submit your work daily</strong> for structured AI feedback with strengths and improvements</li>"
            f"<li><strong>Verified digital badge</strong> on completion, shareable to LinkedIn</li>"
            f"</ol>"
            f"<p>Questions? Reply to this email \u2014 we're here to help.</p>"
            f"<p>\u2014 The Charvak Team</p>"
        )
        result = self.email_engine.send_email(email, subject, body)
        self.sent_emails.append({"type": "internship_enrollment", "email": email, "enrollment_id": enrollment_id})
        return result
    
    def send_assessment_result(self, email, assessment, score):
        """Send assessment results."""
        result = self.email_engine.send_email(
            email,
            f"Your {assessment} Results",
            f"You scored {score} in {assessment}."
        )
        self.sent_emails.append({"type": "assessment", "email": email, "score": score})
        return result
    
    def send_subscription_confirmation(self, email, plan):
        """Send subscription confirmation."""
        result = self.email_engine.send_email(
            email,
            f"Subscription Activated: {plan}",
            f"Your {plan} subscription is now active."
        )
        self.sent_emails.append({"type": "subscription", "email": email, "plan": plan})
        return result
    
    def get_sent_history(self):
        """Get sent email history."""
        return {"status": "success", "total": len(self.sent_emails), "emails": self.sent_emails}


    def send_silent_killer_alert(self, email, watch_name, url, new_status,
                                 status_code=None, error=None, previous_status=None):
        """Send a Silent-Killer state-change alert (Session 15)."""
        name = watch_name or url or 'your monitor'
        if new_status == "fail":
            subject = f"[DOWN] {name} is failing"
            body = (
                f"<h2>Monitor failure detected</h2>"
                f"<p><strong>URL:</strong> {url}</p>"
                f"<p><strong>Status code:</strong> {status_code or 'n/a'}</p>"
                f"<p><strong>Error:</strong> {error or 'unknown'}</p>"
                f"<p><strong>Previous:</strong> {previous_status or 'unknown'} &rarr; {new_status}</p>"
                f"<p>View the dashboard: <a href=\"https://www.charvakit.com/silent-killer\">https://www.charvakit.com/silent-killer</a></p>"
            )
        else:
            subject = f"[RECOVERED] {name} is healthy again"
            body = (
                f"<h2>Monitor recovered</h2>"
                f"<p><strong>URL:</strong> {url}</p>"
                f"<p><strong>Status code:</strong> {status_code or 'n/a'}</p>"
                f"<p><strong>Previous:</strong> {previous_status or 'unknown'} &rarr; {new_status}</p>"
                f"<p>View the dashboard: <a href=\"https://www.charvakit.com/silent-killer\">https://www.charvakit.com/silent-killer</a></p>"
            )

        result = self.email_engine.send_email(email, subject, body, is_html=True)
        self.sent_emails.append({
            "type": "silent_killer_alert",
            "email": email,
            "url": url,
            "new_status": new_status,
            "time": datetime.now().isoformat(),
        })
        return result


    def send_premium_report_email(self, email, report_title, report_id,
                                  pdf_bytes=None, download_url=None):
        """Send the Premium Report notification + PDF attachment (Session 16)."""
        subject = "Your " + str(report_title) + " is ready"
        body_html = (
            "<h2>Your Premium Report is ready</h2>"
            "<p>Hi,</p>"
            "<p>Your <strong>" + str(report_title) + "</strong> has been generated.</p>"
            "<p>Report ID: <code>" + str(report_id) + "</code></p>"
            "<p>The PDF is attached to this email. You can also download it anytime from your dashboard.</p>"
            "<p>The Charvak team</p>"
        )

        result = self.email_engine.send_email(
            email, subject, body_html, is_html=True,
            attachment_bytes=pdf_bytes,
            attachment_filename="Charvak-Premium-Report-" + str(report_id) + ".pdf",
        )
        self.sent_emails.append({
            "type": "premium_report",
            "email": email,
            "report_id": report_id,
            "time": datetime.now().isoformat(),
        })
        return result

    def send_readiness_improved(self, email, old_score, new_score,
                                new_cert_id, old_cert_id):
        """Session 20: notify the user when a new certificate supersedes an older one."""
        import os as _os
        site = _os.getenv("SITE_URL", "https://www.charvakit.com").rstrip("/")
        subject = "Your Role Readiness score improved"
        diff = int(new_score or 0) - int(old_score or 0)
        sign = "+" if diff >= 0 else ""
        body_html = (
            "<h2>Your Role Readiness score improved</h2>"
            "<p>Hi,</p>"
            "<p>You just completed a longer assessment and your Role Readiness score went from "
            "<strong>" + str(old_score) + "</strong> to <strong>" + str(new_score) + "</strong> "
            "(" + sign + str(diff) + " points).</p>"
            "<p><a href='" + site + "/readiness/" + str(new_cert_id) + "'>"
            "View your new certificate</a></p>"
            "<p>Your earlier certificate is still available at "
            "<a href='" + site + "/readiness/" + str(old_cert_id) + "'>this link</a>.</p>"
            "<p>&mdash; The Charvak team</p>"
        )
        try:
            result = self.email_engine.send_email(email, subject, body_html, is_html=True)
            self.sent_emails.append({
                "type": "readiness_improved",
                "email": email,
                "new_cert_id": new_cert_id,
                "old_cert_id": old_cert_id,
                "time": datetime.now().isoformat(),
            })
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}


enhanced_email = EnhancedEmailSystem()
