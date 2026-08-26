"""
Student Suite Engine - Accepts both email and student_email
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger("charvakit.student_suite")

class StudentSuiteEngine:
    def __init__(self):
        self.subscriptions = {}
        self.usage_tracking = {}
        logger.info("Student Suite Engine ready")
    
    def subscribe(self, email: str = None, student_email: str = None, plan: str = "free", **kwargs) -> Dict:
        """Handle subscription - accepts both email and student_email"""
        user_email = email or student_email or kwargs.get('data', {}).get('email')
        
        if not user_email:
            return {"status": "error", "message": "Email is required"}
        
        plans = {
            "free": {"name": "Free", "requests": 10, "price": 0},
            "pro": {"name": "Student Pro", "requests": 100, "price": 99},
            "premium": {"name": "Premium", "requests": 500, "price": 499}
        }
        
        if plan not in plans:
            return {"status": "error", "message": "Invalid plan"}
        
        self.subscriptions[user_email] = {
            "plan": plan,
            "plan_details": plans[plan],
            "subscribed_at": "2026-08-27",
            "requests_used": 0
        }
        
        return {
            "status": "success",
            "message": f"Subscribed to {plans[plan]['name']} plan",
            "plan": plans[plan],
            "email": user_email
        }
    
    def assist_assignment(self, email: str = None, student_email: str = None, subject: str = "", topic: str = "", **kwargs) -> Dict:
        """Assignment assistance - accepts both email formats"""
        user_email = email or student_email
        
        if not user_email:
            return {"status": "error", "message": "Email is required"}
        
        if not self._check_subscription(user_email):
            return {"status": "error", "message": "No active subscription. Please subscribe first."}
        
        self._track_usage(user_email, "assignment")
        
        return {
            "status": "success",
            "message": "Assignment assistance generated",
            "subject": subject,
            "topic": topic,
            "email": user_email
        }
    
    def assist_research(self, email: str = None, student_email: str = None, field: str = "", topic: str = "", **kwargs) -> Dict:
        """Research assistance - accepts both email formats"""
        user_email = email or student_email
        
        if not user_email:
            return {"status": "error", "message": "Email is required"}
        
        if not self._check_subscription(user_email):
            return {"status": "error", "message": "No active subscription. Please subscribe first."}
        
        self._track_usage(user_email, "research")
        
        return {
            "status": "success",
            "message": "Research assistance generated",
            "field": field,
            "topic": topic,
            "email": user_email
        }
    
    def get_plan(self, email: str) -> Dict:
        """Get user's plan"""
        if email in self.subscriptions:
            return {
                "status": "success",
                "subscription": self.subscriptions[email]
            }
        return {"status": "error", "message": "No subscription found"}
    
    def get_stats(self) -> Dict:
        """Get suite stats"""
        return {
            "status": "success",
            "total_subscribers": len(self.subscriptions),
            "total_usage": sum(len(v) for v in self.usage_tracking.values()),
            "usage_by_feature": self.usage_tracking
        }
    
    def _check_subscription(self, email: str) -> bool:
        """Check if user has active subscription"""
        return email in self.subscriptions
    
    def _track_usage(self, email: str, feature: str) -> None:
        """Track usage"""
        if email not in self.usage_tracking:
            self.usage_tracking[email] = {}
        if feature not in self.usage_tracking[email]:
            self.usage_tracking[email][feature] = 0
        self.usage_tracking[email][feature] += 1

student_suite_engine = StudentSuiteEngine()
