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
from dotenv import load_dotenv

# Dev override: .env.local wins if present, then .env fills gaps
load_dotenv(".env.local", override=True)
load_dotenv()

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
        """Check which payment methods are configured."""
        razorpay_ok = bool(self.razorpay_key_id and self.razorpay_key_secret)
        paypal_ok = bool(self.paypal_client_id and self.paypal_client_secret)
        return {
            "razorpay": razorpay_ok,
            "paypal": paypal_ok,
            "upi": bool(self.upi_id),
            # Public-safe fields the frontend needs for lazy SDK loading.
            # The client_id is the public half of the pair (safe to expose);
            # the secret is never returned.
            "razorpay_key_id": self.razorpay_key_id if razorpay_ok else None,
            "paypal_client_id": self.paypal_client_id if paypal_ok else None,
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

    def verify_paypal_webhook_signature(self, headers: dict, raw_body: bytes) -> bool:
        """Verify a PayPal webhook transmission via PayPal's verify API.

        PayPal signs each webhook delivery with a rotating certificate. Instead
        of maintaining a local CA bundle, we forward the transmission headers +
        body back to PayPal's /v1/notifications/verify-webhook-signature
        endpoint. PayPal returns SUCCESS or FAILURE.

        Required env: PAYPAL_WEBHOOK_ID (from PayPal dashboard).
        Required headers (case-insensitive):
            paypal-transmission-id
            paypal-transmission-time
            paypal-cert-url
            paypal-auth-algo
            paypal-transmission-sig
        """
        import os as _os, json as _json, requests as _requests

        webhook_id = _os.getenv("PAYPAL_WEBHOOK_ID", "")
        if not webhook_id:
            logger.error("PAYPAL_WEBHOOK_ID not configured - refusing unverified PayPal webhook")
            return False
        if not self.paypal_client_id or not self.paypal_client_secret:
            logger.error("PayPal credentials missing - cannot verify webhook")
            return False

        h = {k.lower(): v for k, v in (headers or {}).items()}
        required = [
            "paypal-transmission-id",
            "paypal-transmission-time",
            "paypal-cert-url",
            "paypal-auth-algo",
            "paypal-transmission-sig",
        ]
        missing = [r for r in required if not h.get(r)]
        if missing:
            logger.warning(f"PayPal webhook verify: missing headers {missing}")
            return False

        try:
            # 1. OAuth token
            auth = _requests.post(
                "https://api-m.paypal.com/v1/oauth2/token",
                auth=(self.paypal_client_id, self.paypal_client_secret),
                data={"grant_type": "client_credentials"},
                timeout=10,
            )
            token = (auth.json() or {}).get("access_token")
            if not token:
                logger.error(f"PayPal webhook verify: auth failed {auth.status_code}")
                return False

            # 2. Parse raw body so we can send it as webhook_event
            try:
                event_obj = _json.loads(raw_body.decode("utf-8"))
            except Exception as e:
                logger.warning(f"PayPal webhook verify: body not valid JSON - {e}")
                return False

            verify_body = {
                "auth_algo":         h["paypal-auth-algo"],
                "cert_url":          h["paypal-cert-url"],
                "transmission_id":   h["paypal-transmission-id"],
                "transmission_sig":  h["paypal-transmission-sig"],
                "transmission_time": h["paypal-transmission-time"],
                "webhook_id":        webhook_id,
                "webhook_event":     event_obj,
            }
            resp = _requests.post(
                "https://api-m.paypal.com/v1/notifications/verify-webhook-signature",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type":  "application/json",
                },
                json=verify_body,
                timeout=10,
            )
            data = resp.json() or {}
            status = data.get("verification_status", "")
            if status == "SUCCESS":
                return True
            logger.warning(f"PayPal webhook verify: {status} - {str(data)[:300]}")
            return False
        except Exception as e:
            logger.exception(f"PayPal webhook verify: exception {e}")
            return False

    def create_paypal_order(self, amount_inr: float, target_currency: str = "USD", description: str = "", custom_id: str = None) -> Dict:
        """Create a PayPal order.

        Calls PayPal's /v2/checkout/orders endpoint to create a REAL order
        and returns the PayPal-issued order ID (PAY-xxxx). The ID is stored
        locally so fetch_paypal_order can verify it later.

        custom_id is echoed back by PayPal on capture. Use it to carry
        structured metadata (e.g. 'ai_course|email|course|enrollment|country').
        """
        if not self.paypal_client_id or not self.paypal_client_secret:
            return {"status": "error", "message": "PayPal not configured"}

        target = (target_currency or "USD").upper()
        rate = self.INR_RATES.get(target, self.INR_RATES["USD"])
        amount_converted = round(amount_inr * rate, 2)

        try:
            import requests
            base = "https://api-m.paypal.com"

            # 1. Get OAuth token
            auth_resp = requests.post(
                f"{base}/v1/oauth2/token",
                auth=(self.paypal_client_id, self.paypal_client_secret),
                data={"grant_type": "client_credentials"},
                timeout=10
            )
            token = (auth_resp.json() or {}).get("access_token")
            if not token:
                logger.error(f"PayPal order create: auth failed {auth_resp.status_code} {auth_resp.text[:200]}")
                return {"status": "error", "message": "PayPal authentication failed"}

            # 2. Create the order
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": target,
                        "value": f"{amount_converted:.2f}"
                    },
                    "description": (description or "Charvak credits")[:127]
                }]
            }
            if custom_id:
                payload["purchase_units"][0]["custom_id"] = custom_id[:127]

            r = requests.post(
                f"{base}/v2/checkout/orders",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=15
            )
            if r.status_code not in (200, 201):
                logger.error(f"PayPal order create failed: {r.status_code} {r.text[:300]}")
                return {"status": "error", "message": f"PayPal order creation failed: {r.status_code}"}

            data = r.json()
            paypal_order_id = data.get("id")   # e.g. "PAY-xxxx"

            if not paypal_order_id:
                logger.error(f"PayPal order create: no id in response: {data}")
                return {"status": "error", "message": "PayPal returned no order id"}

            # 3. Store locally so fetch_paypal_order / verify can find it
            self._save_payment({
                "order_id": paypal_order_id,
                "paypal_order_id": paypal_order_id,
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
                "order_id": paypal_order_id,       # real PAY-xxx; frontend hands this to the SDK
                "client_id": self.paypal_client_id,
                "amount": amount_converted,
                "currency": target,
                "custom_id": custom_id,
                "description": description
            }

        except Exception as e:
            logger.error(f"PayPal order create exception: {e}")
            return {"status": "error", "message": str(e)}

    def verify_paypal_payment(self, order_id: str, paypal_order_id: str) -> Dict:
        """Verify PayPal payment."""
        if self.mode == "test":
            # Do NOT auto-verify in test mode. Previously this returned
            # {"verified": True} for any input, which was a footgun: a dev
            # environment with PAYMENT_MODE=test would grant credits for any
            # fabricated PayPal order ID. Hardened 2026-09-28.
            logger.warning("verify_paypal_payment called in test mode — refusing auto-verify")
            return {"status": "error", "verified": False,
                    "message": "PayPal verification refused in test mode; use sandbox credentials with PAYMENT_MODE=live"}

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

    def fetch_paypal_order(self, paypal_order_id: str) -> Dict:
        """Fetch a PayPal order's details from their API.

        Mirrors fetch_razorpay_payment: confirms the order was actually
        captured by PayPal and returns its amount, currency, status, and
        payer email so the caller can match against the plan being purchased.
        """
        if not self.paypal_client_id or not self.paypal_client_secret:
            return {"status": "error", "message": "PayPal not configured"}

        # PayPal's API returns order IDs like "4W597217DK354982T" (17-char
        # alphanumeric, no PAY- prefix). The PAY- prefix seen in the UI is a
        # legacy display convention, not what the API returns. Just require a
        # non-empty string here; the PayPal API call below is the real validator.
        if not paypal_order_id or len(paypal_order_id) < 8:
            return {"status": "error", "message": "Invalid PayPal order_id format"}

        try:
            import requests
            # Sandbox vs live determined by the client_id prefix PayPal issues
            # (sandbox ids start with a specific pattern); simplest: try live,
            # fall back to sandbox on 401.
            base = "https://api-m.paypal.com"
            auth_resp = requests.post(
                f"{base}/v1/oauth2/token",
                auth=(self.paypal_client_id, self.paypal_client_secret),
                data={"grant_type": "client_credentials"},
                timeout=10
            )
            token = (auth_resp.json() or {}).get("access_token")
            if not token:
                return {"status": "error", "message": "PayPal auth failed"}

            r = requests.get(
                f"{base}/v2/checkout/orders/{paypal_order_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            if r.status_code == 404:
                return {"status": "error", "message": "PayPal order not found"}
            if r.status_code != 200:
                logger.error(f"PayPal fetch failed: {r.status_code} {r.text[:200]}")
                return {"status": "error", "message": f"PayPal API error: {r.status_code}"}

            data = r.json()
            pu = (data.get("purchase_units") or [{}])[0]
            amount_obj = pu.get("amount") or {}
            payer = data.get("payer") or {}
            return {
                "status": "success",
                "paypal_order_id": data.get("id"),
                "status_field": data.get("status"),           # 'COMPLETED', 'APPROVED', etc.
                "captured": data.get("status") == "COMPLETED",
                "amount": float(amount_obj.get("value") or 0),
                "currency": amount_obj.get("currency_code"),
                "email": payer.get("email_address"),
                "raw": data,
            }
        except Exception as e:
            logger.error(f"PayPal fetch exception: {e}")
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