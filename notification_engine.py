"""
Charvak Notification Engine
Email notifications for credit alerts, purchase confirmations, and daily bonuses
"""
import logging
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.notifications")

class NotificationEngine:
    """Handles all email notifications for the Charvak platform."""
    
    def __init__(self):
        self.notifications = []
        self.email_enabled = os.getenv("SENDGRID_API_KEY") is not None
        self.from_email = "hr@charvakit.com"
        logger.info(f"Notification Engine ready (Email: {'enabled' if self.email_enabled else 'disabled'})")
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> Dict:
        """Send email notification."""
        notification = {
            "notification_id": f"NOTIF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{os.urandom(4).hex().upper()}",
            "to": to_email,
            "subject": subject,
            "html_content": html_content,
            "status": "sent" if self.email_enabled else "logged",
            "sent_at": datetime.now().isoformat()
        }
        
        self.notifications.append(notification)
        
        if self.email_enabled:
            try:
                from sendgrid import SendGridAPIClient
                from sendgrid.helpers.mail import Mail
                
                sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
                message = Mail(
                    from_email=self.from_email,
                    to_emails=to_email,
                    subject=subject,
                    html_content=html_content
                )
                sg.send(message)
                logger.info(f"Email sent to {to_email}: {subject}")
            except Exception as e:
                logger.error(f"SendGrid error: {e}")
                notification["status"] = "failed"
                return {"status": "error", "message": str(e)}
        else:
            logger.info(f"Email logged (SendGrid not configured): {to_email} - {subject}")
        
        return {
            "status": "success",
            "notification_id": notification["notification_id"],
            "message": f"Email {notification['status']}"
        }
    
    def notify_low_credits(self, email: str, credits_remaining: int, threshold: int = 20) -> Dict:
        """Send low credit alert."""
        if credits_remaining > threshold:
            return {"status": "skipped", "message": "Credits above threshold"}
        
        subject = "⚠️ Low Credit Alert - Charvak IT"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1a1a2e;">Your AI credits are running low!</h2>
            <p>You have <strong style="color: #dc2626;">{credits_remaining} credits</strong> remaining.</p>
            <p>Top up now to continue using our AI services without interruption.</p>
            <a href="https://charvakit-website.onrender.com/ai-credits-pricing" 
               style="display: inline-block; padding: 12px 24px; background-color: #3b82f6; 
                      color: white; text-decoration: none; border-radius: 6px; margin-top: 20px;">
                Buy More Credits
            </a>
        </div>
        """
        return self.send_email(email, subject, html)
    
    def notify_expiry(self, email: str, days_remaining: int) -> Dict:
        """Send expiry warning."""
        subject = "⏰ Credits Expiring Soon - Charvak IT"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1a1a2e;">Your credits expire in {days_remaining} days!</h2>
            <p>Renew now to keep your credits and continue using our services.</p>
            <a href="https://charvakit-website.onrender.com/ai-credits-pricing" 
               style="display: inline-block; padding: 12px 24px; background-color: #3b82f6; 
                      color: white; text-decoration: none; border-radius: 6px; margin-top: 20px;">
                Renew Now
            </a>
        </div>
        """
        return self.send_email(email, subject, html)
    
    def notify_purchase(self, email: str, plan_name: str, credits: int) -> Dict:
        """Send purchase confirmation."""
        subject = f"✅ Purchase Confirmed - {plan_name} Plan"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1a1a2e;">Thank you for your purchase!</h2>
            <p>You've successfully subscribed to the <strong>{plan_name}</strong> plan.</p>
            <p><strong style="color: #3b82f6;">{credits:,} credits</strong> have been added to your account.</p>
            <a href="https://charvakit-website.onrender.com/student-suite" 
               style="display: inline-block; padding: 12px 24px; background-color: #3b82f6; 
                      color: white; text-decoration: none; border-radius: 6px; margin-top: 20px;">
                Start Using AI Tools
            </a>
        </div>
        """
        return self.send_email(email, subject, html)
    
    def notify_daily_bonus(self, email: str, bonus: int, total_credits: int) -> Dict:
        """Send daily bonus notification."""
        subject = f"🎁 Daily Bonus Received - {bonus} Credits"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1a1a2e;">Daily bonus received!</h2>
            <p>You've received <strong style="color: #059669;">{bonus} bonus credits</strong>.</p>
            <p>Your total balance: <strong>{total_credits:,} credits</strong></p>
            <p>Come back tomorrow for more bonus credits!</p>
        </div>
        """
        return self.send_email(email, subject, html)
    
    def get_notification_history(self, email: str = None, limit: int = 50) -> Dict:
        """Get notification history."""
        filtered = self.notifications if not email else [n for n in self.notifications if n["to"] == email]
        return {
            "status": "success",
            "notifications": filtered[-limit:],
            "total": len(filtered)
        }
    
    def get_stats(self) -> Dict:
        """Get notification statistics."""
        sent = [n for n in self.notifications if n["status"] == "sent"]
        logged = [n for n in self.notifications if n["status"] == "logged"]
        failed = [n for n in self.notifications if n["status"] == "failed"]
        
        return {
            "status": "success",
            "stats": {
                "total": len(self.notifications),
                "sent": len(sent),
                "logged": len(logged),
                "failed": len(failed),
                "email_enabled": self.email_enabled
            }
        }


    # ============================================================
    # COURSE EMI NOTIFICATIONS (Tier 3, 2026-09-16)
    # ============================================================

    def _site_url(self):
        return os.getenv("SITE_URL", "https://www.charvakit.com").rstrip("/")

    def notify_installment_paid(self, email, enrollment_id, course_name,
                                installment_num, total, amount_inr,
                                unlocks_weeks, is_final=False):
        """Confirmation sent when an installment is successfully captured."""
        site = self._site_url()
        subject = f"Payment received - Installment {installment_num} of {total}"
        if is_final:
            subject = f"Course fully paid - {course_name} unlocked"
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
          <h2 style="color:#1a1a2e;">Payment received</h2>
          <p>Thanks for your payment for <strong>{course_name}</strong>.</p>
          <p><strong>Installment {installment_num} of {total}</strong> - INR {amount_inr}</p>
          <p>Weeks <strong>{unlocks_weeks}</strong> are now unlocked and ready for you.</p>
          <a href="{site}/my-course/{enrollment_id}"
             style="display:inline-block;padding:12px 24px;background:#3ba591;color:#fff;text-decoration:none;border-radius:6px;margin-top:16px;">
            Continue your course
          </a>
          <p style="margin-top:24px;color:#666;font-size:13px;">Need help? Reply to this email or write to hr@charvakit.com.</p>
        </div>
        """
        return self.send_email(email, subject, html)

    def notify_installment_due(self, email, enrollment_id, course_name,
                               installment_num, total, amount_inr,
                               unlocks_weeks, due_date, days_until=3):
        """Upcoming reminder - sent T-3 days and on due date."""
        site = self._site_url()
        if days_until > 0:
            subject = f"Upcoming payment in {days_until} days - {course_name}"
            lead = f"Your next installment is due in <strong>{days_until} days</strong>."
        else:
            subject = f"Installment due today - {course_name}"
            lead = "Your next installment is <strong>due today</strong>."
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
          <h2 style="color:#1a1a2e;">Upcoming course payment</h2>
          <p>{lead}</p>
          <table style="border-collapse:collapse;margin:16px 0;">
            <tr><td style="padding:4px 12px 4px 0;color:#666;">Course</td><td><strong>{course_name}</strong></td></tr>
            <tr><td style="padding:4px 12px 4px 0;color:#666;">Installment</td><td><strong>{installment_num} of {total}</strong></td></tr>
            <tr><td style="padding:4px 12px 4px 0;color:#666;">Amount</td><td><strong>INR {amount_inr}</strong></td></tr>
            <tr><td style="padding:4px 12px 4px 0;color:#666;">Unlocks</td><td><strong>Weeks {unlocks_weeks}</strong></td></tr>
            <tr><td style="padding:4px 12px 4px 0;color:#666;">Due date</td><td><strong>{due_date}</strong></td></tr>
          </table>
          <a href="{site}/my-course/{enrollment_id}"
             style="display:inline-block;padding:12px 24px;background:#3ba591;color:#fff;text-decoration:none;border-radius:6px;">
            Pay now
          </a>
          <p style="margin-top:24px;color:#666;font-size:13px;">You'll keep access to your earlier weeks. This unlocks the next block.</p>
        </div>
        """
        return self.send_email(email, subject, html)

    def notify_installment_overdue(self, email, enrollment_id, course_name,
                                   installment_num, total, amount_inr,
                                   unlocks_weeks, days_overdue):
        """Escalating overdue reminder - day 1, 3, 7."""
        site = self._site_url()
        subject = f"Payment overdue by {days_overdue} days - {course_name}"
        gentle = days_overdue <= 1
        tone_intro = (
            "Just a friendly reminder - your installment is now past its due date."
            if gentle else
            "Your installment is now overdue. Weeks beyond the current block remain locked until payment is completed."
        )
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
          <h2 style="color:#1a1a2e;">Payment reminder</h2>
          <p>{tone_intro}</p>
          <table style="border-collapse:collapse;margin:16px 0;">
            <tr><td style="padding:4px 12px 4px 0;color:#666;">Course</td><td><strong>{course_name}</strong></td></tr>
            <tr><td style="padding:4px 12px 4px 0;color:#666;">Installment</td><td><strong>{installment_num} of {total}</strong></td></tr>
            <tr><td style="padding:4px 12px 4px 0;color:#666;">Amount</td><td><strong>INR {amount_inr}</strong></td></tr>
            <tr><td style="padding:4px 12px 4px 0;color:#666;">Unlocks</td><td><strong>Weeks {unlocks_weeks}</strong></td></tr>
          </table>
          <a href="{site}/my-course/{enrollment_id}"
             style="display:inline-block;padding:12px 24px;background:#3ba591;color:#fff;text-decoration:none;border-radius:6px;">
            Pay and continue
          </a>
        </div>
        """
        return self.send_email(email, subject, html)

    def notify_access_attempt_blocked(self, email, enrollment_id, course_name,
                                      week_num, installment_num, total,
                                      amount_inr, unlocks_weeks, due_date):
        """In-context reminder: student clicked a locked week.
        Fires at the highest-intent moment. Friendly, actionable."""
        site = self._site_url()
        subject = f"Unlock Week {week_num} of {course_name}"
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
          <h2 style="color:#1a1a2e;">Just one step to continue</h2>
          <p>You tried to open <strong>Week {week_num}</strong> of <strong>{course_name}</strong>.</p>
          <p>Weeks <strong>{unlocks_weeks}</strong> unlock with <strong>Installment {installment_num} of {total}</strong> - INR {amount_inr}.</p>
          <p>Due date: <strong>{due_date}</strong></p>
          <a href="{site}/my-course/{enrollment_id}"
             style="display:inline-block;padding:12px 24px;background:#3ba591;color:#fff;text-decoration:none;border-radius:6px;margin-top:8px;">
            Pay now to unlock
          </a>
          <p style="margin-top:24px;color:#666;font-size:13px;">You'll keep access to your earlier weeks.</p>
        </div>
        """
        return self.send_email(email, subject, html)
notification_engine = NotificationEngine()