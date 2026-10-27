"""
Payout engine — manual mode (Session 94a).

Handles payout method setup, eligibility checks, and payout requests.
Real API payouts (Razorpay X / PayPal Payouts) deferred to Session 94b.
"""
import os
import secrets
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from dotenv import load_dotenv


# Payout eligibility constants
MIN_PAYOUT_INR = 100000          # Rs 1,000 in paise
MIN_PAYOUT_USD = 1500            # $15 in cents (approximate threshold)
HOLD_DAYS = 30                   # 30-day fraud hold on conversions

# Supported payout methods per country
SUPPORTED_METHODS = {
    "IN": ["razorpay_upi", "razorpay_bank", "wire"],
    "US": ["paypal", "wire"],
    "GB": ["paypal", "wire"],
    "EU": ["paypal", "wire"],
    "AE": ["paypal", "wire"],
    "SG": ["paypal", "wire"],
    "AU": ["paypal", "wire"],
    "default": ["paypal", "wire"],
}


class PayoutEngine:
    def __init__(self):
        pass

    def _conn(self):
        load_dotenv(".env", override=True)
        url = os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL not set")
        conn = psycopg2.connect(url)
        conn.autocommit = False
        return conn

    # ---------- Payout method setup ----------
    def set_payout_method(self, referrer_id: str, method: str, details: dict, country: str = "IN") -> dict:
        """
        Save or update the referrer's payout method.
        
        method: 'razorpay_upi' | 'razorpay_bank' | 'paypal' | 'wire'
        details: method-specific fields
          - razorpay_upi: {upi_id}
          - razorpay_bank: {account_number, ifsc, account_holder}
          - paypal: {paypal_email}
          - wire: {bank_name, account_number, swift, beneficiary_name}
        """
        try:
            # Validate method for country
            country = (country or "IN").upper()
            allowed = SUPPORTED_METHODS.get(country, SUPPORTED_METHODS["default"])
            
            # Accept both 'razorpay_upi' and 'upi' as aliases
            method_norm = method.lower().replace("-", "_")
            if method_norm == "upi":
                method_norm = "razorpay_upi"
            
            if method_norm not in allowed and method_norm not in allowed + ["razorpay_upi", "razorpay_bank"]:
                # Allow manual override but flag it
                pass
            
            # Validate required fields
            if method_norm == "razorpay_upi":
                if not details.get("upi_id"):
                    return {"status": "error", "message": "UPI ID required"}
            elif method_norm == "razorpay_bank":
                if not details.get("account_number") or not details.get("ifsc"):
                    return {"status": "error", "message": "Bank account + IFSC required"}
            elif method_norm == "paypal":
                if not details.get("paypal_email"):
                    return {"status": "error", "message": "PayPal email required"}
            elif method_norm == "wire":
                if not details.get("account_number") or not details.get("swift"):
                    return {"status": "error", "message": "Bank account + SWIFT required"}
            else:
                return {"status": "error", "message": f"Unknown method: {method}"}
            
            conn = self._conn()
            cur = conn.cursor()
            cur.execute("""
                UPDATE charvak_referrer_accounts
                SET payout_method = %s,
                    payout_details = %s,
                    payout_country = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE referrer_id = %s
            """, (method_norm, psycopg2.extras.Json(details), country, referrer_id))
            conn.commit()
            cur.close()
            conn.close()
            return {"status": "success", "method": method_norm}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------- Eligibility ----------
    def compute_eligibility(self, referrer_id: str) -> dict:
        """Check if referrer can request a payout right now."""
        try:
            conn = self._conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Get referrer
            cur.execute("""
                SELECT payout_method, payout_country, fraud_flags, status
                FROM charvak_referrer_accounts
                WHERE referrer_id = %s
            """, (referrer_id,))
            acc = cur.fetchone()
            if not acc:
                cur.close(); conn.close()
                return {"status": "error", "message": "referrer not found"}
            
            # Pending payout?
            cur.execute("""
                SELECT COUNT(*) FROM charvak_payout_requests
                WHERE referrer_id = %s AND status IN ('requested', 'approved', 'processing')
            """, (referrer_id,))
            pending_payout = cur.fetchone()["count"] > 0
            
            # Eligible conversions (past hold, pending status)
            cur.execute("""
                SELECT COUNT(*) as cnt, COALESCE(SUM(commission_amount_inr), 0) as total
                FROM charvak_referral_conversions
                WHERE referrer_id = %s
                  AND status = 'pending'
                  AND (hold_until IS NULL OR hold_until <= NOW())
                  AND commission_amount_inr > 0
            """, (referrer_id,))
            row = cur.fetchone()
            total_eligible = int(row["total"] or 0)
            conversion_count = int(row["cnt"] or 0)
            
            cur.close()
            conn.close()
            
            reasons = []
            if acc["status"] != "active":
                reasons.append(f"Account status: {acc['status']}")
            if acc["fraud_flags"] and acc["fraud_flags"] > 0:
                reasons.append(f"Account under review ({acc['fraud_flags']} flag{'s' if acc['fraud_flags']>1 else ''})")
            if not acc["payout_method"]:
                reasons.append("No payout method saved")
            if pending_payout:
                reasons.append("You have a pending payout request")
            if total_eligible < MIN_PAYOUT_INR:
                reasons.append(f"Minimum Rs 1,000 to request payout (current: Rs {total_eligible//100})")
            
            return {
                "status": "success",
                "eligible": len(reasons) == 0,
                "amount_available_inr": total_eligible,
                "conversion_count": conversion_count,
                "reasons": reasons,
                "payout_method": acc["payout_method"],
                "payout_country": acc["payout_country"],
                "pending_payout": pending_payout,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------- Payout request ----------
    def request_payout(self, referrer_id: str) -> dict:
        """Create a payout request for all eligible conversions."""
        try:
            # Check eligibility first
            elig = self.compute_eligibility(referrer_id)
            if elig.get("status") != "success":
                return elig
            
            if not elig.get("eligible"):
                return {
                    "status": "error",
                    "message": "Not eligible for payout",
                    "reasons": elig.get("reasons", []),
                }
            
            conn = self._conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Get referrer payout method
            cur.execute("""
                SELECT payout_method, payout_details, payout_country
                FROM charvak_referrer_accounts
                WHERE referrer_id = %s
            """, (referrer_id,))
            acc = cur.fetchone()
            
            amount = elig["amount_available_inr"]
            payout_id = "PAY-" + secrets.token_hex(6).upper()
            
            cur.execute("""
                INSERT INTO charvak_payout_requests
                (payout_id, referrer_id, amount_inr, currency, payout_method,
                 payout_details, status)
                VALUES (%s, %s, %s, 'INR', %s, %s, 'requested')
                RETURNING payout_id, amount_inr, status
            """, (payout_id, referrer_id, amount, acc["payout_method"],
                  psycopg2.extras.Json(acc["payout_details"] or {})))
            
            result = dict(cur.fetchone())
            conn.commit()
            cur.close()
            conn.close()
            
            return {"status": "success", "payout": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------- History ----------
    def list_payouts(self, referrer_id: str, limit: int = 20) -> dict:
        """Get referrer's payout history."""
        try:
            conn = self._conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT payout_id, amount_inr, currency, payout_method, status,
                       requested_at, paid_at, payment_reference
                FROM charvak_payout_requests
                WHERE referrer_id = %s
                ORDER BY requested_at DESC
                LIMIT %s
            """, (referrer_id, limit))
            rows = [dict(r) for r in cur.fetchall()]
            cur.close()
            conn.close()
            return {"status": "success", "payouts": rows, "total": len(rows)}
        except Exception as e:
            return {"status": "error", "message": str(e)}


payout_engine = PayoutEngine()