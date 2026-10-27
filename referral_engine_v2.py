"""
Charvak Referral Engine — attribution, commission, anti-fraud.
Session 92 — Infrastructure.
"""
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, List

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv


# Commission rates by tier
TIER_RATES = {
    "starter": {"student": 0.0, "cert_paid": 1.0, "institution_deal": 0.10, "employer_sub": 0.15, "affiliate_deal": 0.20},
    "pro":     {"student": 0.0, "cert_paid": 1.0, "institution_deal": 0.12, "employer_sub": 0.18, "affiliate_deal": 0.22},
    "partner": {"student": 0.0, "cert_paid": 1.0, "institution_deal": 0.15, "employer_sub": 0.22, "affiliate_deal": 0.25},
    "elite":   {"student": 0.0, "cert_paid": 1.0, "institution_deal": 0.20, "employer_sub": 0.25, "affiliate_deal": 0.30},
}

# Credit rewards (student referral — B2C)
STUDENT_CREDITS = {
    "signup": 50,          # both referrer and referred get 50
    "cert_paid": 100,      # referrer gets +100 when referral pays for cert
    "depth_2": 25,         # referrer gets +25 when referral refers someone
    "milestone_5": 200,    # bonus at 5 referrals
    "milestone_10": 500,   # bonus at 10 referrals
}

# Fraud thresholds
FRAUD_THRESHOLDS = {
    "max_referrals_per_day": 20,
    "max_referrals_per_hour": 5,
    "min_account_age_hours_for_payout": 24,
    "hold_days_before_payout": 30,
    "self_referral_ip_window_hours": 24,
    "max_same_ip_per_referrer": 3,
}

# Tier upgrade thresholds (12-month rolling)
TIER_THRESHOLDS = {
    "starter": {"min_referrals": 0, "min_revenue_inr": 0},
    "pro": {"min_referrals": 3, "min_revenue_inr": 0},
    "partner": {"min_referrals": 10, "min_revenue_inr": 1000000},  # 10K USD ~= 10L INR
    "elite": {"min_referrals": 20, "min_revenue_inr": 5000000},     # 50K USD ~= 50L INR
}


class ReferralEngine:
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

    # ---------- Ref code generation ----------
    def _generate_code(self, prefix="REF"):
        """Generate a unique 8-char referral code."""
        return f"{prefix}-{secrets.token_hex(4).upper()}"

    def _hash_ip(self, ip: str) -> str:
        """Hash an IP for privacy-preserving dedup."""
        if not ip:
            return ""
        salt = os.getenv("REFERRAL_IP_SALT", "charvak-ref-salt-2026")
        return hashlib.sha256(f"{salt}:{ip}".encode()).hexdigest()[:32]

    # ---------- Account creation ----------
    def create_or_get_referrer(self, email: str, name: str = None, phone: str = None,
                                program_type: str = "student", country: str = "IN") -> Dict:
        """Create a referrer account or return existing."""
        email = (email or "").strip().lower()
        if not email:
            return {"status": "error", "message": "email required"}
        
        try:
            conn = self._conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Check existing
            cur.execute("""
                SELECT referrer_id, email, name, referral_code, tier, program_type,
                       total_referrals, total_revenue_referred_inr, total_commissions_earned_inr,
                       total_commissions_paid_inr, status
                FROM charvak_referrer_accounts
                WHERE LOWER(email) = %s
            """, (email,))
            existing = cur.fetchone()
            
            if existing:
                cur.close()
                conn.close()
                return {"status": "success", "referrer": dict(existing), "created": False}
            
            # Create new
            referrer_id = "REF-" + secrets.token_hex(6).upper()
            referral_code = self._generate_code("CHV")
            
            cur.execute("""
                INSERT INTO charvak_referrer_accounts
                (referrer_id, email, name, phone, referral_code, program_type, country)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING referrer_id, email, name, referral_code, tier, program_type
            """, (referrer_id, email, name, phone, referral_code, program_type, country))
            
            result = dict(cur.fetchone())
            conn.commit()
            cur.close()
            conn.close()
            
            return {"status": "success", "referrer": result, "created": True}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------- Attribution ----------
    def record_click(self, referral_code: str, ip: str, user_agent: str,
                      landing_page: str, country: str = None) -> Dict:
        """Record a click on a referral link."""
        referral_code = (referral_code or "").strip().upper()
        if not referral_code:
            return {"status": "error", "message": "no code"}
        
        try:
            conn = self._conn()
            cur = conn.cursor()
            
            # Verify code exists
            cur.execute("SELECT referrer_id FROM charvak_referrer_accounts WHERE referral_code = %s", (referral_code,))
            if not cur.fetchone():
                cur.close()
                conn.close()
                return {"status": "error", "message": "invalid code"}
            
            # Record click
            cur.execute("""
                INSERT INTO charvak_referral_clicks_v2
                (click_id, referral_code, ip_hash, user_agent, landing_page, country)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ("CLK-" + secrets.token_hex(6).upper(), referral_code,
                  self._hash_ip(ip), (user_agent or "")[:200], (landing_page or "")[:200], country))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def resolve_referral(self, referral_code: str) -> Optional[Dict]:
        """Get referrer info by code."""
        try:
            conn = self._conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT referrer_id, email, name, referral_code, tier, program_type, status
                FROM charvak_referrer_accounts
                WHERE referral_code = %s AND status = 'active'
            """, ((referral_code or "").strip().upper(),))
            row = cur.fetchone()
            cur.close()
            conn.close()
            return dict(row) if row else None
        except Exception:
            return None

    # ---------- Fraud detection ----------
    def is_self_referral(self, referrer_email: str, referred_email: str,
                          referrer_ip: str = None, referred_ip: str = None) -> bool:
        """Detect self-referral via email or IP match."""
        if (referrer_email or "").lower() == (referred_email or "").lower():
            return True
        
        if referrer_ip and referred_ip:
            if self._hash_ip(referrer_ip) == self._hash_ip(referred_ip):
                return True
        
        return False

    def check_volume_anomaly(self, referrer_id: str) -> Dict:
        """Check if referrer is generating suspicious volume."""
        try:
            conn = self._conn()
            cur = conn.cursor()
            
            # Last 24h
            cur.execute("""
                SELECT COUNT(*) FROM charvak_referral_conversions
                WHERE referrer_id = %s
                  AND created_at > NOW() - INTERVAL '24 hours'
            """, (referrer_id,))
            count_24h = cur.fetchone()[0]
            
            # Last 1h
            cur.execute("""
                SELECT COUNT(*) FROM charvak_referral_conversions
                WHERE referrer_id = %s
                  AND created_at > NOW() - INTERVAL '1 hour'
            """, (referrer_id,))
            count_1h = cur.fetchone()[0]
            
            cur.close()
            conn.close()
            
            if count_24h > FRAUD_THRESHOLDS["max_referrals_per_day"]:
                return {"anomaly": True, "reason": f"{count_24h} referrals in 24h (max {FRAUD_THRESHOLDS['max_referrals_per_day']})"}
            if count_1h > FRAUD_THRESHOLDS["max_referrals_per_hour"]:
                return {"anomaly": True, "reason": f"{count_1h} referrals in 1h (max {FRAUD_THRESHOLDS['max_referrals_per_hour']})"}
            
            return {"anomaly": False}
        except Exception as e:
            return {"anomaly": False, "warning": str(e)}

    # ---------- Conversion recording ----------
    def record_conversion(self, referral_code: str, referred_email: str,
                           conversion_type: str, conversion_value_inr: int = 0,
                           referred_ip: str = None, metadata: Dict = None) -> Dict:
        """
        Record a conversion and compute commission.
        
        conversion_type:
          - signup: student signs up (0 INR, credits only)
          - cert_paid: student pays for cert (500 INR default, credits only)
          - institution_deal: institution signs (revenue in INR)
          - employer_sub: employer subscribes (revenue in INR)
          - affiliate_deal: affiliate deal closes (revenue in INR)
        """
        referral_code = (referral_code or "").strip().upper()
        referred_email = (referred_email or "").strip().lower()
        
        if not referral_code or not referred_email:
            return {"status": "error", "message": "code and email required"}
        
        try:
            conn = self._conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Get referrer
            cur.execute("""
                SELECT referrer_id, email, tier, status
                FROM charvak_referrer_accounts
                WHERE referral_code = %s
            """, (referral_code,))
            referrer = cur.fetchone()
            
            if not referrer:
                cur.close()
                conn.close()
                return {"status": "error", "message": "invalid referral code"}
            
            if referrer["status"] != "active":
                cur.close()
                conn.close()
                return {"status": "error", "message": "referrer not active"}
            
            # Fraud check: self-referral
            if self.is_self_referral(referrer["email"], referred_email,
                                       referred_ip=referred_ip):
                cur.execute("""
                    INSERT INTO charvak_referral_conversions
                    (conversion_id, referrer_id, referred_email, referred_ip_hash,
                     conversion_type, conversion_value_inr, commission_rate,
                     commission_amount_inr, status, fraud_reason)
                    VALUES (%s, %s, %s, %s, %s, %s, 0, 0, 'fraud_blocked', 'self_referral')
                """, ("CNV-" + secrets.token_hex(8).upper(), referrer["referrer_id"],
                      referred_email, self._hash_ip(referred_ip or ""), conversion_type,
                      conversion_value_inr))
                conn.commit()
                cur.close()
                conn.close()
                return {"status": "blocked", "reason": "self_referral_detected"}
            
            # Fraud check: volume anomaly
            anomaly = self.check_volume_anomaly(referrer["referrer_id"])
            if anomaly.get("anomaly"):
                cur.execute("""
                    INSERT INTO charvak_referral_conversions
                    (conversion_id, referrer_id, referred_email, referred_ip_hash,
                     conversion_type, conversion_value_inr, commission_rate,
                     commission_amount_inr, status, fraud_reason)
                    VALUES (%s, %s, %s, %s, %s, %s, 0, 0, 'fraud_blocked', %s)
                """, ("CNV-" + secrets.token_hex(8).upper(), referrer["referrer_id"],
                      referred_email, self._hash_ip(referred_ip or ""), conversion_type,
                      conversion_value_inr, anomaly["reason"]))
                conn.commit()
                cur.close()
                conn.close()
                return {"status": "blocked", "reason": "volume_anomaly", "detail": anomaly["reason"]}
            
            # Compute commission
            tier = referrer["tier"] or "starter"
            rate = TIER_RATES.get(tier, TIER_RATES["starter"]).get(conversion_type, 0.0)
            
            # Student conversions = credits (not INR commission)
            if conversion_type in ("signup", "cert_paid"):
                # Credits rewarded outside this engine — log 0 INR commission
                commission_inr = 0
            else:
                commission_inr = int(conversion_value_inr * rate)
            
            # 30-day hold for fraud protection
            hold_until = datetime.utcnow() + timedelta(days=FRAUD_THRESHOLDS["hold_days_before_payout"])
            
            cur.execute("""
                INSERT INTO charvak_referral_conversions
                (conversion_id, referrer_id, referred_email, referred_ip_hash,
                 conversion_type, conversion_value_inr, commission_rate,
                 commission_amount_inr, status, hold_until, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s, %s)
                RETURNING conversion_id, commission_amount_inr
            """, ("CNV-" + secrets.token_hex(8).upper(), referrer["referrer_id"],
                  referred_email, self._hash_ip(referred_ip or ""), conversion_type,
                  conversion_value_inr, rate, commission_inr, hold_until,
                  psycopg2.extras.Json(metadata or {})))
            
            result = dict(cur.fetchone())
            
            # Update referrer stats
            cur.execute("""
                UPDATE charvak_referrer_accounts
                SET total_referrals = total_referrals + 1,
                    total_revenue_referred_inr = total_revenue_referred_inr + %s,
                    total_commissions_earned_inr = total_commissions_earned_inr + %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE referrer_id = %s
            """, (conversion_value_inr, commission_inr, referrer["referrer_id"]))
            
            conn.commit()
            
            # Check for tier upgrade
            self._check_tier_upgrade(referrer["referrer_id"], cur, conn)
            
            cur.close()
            conn.close()
            
            return {"status": "success", "conversion": result,
                    "commission_inr": commission_inr,
                    "credits_eligible": conversion_type in ("signup", "cert_paid")}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _check_tier_upgrade(self, referrer_id: str, cur, conn):
        """Check if referrer qualifies for tier upgrade."""
        cur.execute("""
            SELECT total_referrals, total_revenue_referred_inr, tier
            FROM charvak_referrer_accounts
            WHERE referrer_id = %s
        """, (referrer_id,))
        row = cur.fetchone()
        if not row:
            return
        
        current_tier = row["tier"] or "starter"
        referrals = row["total_referrals"] or 0
        revenue = row["total_revenue_referred_inr"] or 0
        
        new_tier = current_tier
        for tier in ["elite", "partner", "pro", "starter"]:
            th = TIER_THRESHOLDS[tier]
            if referrals >= th["min_referrals"] and revenue >= th["min_revenue_inr"]:
                new_tier = tier
                break
        
        if new_tier != current_tier:
            cur.execute("""
                UPDATE charvak_referrer_accounts
                SET tier = %s, updated_at = CURRENT_TIMESTAMP
                WHERE referrer_id = %s
            """, (new_tier, referrer_id))

    # ---------- Stats ----------
    def get_referrer_stats(self, referrer_id: str) -> Dict:
        """Get dashboard stats for a referrer."""
        try:
            conn = self._conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Account info
            cur.execute("""
                SELECT referrer_id, email, name, referral_code, tier, program_type,
                       total_referrals, total_revenue_referred_inr,
                       total_commissions_earned_inr, total_commissions_paid_inr
                FROM charvak_referrer_accounts
                WHERE referrer_id = %s
            """, (referrer_id,))
            account = cur.fetchone()
            if not account:
                cur.close()
                conn.close()
                return {"status": "error", "message": "not found"}
            
            # Conversions by status
            cur.execute("""
                SELECT status, COUNT(*) as cnt, SUM(commission_amount_inr) as total
                FROM charvak_referral_conversions
                WHERE referrer_id = %s
                GROUP BY status
            """, (referrer_id,))
            conversions = {r["status"]: {"count": r["cnt"], "total_inr": r["total"] or 0}
                            for r in cur.fetchall()}
            
            # Recent conversions
            cur.execute("""
                SELECT conversion_id, referred_email, conversion_type,
                       conversion_value_inr, commission_amount_inr,
                       status, created_at, hold_until
                FROM charvak_referral_conversions
                WHERE referrer_id = %s
                ORDER BY created_at DESC
                LIMIT 20
            """, (referrer_id,))
            recent = [dict(r) for r in cur.fetchall()]
            
            # Click count
            cur.execute("""
                SELECT COUNT(*) FROM charvak_referral_clicks_v2
                WHERE referral_code = %s
            """, (account["referral_code"],))
            clicks = cur.fetchone()["count"]
            
            cur.close()
            conn.close()
            
            return {
                "status": "success",
                "account": dict(account),
                "clicks": clicks,
                "conversions_by_status": conversions,
                "recent_conversions": recent,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


referral_engine = ReferralEngine()