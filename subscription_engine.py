"""
Student Pro Subscription Engine - Session 124.1
Handles Razorpay subscription flow, free-tier gating, and Pro status checks.
"""
import os
import json
import hmac
import hashlib
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from database import db

logger = logging.getLogger("charvakit.subscription")

# Razorpay config
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

# Pricing
PRO_MONTHLY_PRICE_PAISE = 19900  # ₹199
FREE_TIER_KIT_LIMIT = 3  # 3 application kits per month for free users


def _init_razorpay():
    """Lazy-init Razorpay client."""
    import razorpay
    return razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


class SubscriptionEngine:
    def get_pro_status(self, student_id: str) -> Dict:
        """Check if student currently has active Pro subscription."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT subscription_id, plan, status, started_at, expires_at, auto_renew
                FROM charvak_pro_subscriptions
                WHERE student_id = %s AND status = 'active'
                  AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY created_at DESC
                LIMIT 1
            """, (student_id,))
            row = cur.fetchone()
            if row:
                return {
                    "is_pro": True,
                    "subscription_id": row[0],
                    "plan": row[1],
                    "started_at": row[3],
                    "expires_at": row[4],
                    "auto_renew": row[5],
                }
            return {"is_pro": False}
        finally:
            cur.close()
            conn.close()

    def get_current_period(self) -> tuple:
        """Get current monthly period (1st of month → 1st of next month)."""
        now = datetime.now(timezone.utc)
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            period_end = period_start.replace(year=now.year + 1, month=1)
        else:
            period_end = period_start.replace(month=now.month + 1)
        return period_start, period_end

    def check_kit_limit(self, student_id: str) -> Dict:
        """Check if student can generate an application kit."""
        # Pro users: unlimited
        pro = self.get_pro_status(student_id)
        if pro["is_pro"]:
            return {
                "allowed": True,
                "reason": "pro",
                "used": None,
                "limit": None,
            }

        # Free users: check usage this month
        period_start, period_end = self.get_current_period()
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT count FROM charvak_pro_usage
                WHERE student_id = %s AND feature = 'application_kit'
                  AND period_start = %s
            """, (student_id, period_start))
            row = cur.fetchone()
            used = row[0] if row else 0

            return {
                "allowed": used < FREE_TIER_KIT_LIMIT,
                "reason": "free",
                "used": used,
                "limit": FREE_TIER_KIT_LIMIT,
                "remaining": max(0, FREE_TIER_KIT_LIMIT - used),
            }
        finally:
            cur.close()
            conn.close()

    def increment_kit_usage(self, student_id: str) -> bool:
        """Increment kit usage for the current month."""
        period_start, period_end = self.get_current_period()
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            usage_id = f"USG-{secrets.token_hex(6).upper()}"
            cur.execute("""
                INSERT INTO charvak_pro_usage (usage_id, student_id, feature, count, period_start, period_end)
                VALUES (%s, %s, 'application_kit', 1, %s, %s)
                ON CONFLICT (student_id, feature, period_start)
                DO UPDATE SET count = charvak_pro_usage.count + 1
            """, (usage_id, student_id, period_start, period_end))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to increment usage: {e}")
            return False
        finally:
            cur.close()
            conn.close()

    def create_pro_order(self, student_id: str, email: str = "") -> Dict:
        """Create a Razorpay order for the ₹199 monthly Pro plan."""
        try:
            client = _init_razorpay()
            order = client.order.create({
                "amount": PRO_MONTHLY_PRICE_PAISE,
                "currency": "INR",
                "receipt": f"pro_{student_id[:12]}_{int(datetime.now().timestamp())}",
                "notes": {
                    "student_id": student_id,
                    "plan": "pro_monthly",
                    "email": email,
                },
            })
            logger.info(f"Created Pro order {order['id']} for student {student_id}")
            return {
                "status": "success",
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"],
                "key_id": RAZORPAY_KEY_ID,  # For frontend
            }
        except Exception as e:
            logger.error(f"Failed to create Pro order: {e}")
            return {"status": "error", "message": str(e)}

    def verify_payment(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> Dict:
        """Verify Razorpay payment signature."""
        try:
            body = f"{razorpay_order_id}|{razorpay_payment_id}"
            expected_signature = hmac.new(
                RAZORPAY_KEY_SECRET.encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(expected_signature, razorpay_signature):
                return {"status": "error", "message": "Invalid signature"}

            return {"status": "success", "verified": True}
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return {"status": "error", "message": str(e)}

    def activate_pro(self, student_id: str, razorpay_order_id: str, razorpay_payment_id: str, email: str = "", amount_paise: int = PRO_MONTHLY_PRICE_PAISE) -> Dict:
        """Activate Pro subscription after successful payment."""
        subscription_id = f"SUB-{secrets.token_hex(6).upper()}"
        invoice_id = f"INV-{secrets.token_hex(6).upper()}"
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=30)

        conn = db.get_connection()
        cur = conn.cursor()
        try:
            # Create subscription
            cur.execute("""
                INSERT INTO charvak_pro_subscriptions 
                (subscription_id, student_id, plan, status, razorpay_payment_id, 
                 amount_paid_paise, currency, started_at, expires_at, auto_renew)
                VALUES (%s, %s, 'pro_monthly', 'active', %s, %s, 'INR', %s, %s, TRUE)
            """, (subscription_id, student_id, razorpay_payment_id, amount_paise, now, expires_at))

            # Create invoice
            cur.execute("""
                INSERT INTO charvak_pro_invoices
                (invoice_id, student_id, subscription_id, razorpay_payment_id, razorpay_order_id,
                 amount_paise, currency, status, description, email)
                VALUES (%s, %s, %s, %s, %s, %s, 'INR', 'paid', 'Charvak Pro Monthly Subscription', %s)
            """, (invoice_id, student_id, subscription_id, razorpay_payment_id, razorpay_order_id, amount_paise, email))

            conn.commit()
            logger.info(f"Activated Pro for {student_id} until {expires_at}")
            return {
                "status": "success",
                "subscription_id": subscription_id,
                "expires_at": expires_at.isoformat(),
            }
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to activate Pro: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def cancel_pro(self, student_id: str) -> Dict:
        """Cancel Pro subscription (auto-renew off, stays active till expiry)."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE charvak_pro_subscriptions
                SET auto_renew = FALSE, cancelled_at = NOW()
                WHERE student_id = %s AND status = 'active'
            """, (student_id,))
            conn.commit()
            return {"status": "success", "message": "Pro will end at current period expiry"}
        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def get_invoices(self, student_id: str) -> list:
        """Return invoice history for a student."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT invoice_id, amount_paise, currency, status, description, invoice_date, razorpay_payment_id
                FROM charvak_pro_invoices
                WHERE student_id = %s
                ORDER BY invoice_date DESC
            """, (student_id,))
            return [
                {
                    "invoice_id": r[0],
                    "amount_paise": r[1],
                    "currency": r[2],
                    "status": r[3],
                    "description": r[4],
                    "invoice_date": r[5],
                    "razorpay_payment_id": r[6],
                }
                for r in cur.fetchall()
            ]
        finally:
            cur.close()
            conn.close()


subscription_engine = SubscriptionEngine()