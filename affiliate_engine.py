"""
Charvak Affiliate Engine — Session 95.

Handles affiliate applications, tier approval, and contracts.
Option C: Bronze auto-approves, Silver+ requires manual review.
"""
import os
import secrets
import hashlib
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv


# Tier commission rates
AFFILIATE_TIERS = {
    "bronze": {"first_year": 0.20, "recurring": 0.15, "threshold_inr": 0},
    "silver": {"first_year": 0.25, "recurring": 0.18, "threshold_inr": 830000},   # ~$10K in INR
    "gold":   {"first_year": 0.28, "recurring": 0.20, "threshold_inr": 4150000},  # ~$50K
    "platinum": {"first_year": 0.30, "recurring": 0.22, "threshold_inr": 8300000},# ~$100K
}

# Tier application thresholds (what an affiliate claims they can do)
TIER_REQUIREMENTS = {
    "bronze": {"min_expected_referrals": 0, "min_expected_deal_inr": 0, "requires_tax_id": False},
    "silver": {"min_expected_referrals": 3, "min_expected_deal_inr": 830000, "requires_tax_id": True},
    "gold": {"min_expected_referrals": 10, "min_expected_deal_inr": 4150000, "requires_tax_id": True},
    "platinum": {"min_expected_referrals": 25, "min_expected_deal_inr": 8300000, "requires_tax_id": True},
}

# Valid affiliate types
AFFILIATE_TYPES = ["individual", "agency", "consultant", "recruiter", "coach", "other"]


class AffiliateEngine:
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

    def _hash_ip(self, ip: str) -> str:
        if not ip:
            return ""
        salt = os.getenv("REFERRAL_IP_SALT", "charvak-ref-salt-2026")
        return hashlib.sha256(f"{salt}:{ip}".encode()).hexdigest()[:32]

    # ---------- Apply ----------
    def apply(self, email: str, name: str, company_name: str = None,
              website: str = None, country: str = "IN", affiliate_type: str = "individual",
              expected_monthly_referrals: int = 0, expected_deal_size_inr: int = 0,
              why_interested: str = "", tax_id_type: str = "none",
              tax_id: str = "", tier_requested: str = "bronze",
              ip: str = None) -> dict:
        """
        Submit an affiliate application.
        Bronze auto-approves. Silver+ requires manual review.
        """
        email = (email or "").strip().lower()
        if not email:
            return {"status": "error", "message": "email required"}
        if not name:
            return {"status": "error", "message": "name required"}
        
        tier_requested = (tier_requested or "bronze").lower()
        if tier_requested not in AFFILIATE_TIERS:
            return {"status": "error", "message": f"invalid tier: {tier_requested}"}
        
        # Validate tier requirements
        req = TIER_REQUIREMENTS[tier_requested]
        if expected_monthly_referrals < req["min_expected_referrals"]:
            return {"status": "error", "message": f"{tier_requested} requires {req['min_expected_referrals']}+ referrals/month"}
        if expected_deal_size_inr < req["min_expected_deal_inr"] and req["min_expected_deal_inr"] > 0:
            return {"status": "error", "message": f"{tier_requested} requires deal size >= Rs {req['min_expected_deal_inr']//100:,}"}
        if req["requires_tax_id"] and not tax_id:
            return {"status": "error", "message": f"{tier_requested} requires tax ID (PAN/GST/W-9)"}
        
        try:
            conn = self._conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Check for existing application
            cur.execute("""
                SELECT application_id, status FROM charvak_affiliate_applications
                WHERE LOWER(applicant_email) = %s
                ORDER BY created_at DESC LIMIT 1
            """, (email,))
            existing = cur.fetchone()
            if existing:
                cur.close(); conn.close()
                return {"status": "error", "message": f"Application already exists ({existing['status']}). Contact hr@charvakit.com.", "existing_application_id": existing["application_id"]}
            
            # Create or get referrer account
            referrer_id = self._create_or_get_referrer(email, name, country, cur)
            
            # Determine auto-approval
            auto_approve = (tier_requested == "bronze")
            status = "auto_approved" if auto_approve else "pending"
            
            # Create application
            application_id = "AFF-" + secrets.token_hex(6).upper()
            cur.execute("""
                INSERT INTO charvak_affiliate_applications
                (application_id, referrer_id, applicant_email, applicant_name,
                 company_name, website, country, affiliate_type,
                 expected_monthly_referrals, expected_deal_size_inr, why_interested,
                 tax_id_type, tax_id, status, tier_requested, tier_granted,
                 reviewed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s)
                RETURNING application_id, status, tier_requested, tier_granted
            """, (
                application_id, referrer_id, email, name,
                company_name, website, country, affiliate_type,
                expected_monthly_referrals, expected_deal_size_inr, why_interested,
                tax_id_type, tax_id, status, tier_requested,
                tier_requested if auto_approve else None,
                datetime.utcnow() if auto_approve else None,
            ))
            
            result = dict(cur.fetchone())
            
            # If auto-approved, upgrade referrer account + create contract
            if auto_approve:
                self._promote_to_affiliate(referrer_id, tier_requested, cur)
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                "status": "success",
                "application": result,
                "auto_approved": auto_approve,
                "next_step": (
                    "You're approved! Check your email for dashboard access."
                    if auto_approve
                    else "Your application is under review. We respond within 2 business days."
                ),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _create_or_get_referrer(self, email: str, name: str, country: str, cur) -> str:
        """Get or create referrer account, return referrer_id."""
        cur.execute("SELECT referrer_id FROM charvak_referrer_accounts WHERE LOWER(email) = %s", (email,))
        row = cur.fetchone()
        if row:
            return row["referrer_id"]
        
        referrer_id = "REF-" + secrets.token_hex(6).upper()
        referral_code = "AFF-" + secrets.token_hex(4).upper()
        cur.execute("""
            INSERT INTO charvak_referrer_accounts
            (referrer_id, email, name, referral_code, program_type, country,
             is_affiliate)
            VALUES (%s, %s, %s, %s, 'affiliate', %s, TRUE)
        """, (referrer_id, email, name, referral_code, country))
        return referrer_id

    def _promote_to_affiliate(self, referrer_id: str, tier: str, cur):
        """Upgrade referrer to affiliate + create contract."""
        cur.execute("""
            UPDATE charvak_referrer_accounts
            SET is_affiliate = TRUE,
                affiliate_tier = %s,
                affiliate_approved_at = NOW(),
                program_type = 'affiliate',
                updated_at = NOW()
            WHERE referrer_id = %s
        """, (tier, referrer_id))
        
        # Create contract
        contract_id = "CON-" + secrets.token_hex(6).upper()
        rates = AFFILIATE_TIERS[tier]
        cur.execute("""
            INSERT INTO charvak_affiliate_contracts
            (contract_id, referrer_id, tier, commission_first_year,
             commission_recurring, effective_until, status)
            VALUES (%s, %s, %s, %s, %s, NOW() + INTERVAL '365 days', 'active')
        """, (contract_id, referrer_id, tier, rates["first_year"], rates["recurring"]))

    # ---------- Admin approval ----------
    def list_applications(self, status_filter: str = None, limit: int = 100) -> dict:
        """Admin: list all applications."""
        try:
            conn = self._conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            query = """
                SELECT application_id, applicant_email, applicant_name, company_name,
                       country, affiliate_type, tier_requested, tier_granted,
                       status, expected_monthly_referrals, expected_deal_size_inr,
                       created_at, reviewed_at
                FROM charvak_affiliate_applications
            """
            if status_filter:
                query += " WHERE status = %s"
                query += " ORDER BY created_at DESC LIMIT %s"
                cur.execute(query, (status_filter, limit))
            else:
                query += " ORDER BY created_at DESC LIMIT %s"
                cur.execute(query, (limit,))
            rows = []
            for r in cur.fetchall():
                d = dict(r)
                for k, v in d.items():
                    if hasattr(v, "isoformat"):
                        d[k] = v.isoformat()
                    elif not isinstance(v, (int, float, str, bool, type(None))):
                        d[k] = float(v) if hasattr(v, "__float__") else str(v)
                rows.append(d)
            cur.close()
            conn.close()
            return {"status": "success", "applications": rows, "total": len(rows)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_application(self, application_id: str) -> dict:
        """Admin: get single application."""
        try:
            conn = self._conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT a.*, r.referral_code, r.total_referrals, r.total_revenue_referred_inr
                FROM charvak_affiliate_applications a
                LEFT JOIN charvak_referrer_accounts r ON r.referrer_id = a.referrer_id
                WHERE a.application_id = %s
            """, (application_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                return {"status": "error", "message": "not found"}
            d = dict(row)
            for k, v in d.items():
                if hasattr(v, "isoformat"):
                    d[k] = v.isoformat()
                elif not isinstance(v, (int, float, str, bool, type(None))):
                    d[k] = float(v) if hasattr(v, "__float__") else str(v)
            return {"status": "success", "application": d}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def approve(self, application_id: str, admin_email: str, tier_granted: str = None) -> dict:
        """Admin: approve a pending application."""
        try:
            conn = self._conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cur.execute("""
                SELECT application_id, referrer_id, tier_requested, status
                FROM charvak_affiliate_applications
                WHERE application_id = %s
            """, (application_id,))
            app = cur.fetchone()
            if not app:
                cur.close(); conn.close()
                return {"status": "error", "message": "application not found"}
            if app["status"] not in ("pending", "auto_approved"):
                cur.close(); conn.close()
                return {"status": "error", "message": f"cannot approve in status: {app['status']}"}
            
            tier = (tier_granted or app["tier_requested"]).lower()
            if tier not in AFFILIATE_TIERS:
                cur.close(); conn.close()
                return {"status": "error", "message": f"invalid tier: {tier}"}
            
            cur.execute("""
                UPDATE charvak_affiliate_applications
                SET status = 'approved',
                    tier_granted = %s,
                    reviewed_by = %s,
                    reviewed_at = NOW(),
                    updated_at = NOW()
                WHERE application_id = %s
            """, (tier, admin_email, application_id))
            
            self._promote_to_affiliate(app["referrer_id"], tier, cur)
            
            conn.commit()
            cur.close()
            conn.close()
            return {"status": "success", "application_id": application_id, "tier": tier}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def reject(self, application_id: str, reason: str, admin_email: str = None) -> dict:
        """Admin: reject a pending application."""
        if not reason:
            return {"status": "error", "message": "reason required"}
        try:
            conn = self._conn()
            cur = conn.cursor()
            cur.execute("""
                UPDATE charvak_affiliate_applications
                SET status = 'rejected',
                    rejection_reason = %s,
                    reviewed_by = %s,
                    reviewed_at = NOW(),
                    updated_at = NOW()
                WHERE application_id = %s
                  AND status IN ('pending', 'auto_approved')
                RETURNING application_id
            """, (reason, admin_email, application_id))
            row = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            if not row:
                return {"status": "error", "message": "not found or already processed"}
            return {"status": "success", "application_id": application_id, "reason": reason}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------- Affiliate-facing ----------
    def get_my_status(self, email: str) -> dict:
        """Get current user's affiliate status."""
        email = (email or "").strip().lower()
        try:
            conn = self._conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Application
            cur.execute("""
                SELECT application_id, status, tier_requested, tier_granted,
                       created_at, reviewed_at
                FROM charvak_affiliate_applications
                WHERE LOWER(applicant_email) = %s
                ORDER BY created_at DESC LIMIT 1
            """, (email,))
            app = cur.fetchone()
            
            # Referrer account
            cur.execute("""
                SELECT referrer_id, referral_code, is_affiliate, affiliate_tier,
                       total_referrals, total_revenue_referred_inr,
                       total_commissions_earned_inr, total_commissions_paid_inr
                FROM charvak_referrer_accounts
                WHERE LOWER(email) = %s
            """, (email,))
            acc = cur.fetchone()
            
            cur.close()
            conn.close()
            
            def _serialize(d):
                if not d:
                    return None
                out = dict(d)
                for k, v in out.items():
                    if hasattr(v, "isoformat"):
                        out[k] = v.isoformat()
                    elif not isinstance(v, (int, float, str, bool, type(None))):
                        out[k] = float(v) if hasattr(v, "__float__") else str(v)
                return out
            
            return {
                "status": "success",
                "application": _serialize(app),
                "account": _serialize(acc),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


affiliate_engine = AffiliateEngine()