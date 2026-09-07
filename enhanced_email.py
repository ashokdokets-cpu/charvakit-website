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

enhanced_email = EnhancedEmailSystem()
