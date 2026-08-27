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
PAYMENT_MODE = os.getenv("PAYMENT_MODE", "test")


class PaymentEngine:
    """Handles all payment processing for Charvak platform."""

    def __init__(self):
        self.razorpay_key_id = RAZORPAY_KEY_ID
        self.razorpay_key_secret = RAZORPAY_KEY_SECRET
        self.paypal_client_id = PAYPAL_CLIENT_ID
        self.paypal_client_secret = PAYPAL_CLIENT_SECRET
        self.upi_id = UPI_ID
        self.mode = PAYMENT_MODE
        self.payments = []

        if self.mode == "live":
            logger.info("Payment Engine: LIVE mode")
        else:
            logger.warning("Payment Engine: TEST mode")

    def is_ready(self) -> Dict:
        """Check which payment methods are configured."""
        return {
            "razorpay": bool(self.razorpay_key_id and self.razorpay_key_secret),
            "paypal": bool(self.paypal_client_id and self.paypal_client_secret),
            "upi": bool(self.upi_id),
            "mode": self.mode,
            "paypal_client_id": self.paypal_client_id,
            "razorpay_key_id": self.razorpay_key_id
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
                "key_id": self.razorpay_key_id
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
    # ADD KEY TO LIVE MODE RESPONSE
    data["key_id"] = self.razorpay_key_id
    data["key"] = self.razorpay_key_id
    return {"status": "success", **data}
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

    def create_paypal_order(self, amount_usd: float, description: str) -> Dict:
        """Create a PayPal order."""
        if not self.paypal_client_id:
            return {"status": "error", "message": "PayPal not configured"}

        order_id = f"PAYPAL_{secrets.token_hex(8)}"
        self._save_payment({
            "order_id": order_id,
            "amount": amount_usd,
            "currency": "USD",
            "method": "paypal",
            "description": description,
            "status": "created",
            "created_at": datetime.now().isoformat()
        })

        return {
            "status": "success",
            "order_id": order_id,
            "client_id": self.paypal_client_id,
            "amount": amount_usd
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
        self.payments.append(data)
        logger.info(f"Payment recorded: {data.get('order_id')}")

    def _update_payment(self, order_id: str, status: str, txn_id: str = None):
        for payment in self.payments:
            if payment.get("order_id") == order_id:
                payment["status"] = status
                if txn_id:
                    payment["txn_id"] = txn_id
                payment["updated_at"] = datetime.now().isoformat()
                return

    def get_payment_status(self, order_id: str) -> Dict:
        for payment in self.payments:
            if payment.get("order_id") == order_id:
                return payment
        return {"status": "not_found"}

    def get_all_payments(self) -> Dict:
        return {
            "payments": self.payments,
            "count": len(self.payments),
            "total_revenue": sum(p.get("amount", 0) for p in self.payments if p.get("status") == "completed")
        }


payment_engine = PaymentEngine()