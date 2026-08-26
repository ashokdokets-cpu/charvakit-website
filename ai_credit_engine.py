"""
Charvak AI Credit System
Complete credit management — tracking, limits, renewals, expiry, admin monitoring
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.credits")


class CreditPlan:
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class AICreditEngine:
    """Complete AI credit management system."""
    
    PLANS = {
        CreditPlan.FREE: {
            "name": "Free Trial",
            "price": 0,
            "credits": 50,
            "validity_days": 7,
            "daily_bonus": 0,
            "features": ["Basic AI tools", "50 credits to start"]
        },
        CreditPlan.STARTER: {
            "name": "Starter",
            "price": 99,
            "credits": 500,
            "validity_days": 30,
            "daily_bonus": 10,
            "features": ["All AI tools", "500 credits", "Daily bonus"]
        },
        CreditPlan.PRO: {
            "name": "Pro",
            "price": 299,
            "credits": 2000,
            "validity_days": 30,
            "daily_bonus": 25,
            "features": ["All AI tools", "2000 credits", "Priority processing"]
        },
        CreditPlan.PREMIUM: {
            "name": "Premium",
            "price": 999,
            "credits": 10000,
            "validity_days": 90,
            "daily_bonus": 50,
            "features": ["All AI tools", "10000 credits", "Premium support"]
        },
        CreditPlan.ENTERPRISE: {
            "name": "Enterprise",
            "price": 4999,
            "credits": 50000,
            "validity_days": 365,
            "daily_bonus": 100,
            "features": ["Unlimited AI", "Custom limits", "Dedicated support"]
        }
    }
    
    FEATURE_CREDITS = {
        "resume_roast": 5,
        "skill_assessment": 10,
        "ai_premium_report": 20,
        "voice_to_web": 30,
        "neural_wireframe": 25,
        "assignment_assistant": 10,
        "research_helper": 15,
        "fyp_topics": 5,
        "fyp_proposal": 15,
        "fyp_documentation": 30,
        "fyp_viva": 10,
        "marketing_job_ad": 10,
        "indian_language_assessment": 10,
        "lms_quiz": 5,
        "interview_prep": 8,
        "chatbot_query": 2,
        "default": 10
    }
    
    def __init__(self):
        self.user_credits = {}
        self.usage_history = []
        self.credit_purchases = []
        logger.info("AI Credit Engine ready")
    
    # ============================================================
    # USER CREDIT MANAGEMENT
    # ============================================================
    
    def initialize_user(self, email: str, plan: str = CreditPlan.FREE) -> Dict:
        """Initialize credits for new user."""
        if email in self.user_credits:
            return {"status": "exists", "message": "User already initialized"}
        
        plan_data = self.PLANS.get(plan, self.PLANS[CreditPlan.FREE])
        
        self.user_credits[email] = {
            "email": email,
            "plan": plan,
            "credits_remaining": plan_data["credits"],
            "total_credits_used": 0,
            "total_ai_calls": 0,
            "daily_usage": {},
            "last_daily_bonus": None,
            "expires_at": (datetime.now() + timedelta(days=plan_data["validity_days"])).isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Credits initialized for {email}: {plan_data['credits']} credits")
        
        return {"status": "success", "credits": plan_data["credits"], "message": "Credits initialized"}
    
    def get_user_credits(self, email: str) -> Dict:
        """Get user's credit balance."""
        user = self.user_credits.get(email)
        if not user:
            user = self.initialize_user(email).get("user")
        
        # Check expiry
        if user and datetime.fromisoformat(user["expires_at"]) < datetime.now():
            user["credits_remaining"] = 0
            user["plan"] = CreditPlan.FREE
        
        return {
            "status": "success",
            "email": email,
            "credits_remaining": user["credits_remaining"],
            "plan": user["plan"],
            "expires_at": user["expires_at"],
            "total_used": user["total_credits_used"]
        }
    
    # ============================================================
    # CREDIT USAGE
    # ============================================================
    
    def check_and_deduct(self, email: str, feature: str) -> Dict:
        """Check credits and deduct for AI usage."""
        user = self.user_credits.get(email)
        if not user:
            user = self.initialize_user(email).get("user")
            if not user:
                return {"status": "error", "message": "Failed to initialize user"}
        
        credits_needed = self.FEATURE_CREDITS.get(feature, self.FEATURE_CREDITS["default"])
        
        if user["credits_remaining"] < credits_needed:
            return {
                "status": "error",
                "message": f"Insufficient credits. Need {credits_needed} credits, have {user['credits_remaining']}.",
                "credits_needed": credits_needed,
                "credits_remaining": user["credits_remaining"],
                "top_up_url": "/pricing"
            }
        
        # Deduct credits
        user["credits_remaining"] -= credits_needed
        user["total_credits_used"] += credits_needed
        user["total_ai_calls"] += 1
        user["updated_at"] = datetime.now().isoformat()
        
        # Track daily usage
        today = datetime.now().date().isoformat()
        if today not in user["daily_usage"]:
            user["daily_usage"][today] = {"calls": 0, "credits": 0}
        user["daily_usage"][today]["calls"] += 1
        user["daily_usage"][today]["credits"] += credits_needed
        
        # Log usage
        usage_record = {
            "usage_id": f"CRED-{secrets.token_hex(4).upper()}",
            "email": email,
            "feature": feature,
            "credits_used": credits_needed,
            "timestamp": datetime.now().isoformat()
        }
        self.usage_history.append(usage_record)
        
        logger.info(f"Credits deducted: {email} - {feature} - {credits_needed} credits")
        
        return {
            "status": "success",
            "credits_deducted": credits_needed,
            "credits_remaining": user["credits_remaining"],
            "message": "Credits deducted successfully"
        }
    
    # ============================================================
    # RENEWALS & TOP-UP
    # ============================================================
    
    def purchase_credits(self, email: str, plan: str) -> Dict:
        """Purchase credit plan."""
        plan_data = self.PLANS.get(plan)
        if not plan_data:
            return {"status": "error", "message": "Invalid plan"}
        
        user = self.user_credits.get(email)
        if not user:
            self.initialize_user(email, plan)
            user = self.user_credits[email]
        
        # Add credits
        user["credits_remaining"] += plan_data["credits"]
        user["plan"] = plan
        user["expires_at"] = (datetime.now() + timedelta(days=plan_data["validity_days"])).isoformat()
        user["updated_at"] = datetime.now().isoformat()
        
        # Record purchase
        purchase = {
            "purchase_id": f"PURCH-{secrets.token_hex(4).upper()}",
            "email": email,
            "plan": plan,
            "price": plan_data["price"],
            "credits_added": plan_data["credits"],
            "purchased_at": datetime.now().isoformat()
        }
        self.credit_purchases.append(purchase)
        
        logger.info(f"Credits purchased: {email} - {plan} - {plan_data['credits']} credits")
        
        return {
            "status": "success",
            "credits_added": plan_data["credits"],
            "total_credits": user["credits_remaining"],
            "expires_at": user["expires_at"],
            "message": f"Purchased {plan_data['name']} — {plan_data['credits']} credits added"
        }
    
    def apply_daily_bonus(self, email: str) -> Dict:
        """Apply daily bonus credits."""
        user = self.user_credits.get(email)
        if not user:
            return {"status": "error", "message": "User not found"}
        
        plan_data = self.PLANS.get(user["plan"], self.PLANS[CreditPlan.FREE])
        bonus = plan_data.get("daily_bonus", 0)
        
        if bonus <= 0:
            return {"status": "skipped", "message": "No daily bonus for this plan"}
        
        today = datetime.now().date().isoformat()
        if user["last_daily_bonus"] == today:
            return {"status": "already_claimed", "message": "Daily bonus already claimed"}
        
        user["credits_remaining"] += bonus
        user["last_daily_bonus"] = today
        user["updated_at"] = datetime.now().isoformat()
        
        return {"status": "success", "bonus_added": bonus, "message": f"Daily bonus of {bonus} credits added"}
    
    # ============================================================
    # AUTO-RENEWAL
    # ============================================================
    
    def check_expiry(self, email: str) -> Dict:
        """Check if credits expired and handle renewal."""
        user = self.user_credits.get(email)
        if not user:
            return {"status": "error", "message": "User not found"}
        
        expires = datetime.fromisoformat(user["expires_at"])
        days_remaining = (expires - datetime.now()).days
        
        if days_remaining < 0:
            # Expired
            user["credits_remaining"] = 0
            return {
                "status": "expired",
                "message": "Credits expired. Please renew.",
                "renew_url": "/pricing"
            }
        elif days_remaining <= 3:
            # About to expire
            return {
                "status": "expiring_soon",
                "days_remaining": days_remaining,
                "message": f"Credits expire in {days_remaining} days. Renew to continue.",
                "renew_url": "/pricing"
            }
        
        return {"status": "active", "days_remaining": days_remaining}
    
    # ============================================================
    # ADMIN MONITORING
    # ============================================================
    
    def get_admin_stats(self) -> Dict:
        """Complete admin statistics."""
        total_users = len(self.user_credits)
        total_credits_used = sum(u["total_credits_used"] for u in self.user_credits.values())
        total_ai_calls = sum(u["total_ai_calls"] for u in self.user_credits.values())
        total_revenue = sum(p["price"] for p in self.credit_purchases)
        active_users = len([u for u in self.user_credits.values() 
                           if datetime.fromisoformat(u["expires_at"]) > datetime.now()])
        
        return {
            "status": "success",
            "stats": {
                "total_users": total_users,
                "active_users": active_users,
                "total_credits_used": total_credits_used,
                "total_ai_calls": total_ai_calls,
                "total_revenue": total_revenue,
                "total_purchases": len(self.credit_purchases),
                "plans": {k: {"price": v["price"], "credits": v["credits"]} for k, v in self.PLANS.items()}
            }
        }
    
    def get_user_usage_history(self, email: str, limit: int = 50) -> Dict:
        """Get user's AI usage history."""
        user_usage = [u for u in self.usage_history if u["email"] == email][-limit:]
        return {
            "status": "success",
            "usage": user_usage,
            "count": len(user_usage),
            "total_credits_used": sum(u["credits_used"] for u in user_usage)
        }


ai_credit_engine = AICreditEngine()