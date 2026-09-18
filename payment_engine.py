"""
Charvak Payment Engine
Handles Razorpay, PayPal, and UPI payment processing
"""
import os
import json
import hashlib
import hmac
import logging
from datetime import datetime
from typing import Dict, Optional
import secrets

logger = logging.getLogger("charvakit.payments")

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
UPI_ID = os.getenv("UPI_ID", "charvakit@upi")
PAYMENT_MODE = os.getenv("PAYMENT_MODE", "live")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")


class PaymentEngine:
    """Handles all payment processing for Charvak platform."""

    def __init__(self):
        self.razorpay_key_id = RAZORPAY_KEY_ID
        self.razorpay_key_secret = RAZORPAY_KEY_SECRET
        self.paypal_client_id = PAYPAL_CLIENT_ID
        self.paypal_client_secret = PAYPAL_CLIENT_SECRET
        self.upi_id = UPI_ID
        self.mode = PAYMENT_MODE
        self._ensure_tables()

        if self.mode == "live":
            logger.info("Payment Engine: LIVE mode")
        else:
            logger.warning("Payment Engine: TEST mode")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_payment_log (
                    order_id     TEXT PRIMARY KEY,
                    status       TEXT,
                    amount       NUMERIC(12,2) DEFAULT 0,
                    raw_data     JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_payment_log_status  ON charvak_payment_log(status)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_payment_log_created ON charvak_payment_log(created_at)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"payment_log tables init failed: {e}")

    def is_ready(self) -> Dict:
        """Check which payment methods are configured. Booleans only."""
        return {
            "razorpay": bool(self.razorpay_key_id and self.razorpay_key_secret),
            "paypal": bool(self.paypal_client_id and self.paypal_client_secret),
            "upi": bool(self.upi_id),
        }

    def create_razorpay_order(self, amount_inr: int, receipt: str, notes: Dict = None) -> Dict:
        """Create a Razorpay order."""
        if not self.razorpay_key_id:
            return {"status": "error", "message": "Razorpay not configured"}

        if self.mode == "test":
            order_id = f"order_test_{secrets.token_hex(8)}"
            self._save_payment({
                "order_id": order_id,
                "amount": amount_inr,
                "currency": "INR",
                "receipt": receipt,
                "method": "razorpay",
                "status": "created",
                "notes": notes or {},
                "created_at": datetime.now().isoformat()
            })
            return {
                "status": "success",
                "order_id": order_id,
                "amount": amount_inr,
                "currency": "INR",
                "key_id": self.razorpay_key_id,
                "key": self.razorpay_key_id
            }

        try:
            import requests
            response = requests.post(
                "https://api.razorpay.com/v1/orders",
                auth=(self.razorpay_key_id, self.razorpay_key_secret),
                json={"amount": amount_inr, "currency": "INR", "receipt": receipt, "notes": notes or {}}
            )
            data = response.json()
            self._save_payment({
                "order_id": data.get("id"),
                "amount": amount_inr,
                "currency": "INR",
                "method": "razorpay",
                "status": "created",
                "notes": notes or {}
            })
            data["key_id"] = self.razorpay_key_id
            data["key"] = self.razorpay_key_id
            return {**data, "status": "success", "order_id": data.get("id")}
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {e}")
            return {"status": "error", "message": str(e)}

    def verify_razorpay_payment(self, payment_id: str, order_id: str, signature: str) -> Dict:
        """Verify Razorpay payment signature."""
        if self.mode == "test":
            self._update_payment(order_id, "completed", payment_id)
            return {"status": "success", "verified": True}

        message = f"{order_id}|{payment_id}"
        expected_signature = hmac.new(
            self.razorpay_key_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(expected_signature, signature):
            self._update_payment(order_id, "completed", payment_id)
            return {"status": "success", "verified": True}

        return {"status": "error", "verified": False, "message": "Signature mismatch"}


    def fetch_razorpay_payment(self, payment_id: str) -> Dict:
        """Fetch a Razorpay payment's details from their API.

        Used for server-side verification: confirms the payment was actually
        captured by Razorpay and returns its amount, status, and email so the
        caller can match them against the plan being purchased.
        """
        if not self.razorpay_key_id or not self.razorpay_key_secret:
            return {"status": "error", "message": "Razorpay not configured"}

        if not payment_id or not payment_id.startswith("pay_"):
            return {"status": "error", "message": "Invalid payment_id format"}

        try:
            import requests
            response = requests.get(
                f"https://api.razorpay.com/v1/payments/{payment_id}",
                auth=(self.razorpay_key_id, self.razorpay_key_secret),
                timeout=10
            )

            if response.status_code == 404:
                return {"status": "error", "message": "Payment not found in Razorpay"}

            if response.status_code != 200:
                logger.error(f"Razorpay fetch failed: {response.status_code} {response.text[:200]}")
                return {"status": "error", "message": f"Razorpay API error: {response.status_code}"}

            data = response.json()
            return {
                "status": "success",
                "payment_id": data.get("id"),
                "order_id": data.get("order_id"),
                "amount": data.get("amount"),          # in paise
                "currency": data.get("currency"),
                "status_field": data.get("status"),    # 'captured', 'authorized', 'failed', etc.
                "email": data.get("email"),
                "contact": data.get("contact"),
                "method": data.get("method"),
                "captured": data.get("captured"),
                "raw": data
            }
        except Exception as e:
            logger.error(f"Razorpay fetch exception: {e}")
            return {"status": "error", "message": str(e)}

    # INR ? target currency conversion rates (approx ? update periodically)
    INR_RATES = {
        "USD": 0.012, "EUR": 0.011, "GBP": 0.0095,
        "AUD": 0.018, "CAD": 0.016, "JPY": 1.80,
        "SGD": 0.016, "HKD": 0.094, "NZD": 0.020,
        "CHF": 0.011, "SEK": 0.13, "NOK": 0.13,
        "DKK": 0.083, "PLN": 0.048, "MXN": 0.21,
        "BRL": 0.065,
        "AED": 0.044,
    }

    def verify_webhook_signature(self, raw_body: bytes, signature: str) -> bool:
        """Verify a Razorpay webhook signature.

        Razorpay signs the raw request body with the webhook secret using
        HMAC-SHA256 and sends the hex digest in the X-Razorpay-Signature header.
        """
        if not RAZORPAY_WEBHOOK_SECRET:
            logger.error("RAZORPAY_WEBHOOK_SECRET not configured")
            return False
        if not signature:
            return False
        try:
            expected = hmac.new(
                RAZORPAY_WEBHOOK_SECRET.encode(),
                raw_body,
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected, signature)
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False

    def create_paypal_order(self, amount_inr: float, target_currency: str = "USD", description: str = "", custom_id: str = None) -> Dict:
        """Create a PayPal order.

        custom_id is echoed back by PayPal on capture. Use it to carry
        structured metadata (e.g. 'ai_course|email|course|enrollment|country').
        """
        """Create a PayPal order."""
        if not self.paypal_client_id:
            return {"status": "error", "message": "PayPal not configured"}

        target = (target_currency or "USD").upper()
        rate = self.INR_RATES.get(target, self.INR_RATES["USD"])
        amount_converted = round(amount_inr * rate, 2)

        order_id = f"PAYPAL_{secrets.token_hex(8)}"
        self._save_payment({
            "order_id": order_id,
            "amount": amount_converted,
            "currency": target,
            "method": "paypal",
            "description": description,
            "custom_id": custom_id,
            "status": "created",
            "created_at": datetime.now().isoformat()
        })

        return {
            "status": "success",
            "order_id": order_id,
            "client_id": self.paypal_client_id,
            "amount": amount_converted,
            "currency": target,
            "custom_id": custom_id,
            "description": description
        }

    def verify_paypal_payment(self, order_id: str, paypal_order_id: str) -> Dict:
        """Verify PayPal payment."""
        if self.mode == "test":
            self._update_payment(order_id, "completed", paypal_order_id)
            return {"status": "success", "verified": True}

        try:
            import requests
            auth_response = requests.post(
                "https://api-m.paypal.com/v1/oauth2/token",
                auth=(self.paypal_client_id, self.paypal_client_secret),
                data={"grant_type": "client_credentials"}
            )
            token = auth_response.json().get("access_token")

            verify_response = requests.get(
                f"https://api-m.paypal.com/v2/checkout/orders/{paypal_order_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            data = verify_response.json()

            if data.get("status") == "COMPLETED":
                self._update_payment(order_id, "completed", paypal_order_id)
                return {"status": "success", "verified": True}

            return {"status": "error", "verified": False}
        except Exception as e:
            logger.error(f"PayPal verification failed: {e}")
            return {"status": "error", "message": str(e)}

    def verify_upi_payment(self, txn_id: str, amount: float, notes: str = "") -> Dict:
        """Record UPI payment."""
        order_id = f"UPI_{secrets.token_hex(6)}"
        self._save_payment({
            "order_id": order_id,
            "amount": amount,
            "currency": "INR",
            "method": "upi",
            "status": "completed",
            "txn_id": txn_id,
            "notes": notes,
            "created_at": datetime.now().isoformat()
        })
        return {"status": "success", "message": "UPI payment recorded", "order_id": order_id, "txn_id": txn_id}

    def _save_payment(self, data: Dict):
        """Persist a payment record to the log. Idempotent per order_id."""
        order_id = data.get("order_id")
        if not order_id:
            logger.warning("_save_payment called without order_id - skipping")
            return
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_payment_log (order_id, status, amount, raw_data)
                VALUES (%s, %s, %s, %s::jsonb)
                ON CONFLICT (order_id) DO NOTHING
            ''', (
                order_id,
                data.get("status"),
                float(data.get("amount") or 0),
                json.dumps(data, default=str),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"_save_payment failed: {e}")
            return
        logger.info(f"Payment recorded: {order_id}")

    def _update_payment(self, order_id: str, status: str, txn_id: str = None):
        """Merge status/txn_id into the stored raw_data dict."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            # Fetch, patch in Python, write back - preserves dict.update() semantics
            cur.execute('SELECT raw_data FROM charvak_payment_log WHERE order_id = %s', (order_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return
            raw = row[0] if isinstance(row[0], dict) else json.loads(row[0] or "{}")
            raw["status"] = status
            if txn_id:
                raw["txn_id"] = txn_id
            raw["updated_at"] = datetime.now().isoformat()
            cur.execute('''
                UPDATE charvak_payment_log
                SET status = %s, raw_data = %s::jsonb, updated_at = CURRENT_TIMESTAMP
                WHERE order_id = %s
            ''', (status, json.dumps(raw, default=str), order_id))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"_update_payment failed: {e}")

    def get_payment_status(self, order_id: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT raw_data FROM charvak_payment_log WHERE order_id = %s', (order_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_payment_status failed: {e}")
            return {"status": "not_found"}

        if not row:
            return {"status": "not_found"}
        return row[0] if isinstance(row[0], dict) else json.loads(row[0] or "{}")

    def get_all_payments(self) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT raw_data FROM charvak_payment_log ORDER BY created_at ASC')
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_all_payments failed: {e}")
            return {"payments": [], "count": 0, "total_revenue": 0}

        payments = [r[0] if isinstance(r[0], dict) else json.loads(r[0] or "{}") for r in rows]

        # total_revenue preserves the original formula: sum of amount where status == 'completed'
        total_revenue = sum(p.get("amount", 0) for p in payments if p.get("status") == "completed")

        return {
            "payments": payments,
            "count": len(payments),
            "total_revenue": total_revenue,
        }


payment_engine = PaymentEngine()