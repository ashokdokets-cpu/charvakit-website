"""
Charvak Unified Analytics - Integrates with existing engines
"""
import logging
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger("charvakit.unified_analytics")

class UnifiedAnalytics:
    def __init__(self):
        self.events = []
        self.daily_stats = defaultdict(lambda: {"users": 0, "revenue": 0, "assessments": 0, "emails": 0})
        logger.info("Unified Analytics ready")
    
    def track(self, event_type, data=None):
        event = {
            "type": event_type,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        
        today = datetime.now().strftime("%Y-%m-%d")
        if event_type == "user_registered":
            self.daily_stats[today]["users"] += 1
        elif event_type == "payment":
            self.daily_stats[today]["revenue"] += data.get("amount", 0) if data else 0
        elif event_type == "assessment":
            self.daily_stats[today]["assessments"] += 1
        elif event_type == "email_sent":
            self.daily_stats[today]["emails"] += 1
        
        return {"status": "success"}
    
    def get_dashboard(self):
        from email_engine import email_engine
        from notification_engine import notification_engine
        from exam_analytics_engine import exam_analytics_engine
        
        return {
            "status": "success",
            "email_stats": email_engine.get_stats(),
            "notification_stats": notification_engine.get_stats(),
            "daily_stats": dict(self.daily_stats),
            "total_events": len(self.events)
        }

unified_analytics = UnifiedAnalytics()
