"""
Charvak Referral & Affiliate Engine
Handles referral tracking, bounty rewards, and affiliate commissions.
Database-backed: charvak_referrals, charvak_referral_clicks, charvak_referral_bounties.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.referral")

REFERRAL_MODE = os.getenv("REFERRAL_MODE", "test")
DEFAULT_BOUNTY_INR = 500
DEFAULT_AFFILIATE_COMMISSION = 10  # percent


class ReferralStatus:
    PENDING = "pending"
    CLICKED = "clicked"
    SIGNED_UP = "signed_up"
    CONVERTED = "converted"
    PAID = "paid"
    EXPIRED = "expired"


class ReferralEngine:
    """Database-backed referral and affiliate tracking."""

    def __init__(self):
        self.mode = REFERRAL_MODE
        self._ensure_tables()
        logger.info(f"Referral Engine ready (DB-backed): {'LIVE' if self.mode == 'live' else 'TEST'} mode")

    def _ensure_tables(self):
        """Idempotent table creation."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_referrals (
                    referral_code TEXT PRIMARY KEY,
                    referral_link TEXT NOT NULL,
                    referrer_name TEXT,
                    referrer_email TEXT NOT NULL,
                    user_type TEXT DEFAULT 'candidate',
                    clicks INTEGER DEFAULT 0,
                    signups INTEGER DEFAULT 0,
                    conversions INTEGER DEFAULT 0,
                    total_earned INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_referral_clicks (
                    id SERIAL PRIMARY KEY,
                    referral_code TEXT NOT NULL,
                    source TEXT DEFAULT 'direct',
                    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_referral_bounties (
                    bounty_id TEXT PRIMARY KEY,
                    referral_code TEXT NOT NULL,
                    referrer_email TEXT NOT NULL,
                    new_user_email TEXT,
                    amount_inr INTEGER DEFAULT 500,
                    status TEXT DEFAULT 'signed_up',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Referral tables init failed: {e}")

    def _row_to_referral(self, row) -> Dict:
        if not row:
            return None
        return {
            "referral_code": row[0],
            "referral_link": row[1],
            "referrer_name": row[2],
            "referrer_email": row[3],
            "user_type": row[4],
            "clicks": row[5] or 0,
            "signups": row[6] or 0,
            "conversions": row[7] or 0,
            "total_earned": row[8] or 0,
            "created_at": row[9].isoformat() if row[9] else None,
            "expires_at": row[10].isoformat() if row[10] else None,
        }

    def _row_to_bounty(self, row) -> Dict:
        if not row:
            return None
        return {
            "bounty_id": row[0],
            "referral_code": row[1],
            "referrer_email": row[2],
            "new_user_email": row[3],
            "amount_inr": row[4],
            "status": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "paid_at": row[7].isoformat() if row[7] else None,
        }

    # ============================================================
    # REFERRAL LINKS
    # ============================================================

    def create_referral_link(self, user_data: Dict) -> Dict:
        """Generate a unique referral link for a user. Returns existing link if one already exists."""
        email = user_data.get("email")

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Check if a link already exists for this email
            cur.execute("""
                SELECT referral_code, referral_link FROM charvak_referrals
                WHERE referrer_email = %s
                ORDER BY created_at ASC LIMIT 1
            """, (email,))
            existing = cur.fetchone()

            if existing:
                referral_code, referral_link = existing
                cur.close()
                conn.close()
                logger.info(f"Existing referral link returned for {email}: {referral_code}")
            else:
                referral_code = f"REF-{secrets.token_hex(4).upper()}"
                referral_link = f"https://www.charvakit.com/ref/{referral_code}"
                expires = datetime.now() + timedelta(days=365)

                cur.execute("""
                    INSERT INTO charvak_referrals
                        (referral_code, referral_link, referrer_name, referrer_email, user_type, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    referral_code,
                    referral_link,
                    user_data.get("name"),
                    email,
                    user_data.get("user_type", "candidate"),
                    expires
                ))
                conn.commit()
                cur.close()
                conn.close()
                logger.info(f"Referral link created: {referral_code} for {email}")

            return {
                "status": "success",
                "referral_code": referral_code,
                "referral_link": referral_link,
                "share_text": f"Join Charvak IT Consulting and get hired! Use my referral: {referral_link}",
                "share_links": {
                    "whatsapp": f"https://wa.me/?text=Join+Charvak+IT+Consulting!+Use+my+referral:+{referral_link}",
                    "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={referral_link}",
                    "twitter": f"https://twitter.com/intent/tweet?text=Join+Charvak+IT+Consulting!&url={referral_link}",
                    "email": f"mailto:?subject=Join Charvak IT Consulting&body=Use my referral link: {referral_link}"
                }
            }
        except Exception as e:
            logger.error(f"create_referral_link failed: {e}")
            return {"status": "error", "message": str(e)}

    def track_click(self, referral_code: str, source: str = "direct") -> Dict:
        """Track a referral link click."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("SELECT referral_code FROM charvak_referrals WHERE referral_code = %s", (referral_code,))
            if not cur.fetchone():
                cur.close()
                conn.close()
                return {"status": "error", "message": "Invalid referral code"}

            cur.execute("INSERT INTO charvak_referral_clicks (referral_code, source) VALUES (%s, %s)", (referral_code, source))
            cur.execute("UPDATE charvak_referrals SET clicks = clicks + 1 WHERE referral_code = %s", (referral_code,))
            conn.commit()
            cur.close()
            conn.close()

            logger.info(f"Referral click: {referral_code} from {source}")
            return {"status": "success", "message": "Click tracked"}
        except Exception as e:
            logger.error(f"track_click failed: {e}")
            return {"status": "error", "message": str(e)}

    def track_signup(self, referral_code: str, new_user_email: str) -> Dict:
        """Track a signup from a referral."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("SELECT referrer_email FROM charvak_referrals WHERE referral_code = %s", (referral_code,))
            row = cur.fetchone()
            if not row:
                cur.close()
                conn.close()
                return {"status": "error", "message": "Invalid referral code"}

            referrer_email = row[0]
            bounty_id = f"BOUNTY-{secrets.token_hex(4).upper()}"

            cur.execute("""
                INSERT INTO charvak_referral_bounties
                    (bounty_id, referral_code, referrer_email, new_user_email, amount_inr, status)
                VALUES (%s, %s, %s, %s, %s, 'signed_up')
            """, (bounty_id, referral_code, referrer_email, new_user_email, DEFAULT_BOUNTY_INR))

            cur.execute("UPDATE charvak_referrals SET signups = signups + 1 WHERE referral_code = %s", (referral_code,))
            conn.commit()
            cur.close()
            conn.close()

            logger.info(f"Signup from referral: {referral_code} → {new_user_email}")

            return {
                "status": "success",
                "bounty_id": bounty_id,
                "referrer_email": referrer_email,
                "message": f"Signup tracked! Bounty of ₹{DEFAULT_BOUNTY_INR} will be credited upon conversion."
            }
        except Exception as e:
            logger.error(f"track_signup failed: {e}")
            return {"status": "error", "message": str(e)}

    def mark_conversion(self, bounty_id: str) -> Dict:
        """Mark a referral as converted."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                UPDATE charvak_referral_bounties
                SET status = 'converted'
                WHERE bounty_id = %s
                RETURNING referral_code, amount_inr
            """, (bounty_id,))
            row = cur.fetchone()
            if not row:
                cur.close()
                conn.close()
                return {"status": "error", "message": "Bounty not found"}

            referral_code, amount = row
            cur.execute("""
                UPDATE charvak_referrals
                SET conversions = conversions + 1, total_earned = total_earned + %s
                WHERE referral_code = %s
            """, (amount, referral_code))
            conn.commit()
            cur.close()
            conn.close()

            logger.info(f"✅ Referral converted: {bounty_id}")
            return {
                "status": "success",
                "bounty_id": bounty_id,
                "amount": amount,
                "message": f"Referral converted! ₹{amount} bounty earned."
            }
        except Exception as e:
            logger.error(f"mark_conversion failed: {e}")
            return {"status": "error", "message": str(e)}

    def pay_bounty(self, bounty_id: str) -> Dict:
        """Mark a bounty as paid."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE charvak_referral_bounties
                SET status = 'paid', paid_at = CURRENT_TIMESTAMP
                WHERE bounty_id = %s
                RETURNING amount_inr, referrer_email
            """, (bounty_id,))
            row = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            if not row:
                return {"status": "error", "message": "Bounty not found"}

            logger.info(f"💰 Bounty paid: {bounty_id} | ₹{row[0]}")
            return {
                "status": "success",
                "bounty_id": bounty_id,
                "amount_paid": row[0],
                "paid_to": row[1],
                "message": "Bounty paid successfully"
            }
        except Exception as e:
            logger.error(f"pay_bounty failed: {e}")
            return {"status": "error", "message": str(e)}

    # ============================================================
    # AFFILIATE PROGRAM
    # ============================================================

    def register_affiliate(self, affiliate_data: Dict) -> Dict:
        """Register as an affiliate partner — creates a referral code."""
        try:
            referral_code = f"REF-{secrets.token_hex(4).upper()}"
            referral_link = f"https://www.charvakit.com/ref/{referral_code}"
            expires = datetime.now() + timedelta(days=365)

            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_referrals
                    (referral_code, referral_link, referrer_name, referrer_email, user_type, expires_at)
                VALUES (%s, %s, %s, %s, 'partner', %s)
            """, (referral_code, referral_link, affiliate_data.get("name"), affiliate_data.get("email"), expires))
            conn.commit()
            cur.close()
            conn.close()

            affiliate_id = f"AFF-{secrets.token_hex(4).upper()}"
            logger.info(f"Affiliate registered: {affiliate_id}")

            return {
                "status": "success",
                "affiliate_id": affiliate_id,
                "referral_link": referral_link,
                "commission": f"{DEFAULT_AFFILIATE_COMMISSION}%",
                "message": "Affiliate registered successfully!"
            }
        except Exception as e:
            logger.error(f"register_affiliate failed: {e}")
            return {"status": "error", "message": str(e)}

    # ============================================================
    # DASHBOARD
    # ============================================================

    def get_referrer_stats(self, email: str) -> Dict:
        """Get stats for a specific referrer."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT referral_code, referral_link, referrer_name, referrer_email, user_type,
                       clicks, signups, conversions, total_earned, created_at, expires_at
                FROM charvak_referrals WHERE referrer_email = %s
                ORDER BY created_at DESC LIMIT 1
            """, (email,))
            ref = self._row_to_referral(cur.fetchone())
            if not ref:
                cur.close()
                conn.close()
                return {"status": "error", "message": "No referral found for this email"}

            cur.execute("""
                SELECT bounty_id, referral_code, referrer_email, new_user_email, amount_inr, status, created_at, paid_at
                FROM charvak_referral_bounties WHERE referral_code = %s
                ORDER BY created_at DESC LIMIT 100
            """, (ref["referral_code"],))
            bounties = [self._row_to_bounty(r) for r in cur.fetchall()]
            cur.close()
            conn.close()

            return {
                "status": "success",
                "referral": ref,
                "bounties": bounties,
                "pending_bounties": len([b for b in bounties if b["status"] == "signed_up"]),
                "converted_bounties": len([b for b in bounties if b["status"] == "converted"]),
                "paid_bounties": len([b for b in bounties if b["status"] == "paid"])
            }
        except Exception as e:
            logger.error(f"get_referrer_stats failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_stats(self) -> Dict:
        """Get referral system statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM charvak_referrals")
            total_referrers = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_referrals WHERE user_type = 'partner'")
            total_affiliates = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_referral_bounties")
            total_bounties = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_referral_bounties WHERE status = 'signed_up'")
            pending = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_referral_bounties WHERE status = 'converted'")
            converted = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_referral_bounties WHERE status = 'paid'")
            paid = cur.fetchone()[0] or 0
            cur.execute("SELECT COALESCE(SUM(amount_inr), 0) FROM charvak_referral_bounties WHERE status = 'paid'")
            total_payout = cur.fetchone()[0] or 0

            cur.close()
            conn.close()

            return {
                "status": "success",
                "stats": {
                    "total_referrers": total_referrers,
                    "total_affiliates": total_affiliates,
                    "total_bounties": total_bounties,
                    "pending_bounties": pending,
                    "converted_bounties": converted,
                    "paid_bounties": paid,
                    "total_payout_inr": total_payout,
                    "default_bounty": DEFAULT_BOUNTY_INR
                }
            }
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "stats": {}}

    def get_leaderboard(self, limit: int = 10) -> Dict:
        """Get top referrers leaderboard."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT referrer_name, conversions, total_earned
                FROM charvak_referrals
                WHERE conversions > 0
                ORDER BY total_earned DESC
                LIMIT %s
            """, (limit,))
            rows = cur.fetchall()
            cur.close()
            conn.close()

            return {
                "status": "success",
                "leaderboard": [
                    {"rank": i + 1, "name": r[0], "conversions": r[1], "earned": r[2]}
                    for i, r in enumerate(rows)
                ]
            }
        except Exception as e:
            logger.error(f"get_leaderboard failed: {e}")
            return {"status": "success", "leaderboard": []}


# ============================================================
# SINGLETON
# ============================================================
referral_engine = ReferralEngine()