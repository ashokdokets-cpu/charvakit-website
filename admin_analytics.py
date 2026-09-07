"""
Charvak Admin Analytics - Integrates with existing admin dashboard
"""
import logging
from datetime import datetime

logger = logging.getLogger("charvakit.admin_analytics")

class AdminAnalyticsDashboard:
    def __init__(self):
        self.settings = {
            "platform_fee_percent": 20,
            "maintenance_mode": False,
            "auto_payout": True
        }
        logger.info("Admin Analytics ready")
    
    def get_full_overview(self):
        """Get complete overview using all existing systems."""
        from email_engine import email_engine
        from notification_engine import notification_engine
        from payment_engine import payment_engine
        from training_engine import training_engine
        from lms_engine import lms_engine
        from enhanced_payment import enhanced_payment
        
        return {
            "status": "success",
            "emails": {
                "sent": email_engine.sent_count,
                "enabled": email_engine.enabled
            },
            "notifications": notification_engine.get_stats(),
            "payments": {
                "total": len(payment_engine.payments),
                "mode": payment_engine.mode
            },
            "training": training_engine.get_stats() if hasattr(training_engine, 'get_stats') else {},
            "lms": lms_engine.get_stats() if hasattr(lms_engine, 'get_stats') else {},
            "subscriptions": {
                "plans": len(enhanced_payment.subscription_plans),
                "discounts": len(enhanced_payment.discount_codes)
            },
            "settings": self.settings
        }
    
    def update_setting(self, key, value):
        self.settings[key] = value
        return {"status": "success", "settings": self.settings}

admin_analytics = AdminAnalyticsDashboard()
