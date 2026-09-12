"""
Charvak AI Credit System
Complete credit management - tracking, limits, renewals, expiry, admin monitoring
Database-backed: state persists across restarts (Render, uvicorn, deploys)
"""
import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.credits")

# Admin emails - full access, no credit deduction
ADMIN_EMAILS = {"charvakit@gmail.com", "hr@charvakit.com"}


class CreditPlan:
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class AICreditEngine:
    """Complete AI credit management system. Postgres-backed."""

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
        "ai_questions": 5,
        "practice_test": 5,
        "mock_test": 20,
        "default": 10
    }

    def __init__(self):
        self._ensure_tables()
        logger.info("AI Credit Engine ready (database-backed)")

    def _ensure_tables(self):
        """Create the credit tables if they don't exist. Idempotent."""
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS charvak_user_credits (
                    email TEXT PRIMARY KEY,
                    plan TEXT NOT NULL DEFAULT 'free',
                    credits_remaining INTEGER NOT NULL DEFAULT 0,
                    total_credits_used INTEGER NOT NULL DEFAULT 0,
                    total_ai_calls INTEGER NOT NULL DEFAULT 0,
                    daily_usage JSONB NOT NULL DEFAULT '{}'::jsonb,
                    last_daily_bonus DATE,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS charvak_credit_usage_history (
                    usage_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    feature TEXT NOT NULL,
                    credits_used INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS charvak_credit_purchases (
                    purchase_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    credits_added INTEGER NOT NULL,
                    payment_id TEXT UNIQUE,
                    status TEXT NOT NULL DEFAULT 'completed',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_charvak_usage_email
                ON charvak_credit_usage_history(email)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_charvak_purchases_email
                ON charvak_credit_purchases(email)
            """)

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Credit tables init failed: {e}")

    def _row_to_user(self, row) -> Dict:
        """Convert a user_credits row to the dict shape the rest of the code expects."""
        if not row:
            return None
        (email, plan, credits_remaining, total_credits_used, total_ai_calls,
         daily_usage, last_daily_bonus, expires_at, created_at, updated_at) = row

        if isinstance(daily_usage, str):
            try:
                daily_usage = json.loads(daily_usage)
            except Exception:
                daily_usage = {}
        if daily_usage is None:
            daily_usage = {}

        return {
            "email": email,
            "plan": plan,
            "credits_remaining": credits_remaining,
            "total_credits_used": total_credits_used,
            "total_ai_calls": total_ai_calls,
            "daily_usage": daily_usage,
            "last_daily_bonus": last_daily_bonus.isoformat() if last_daily_bonus else None,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "created_at": created_at.isoformat() if created_at else None,
            "updated_at": updated_at.isoformat() if updated_at else None,
        }

    def _fetch_user(self, cursor, email: str) -> Optional[Dict]:
        cursor.execute("""
            SELECT email, plan, credits_remaining, total_credits_used, total_ai_calls,
                   daily_usage, last_daily_bonus, expires_at, created_at, updated_at
            FROM charvak_user_credits WHERE email = %s
        """, (email,))
        return self._row_to_user(cursor.fetchone())

    def initialize_user(self, email: str, plan: str = CreditPlan.FREE) -> Dict:
        """Initialize credits for new user. Idempotent - returns 'exists' if already there."""
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()

            existing = self._fetch_user(cursor, email)
            if existing:
                cursor.close()
                conn.close()
                return {"status": "exists", "message": "User already initialized"}

            plan_data = self.PLANS.get(plan, self.PLANS[CreditPlan.FREE])
            expires_at = datetime.now() + timedelta(days=plan_data["validity_days"])

            cursor.execute("""
                INSERT INTO charvak_user_credits
                    (email, plan, credits_remaining, expires_at)
                VALUES (%s, %s, %s, %s)
            """, (email, plan, plan_data["credits"], expires_at))
            conn.commit()

            user = self._fetch_user(cursor, email)
            cursor.close()
            conn.close()

            logger.info(f"Credits initialized for {email}: {plan_data['credits']} credits")

            return {
                "status": "success",
                "credits": plan_data["credits"],
                "message": "Credits initialized",
                "user": user
            }
        except Exception as e:
            logger.error(f"initialize_user failed for {email}: {e}")
            return {"status": "error", "message": "Failed to initialize user"}

    def get_user_credits(self, email: str) -> Dict:
        """Get user's credit balance. Auto-initializes free plan if user is new."""
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()

            user = self._fetch_user(cursor, email)
            if not user:
                cursor.close()
                conn.close()
                init_result = self.initialize_user(email)
                if init_result["status"] == "success":
                    user = init_result["user"]
                else:
                    return {"status": "error", "message": "Failed to initialize user"}
                conn = db.get_connection()
                cursor = conn.cursor()

            expires_at = datetime.fromisoformat(user["expires_at"]) if user["expires_at"] else datetime.now()
            if expires_at < datetime.now() and user["plan"] != CreditPlan.FREE:
                cursor.execute("""
                    UPDATE charvak_user_credits
                    SET credits_remaining = 0, plan = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE email = %s
                """, (CreditPlan.FREE, email))
                conn.commit()
                user = self._fetch_user(cursor, email)

            cursor.close()
            conn.close()

            return {
                "status": "success",
                "email": email,
                "credits_remaining": user["credits_remaining"],
                "plan": user["plan"],
                "expires_at": user["expires_at"],
                "total_used": user["total_credits_used"]
            }
        except Exception as e:
            logger.error(f"get_user_credits failed for {email}: {e}")
            return {"status": "error", "message": str(e)}

    def get_plans(self) -> Dict:
        """Get all plans in a clean serializable format."""
        serializable_plans = {}
        for plan_key, plan_data in self.PLANS.items():
            serializable_plans[plan_key] = {
                "name": plan_data["name"],
                "price": plan_data["price"],
                "credits": plan_data["credits"],
                "validity_days": plan_data["validity_days"],
                "daily_bonus": plan_data["daily_bonus"],
                "features": plan_data["features"]
            }
        return serializable_plans

    def check_and_deduct(self, email: str, feature: str) -> Dict:
        """Check credits and deduct for AI usage. Admin bypass preserved."""
        if (email or "").lower() in ADMIN_EMAILS:
            return {
                "status": "success",
                "credits_deducted": 0,
                "credits_remaining": 999999999,
                "admin_bypass": True,
                "feature": feature,
            }

        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()

            user = self._fetch_user(cursor, email)
            if not user:
                cursor.close()
                conn.close()
                init_result = self.initialize_user(email)
                if init_result["status"] != "success":
                    return {"status": "error", "message": "Failed to initialize user"}
                user = init_result["user"]
                conn = db.get_connection()
                cursor = conn.cursor()

            credits_needed = self.FEATURE_CREDITS.get(feature, self.FEATURE_CREDITS["default"])

            if user["credits_remaining"] < credits_needed:
                cursor.close()
                conn.close()
                return {
                    "status": "error",
                    "message": f"Insufficient credits. Need {credits_needed} credits, have {user['credits_remaining']}.",
                    "credits_needed": credits_needed,
                    "credits_remaining": user["credits_remaining"],
                    "top_up_url": "/pricing"
                }

            today = datetime.now().date().isoformat()
            daily = user["daily_usage"] or {}
            if today not in daily:
                daily[today] = {"calls": 0, "credits": 0}
            daily[today]["calls"] += 1
            daily[today]["credits"] += credits_needed

            cursor.execute("""
                UPDATE charvak_user_credits
                SET credits_remaining = credits_remaining - %s,
                    total_credits_used = total_credits_used + %s,
                    total_ai_calls = total_ai_calls + 1,
                    daily_usage = %s::jsonb,
                    updated_at = CURRENT_TIMESTAMP
                WHERE email = %s
            """, (credits_needed, credits_needed, json.dumps(daily), email))

            usage_id = f"CRED-{secrets.token_hex(4).upper()}"
            cursor.execute("""
                INSERT INTO charvak_credit_usage_history
                    (usage_id, email, feature, credits_used)
                VALUES (%s, %s, %s, %s)
            """, (usage_id, email, feature, credits_needed))

            conn.commit()
            new_balance = user["credits_remaining"] - credits_needed
            cursor.close()
            conn.close()

            logger.info(f"Credits deducted: {email} - {feature} - {credits_needed} credits")

            return {
                "status": "success",
                "credits_deducted": credits_needed,
                "credits_remaining": new_balance,
                "message": "Credits deducted successfully"
            }
        except Exception as e:
            logger.error(f"check_and_deduct failed for {email}: {e}")
            return {"status": "error", "message": str(e)}

    def purchase_credits(self, email: str, plan: str, payment_id: str = None) -> Dict:
        """Purchase credit plan.

        payment_id is optional for now (Fix A will require it for paid plans).
        If provided and already used, returns idempotently - no double-credit.
        """
        plan_data = self.PLANS.get(plan)
        if not plan_data:
            return {"status": "error", "message": "Invalid plan"}

        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()

            if payment_id:
                cursor.execute("""
                    SELECT purchase_id FROM charvak_credit_purchases
                    WHERE payment_id = %s AND status = 'completed'
                """, (payment_id,))
                if cursor.fetchone():
                    user = self._fetch_user(cursor, email)
                    cursor.close()
                    conn.close()
                    return {
                        "status": "success",
                        "credits_added": 0,
                        "total_credits": user["credits_remaining"] if user else 0,
                        "expires_at": user["expires_at"] if user else None,
                        "message": "Already credited (duplicate payment_id)",
                        "already_credited": True
                    }

            user = self._fetch_user(cursor, email)
            if not user:
                cursor.close()
                conn.close()
                init_result = self.initialize_user(email, plan)
                if init_result["status"] != "success":
                    return {"status": "error", "message": "Failed to initialize user"}
                conn = db.get_connection()
                cursor = conn.cursor()
                user = self._fetch_user(cursor, email)

            new_credits = user["credits_remaining"] + plan_data["credits"]
            new_expires = datetime.now() + timedelta(days=plan_data["validity_days"])

            cursor.execute("""
                UPDATE charvak_user_credits
                SET credits_remaining = %s,
                    plan = %s,
                    expires_at = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE email = %s
            """, (new_credits, plan, new_expires, email))

            purchase_id = f"PURCH-{secrets.token_hex(4).upper()}"
            cursor.execute("""
                INSERT INTO charvak_credit_purchases
                    (purchase_id, email, plan, price, credits_added, payment_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'completed')
            """, (purchase_id, email, plan, plan_data["price"], plan_data["credits"], payment_id))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Credits purchased: {email} - {plan} - {plan_data['credits']} credits")

            return {
                "status": "success",
                "credits_added": plan_data["credits"],
                "total_credits": new_credits,
                "expires_at": new_expires.isoformat(),
                "message": f"Purchased {plan_data['name']} - {plan_data['credits']} credits added"
            }
        except Exception as e:
            logger.error(f"purchase_credits failed for {email}: {e}")
            return {"status": "error", "message": str(e)}

    def apply_daily_bonus(self, email: str) -> Dict:
        """Apply daily bonus credits."""
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()

            user = self._fetch_user(cursor, email)
            if not user:
                cursor.close()
                conn.close()
                return {"status": "error", "message": "User not found"}

            plan_data = self.PLANS.get(user["plan"], self.PLANS[CreditPlan.FREE])
            bonus = plan_data.get("daily_bonus", 0)

            if bonus <= 0:
                cursor.close()
                conn.close()
                return {"status": "skipped", "message": "No daily bonus for this plan"}

            today_str = datetime.now().date().isoformat()
            if user["last_daily_bonus"] == today_str:
                cursor.close()
                conn.close()
                return {"status": "already_claimed", "message": "Daily bonus already claimed"}

            cursor.execute("""
                UPDATE charvak_user_credits
                SET credits_remaining = credits_remaining + %s,
                    last_daily_bonus = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE email = %s
            """, (bonus, today_str, email))
            conn.commit()
            cursor.close()
            conn.close()

            return {"status": "success", "bonus_added": bonus, "message": f"Daily bonus of {bonus} credits added"}
        except Exception as e:
            logger.error(f"apply_daily_bonus failed for {email}: {e}")
            return {"status": "error", "message": str(e)}

    def check_expiry(self, email: str) -> Dict:
        """Check if credits expired and handle renewal."""
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()

            user = self._fetch_user(cursor, email)
            if not user:
                cursor.close()
                conn.close()
                return {"status": "error", "message": "User not found"}

            expires = datetime.fromisoformat(user["expires_at"]) if user["expires_at"] else datetime.now()
            days_remaining = (expires - datetime.now()).days

            if days_remaining < 0:
                cursor.execute("""
                    UPDATE charvak_user_credits
                    SET credits_remaining = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE email = %s
                """, (email,))
                conn.commit()
                cursor.close()
                conn.close()
                return {
                    "status": "expired",
                    "message": "Credits expired. Please renew.",
                    "renew_url": "/pricing"
                }
            elif days_remaining <= 3:
                cursor.close()
                conn.close()
                return {
                    "status": "expiring_soon",
                    "days_remaining": days_remaining,
                    "message": f"Credits expire in {days_remaining} days. Renew to continue.",
                    "renew_url": "/pricing"
                }

            cursor.close()
            conn.close()
            return {"status": "active", "days_remaining": days_remaining}
        except Exception as e:
            logger.error(f"check_expiry failed for {email}: {e}")
            return {"status": "error", "message": str(e)}

    def get_admin_stats(self) -> Dict:
        """Complete admin statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM charvak_user_credits")
            total_users = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM charvak_user_credits WHERE expires_at > CURRENT_TIMESTAMP")
            active_users = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COALESCE(SUM(total_credits_used), 0) FROM charvak_user_credits")
            total_credits_used = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COALESCE(SUM(total_ai_calls), 0) FROM charvak_user_credits")
            total_ai_calls = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COALESCE(SUM(price), 0) FROM charvak_credit_purchases WHERE status = 'completed'")
            total_revenue = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM charvak_credit_purchases WHERE status = 'completed'")
            total_purchases = cursor.fetchone()[0] or 0

            cursor.close()
            conn.close()

            return {
                "status": "success",
                "stats": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "total_credits_used": int(total_credits_used),
                    "total_ai_calls": int(total_ai_calls),
                    "total_revenue": int(total_revenue),
                    "total_purchases": int(total_purchases),
                    "plans": self.get_plans()
                }
            }
        except Exception as e:
            logger.error(f"get_admin_stats failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_user_usage_history(self, email: str, limit: int = 50) -> Dict:
        """Get user's AI usage history."""
        try:
            from database import db
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT usage_id, email, feature, credits_used, created_at
                FROM charvak_credit_usage_history
                WHERE email = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (email, limit))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            usage = []
            for r in rows:
                usage.append({
                    "usage_id": r[0],
                    "email": r[1],
                    "feature": r[2],
                    "credits_used": r[3],
                    "timestamp": r[4].isoformat() if r[4] else None
                })

            return {
                "status": "success",
                "usage": usage,
                "count": len(usage),
                "total_credits_used": sum(u["credits_used"] for u in usage)
            }
        except Exception as e:
            logger.error(f"get_user_usage_history failed for {email}: {e}")
            return {"status": "error", "message": str(e)}


ai_credit_engine = AICreditEngine()