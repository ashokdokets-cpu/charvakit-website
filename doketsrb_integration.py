"""
Charvak <-> DoketsRB Integration Engine
Deep links, cross-promotion, bundle pricing
(DB-backed - Session J/1)
"""
import json
import logging
import secrets
import hmac
import hashlib
import os
import base64
import time
from urllib.parse import urlencode
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.doketsrb")


class DoketsRBIntegration:
    """Integration layer between Charvak and DoketsRB (DB-backed)."""

    DOKETSRB_URL = "https://doketsrb.com"

    FEATURES = {
        "resume_builder": {"name": "AI Resume Builder", "url": f"{DOKETSRB_URL}/resume-builder", "free": True},
        "cover_letter": {"name": "Cover Letter Generator", "url": f"{DOKETSRB_URL}/cover-letter", "free": True},
        "linkedin_optimizer": {"name": "LinkedIn Profile Optimizer", "url": f"{DOKETSRB_URL}/linkedin", "free": True},
        "jd_parser": {"name": "JD Parser (ATS Tailor)", "url": f"{DOKETSRB_URL}/jd-parser", "free": True},
        "chrome_extension": {"name": "Chrome Extension", "url": f"{DOKETSRB_URL}/extension", "free": True},
    }

    BUNDLES = {
        "basic": {"name": "Basic", "price": 0, "includes": ["Charvak Free", "DoketsRB Free"]},
        "pro": {"name": "Pro Bundle", "price": 149, "includes": ["Charvak AI Assessment", "DoketsRB Premium"]},
        "enterprise": {"name": "Enterprise", "price": 999, "includes": ["Everything", "White-label", "API access"]},
    }

    def __init__(self):
        self._ensure_tables()
        logger.info("DoketsRB Integration ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_doketsrb_bundle_subs (
                    subscription_id  TEXT PRIMARY KEY,
                    email            TEXT,
                    bundle           TEXT,
                    bundle_name      TEXT,
                    price            NUMERIC(10,2) DEFAULT 0,
                    includes         JSONB DEFAULT '[]'::jsonb,
                    subscribed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_doketsrb_subs_email  ON charvak_doketsrb_bundle_subs(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_doketsrb_subs_bundle ON charvak_doketsrb_bundle_subs(bundle)''')
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_doketsrb_score_tokens (
                    token            TEXT PRIMARY KEY,
                    candidate_id     TEXT NOT NULL,
                    email            TEXT,
                    target_role      TEXT DEFAULT '',
                    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at       TIMESTAMP NOT NULL,
                    used_at          TIMESTAMP,
                    status           TEXT DEFAULT 'pending'
                )
            """)
            cur.execute("""CREATE INDEX IF NOT EXISTS idx_doketsrb_score_tokens_cand ON charvak_doketsrb_score_tokens(candidate_id)""")
            cur.execute("""CREATE INDEX IF NOT EXISTS idx_doketsrb_score_tokens_status ON charvak_doketsrb_score_tokens(status)""")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_doketsrb_score_events (
                    event_id         TEXT PRIMARY KEY,
                    candidate_id     TEXT NOT NULL,
                    score            INTEGER,
                    source           TEXT DEFAULT 'doketsrb',
                    target_role      TEXT DEFAULT '',
                    metadata         JSONB DEFAULT '{}'::jsonb,
                    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""CREATE INDEX IF NOT EXISTS idx_doketsrb_score_events_cand ON charvak_doketsrb_score_events(candidate_id)""")
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"doketsrb tables init failed: {e}")

    # ============================================================
    # STATIC READS
    # ============================================================

    def get_deep_links(self) -> Dict:
        """Get all DoketsRB feature links for cross-promotion."""
        return {
            "status": "success",
            "doketsrb_url": self.DOKETSRB_URL,
            "features": self.FEATURES,
            "message": "DoketsRB features ready for integration",
        }

    def get_promotional_banner(self, context: str = "career") -> Dict:
        """Get promotional banner for Charvak pages."""
        banners = {
            "resume": {
                "title": "Need a resume? Try DoketsRB (Free)",
                "features": ["AI Resume Builder", "Cover Letter Generator", "LinkedIn Optimizer", "JD Parser"],
                "cta": "Build Your Resume ->",
                "url": self.DOKETSRB_URL,
            },
            "career": {
                "title": "Boost Your Career with DoketsRB",
                "features": ["ATS-Friendly Templates", "1-Click Apply", "LinkedIn Chrome Extension"],
                "cta": "Try DoketsRB Free ->",
                "url": self.DOKETSRB_URL,
            },
            "student": {
                "title": "Students: Build Your First Resume",
                "features": ["Free Templates", "AI Suggestions", "Cover Letter Generator"],
                "cta": "Start Free ->",
                "url": self.DOKETSRB_URL,
            },
        }

        banner = banners.get(context, banners["career"])
        return {"status": "success", "banner": banner}

    # ============================================================
    # BUNDLE SUBSCRIPTIONS
    # ============================================================

    def subscribe_bundle(self, data: Dict) -> Dict:
        """
        Subscribe to Charvak + DoketsRB bundle.
        data = {email, bundle: "basic"/"pro"/"enterprise"}
        """
        bundle_key = data.get("bundle", "basic")
        bundle = self.BUNDLES.get(bundle_key, self.BUNDLES["basic"])
        subscription_id = f"BNDL-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_doketsrb_bundle_subs
                    (subscription_id, email, bundle, bundle_name, price, includes)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
            ''', (
                subscription_id,
                data.get("email"),
                bundle_key,
                bundle["name"],
                bundle["price"],
                json.dumps(bundle["includes"]),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"subscribe_bundle failed: {e}")
            return {"status": "error", "message": "Could not subscribe to bundle"}

        return {
            "status": "success",
            "subscription_id": subscription_id,
            "bundle": bundle["name"],
            "price": bundle["price"],
            "message": f"Subscribed to {bundle['name']} bundle!",
        }

    def get_bundles(self) -> Dict:
        """Get all bundle options."""
        return {"status": "success", "bundles": self.BUNDLES}

    # ============================================================
    # STATS
    # ============================================================

    def get_stats(self) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM charvak_doketsrb_bundle_subs')
            total_subs = int(cur.fetchone()[0] or 0)
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "total_bundle_subscriptions": total_subs,
                "features_available": len(self.FEATURES),
            },
        }


    # ============================================================
    # ATS RESUME SCORING BRIDGE (Session ATS-1)
    # ============================================================

    SCORE_TOKEN_TTL_SECONDS = 3600

    def _score_secret(self):
        secret = os.getenv("DOKETSRB_SCORE_SECRET") or os.getenv("SECRET_KEY") or "charvak-dev-secret"
        return secret.encode("utf-8")

    def _sign_token(self, payload):
        sig = hmac.new(self._score_secret(), payload.encode("utf-8"), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=")

    def request_score_link(self, candidate_id, target_role=""):
        token = secrets.token_urlsafe(24)
        expires_at = time.time() + self.SCORE_TOKEN_TTL_SECONDS
        signed = self._sign_token(f"{token}:{candidate_id}")

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_doketsrb_score_tokens
                    (token, candidate_id, target_role, expires_at, status)
                VALUES (%s, %s, %s, to_timestamp(%s) AT TIME ZONE 'UTC', 'pending')
            ''', (token, candidate_id, target_role, expires_at))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"request_score_link insert failed: {e}")
            return {"status": "error", "message": "Could not create score request"}

        return_url = f"https://charvakit.com/api/ats/score-callback?token={token}&sig={signed}"
        params = urlencode({"return_url": return_url, "role": target_role, "source": "charvak"})
        url = f"{self.DOKETSRB_URL}/ats-check?{params}"

        return {
            "status": "success",
            "token": token,
            "url": url,
            "expires_in": self.SCORE_TOKEN_TTL_SECONDS,
            "message": "Open the link to run a free ATS check on DoketsRB",
        }

    def record_external_score(self, candidate_id, score, source="doketsrb", target_role="", metadata=None):
        if score is None or not isinstance(score, (int, float)):
            return {"status": "error", "message": "Invalid score"}
        score_int = int(round(float(score)))
        if score_int < 0 or score_int > 100:
            return {"status": "error", "message": "Score out of range (0-100)"}

        event_id = f"ATSSCORE-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_doketsrb_score_events
                    (event_id, candidate_id, score, source, target_role, metadata)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
            ''', (event_id, candidate_id, score_int, source, target_role,
                  json.dumps(metadata or {})))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"record_external_score event log failed: {e}")

        from candidate_engine import candidate_engine
        result = candidate_engine.update_skill_score(candidate_id, score_int)
        if result.get("status") != "success":
            return {"status": "error", "message": result.get("message", "Could not update candidate")}

        return {
            "status": "success",
            "candidate_id": candidate_id,
            "score": score_int,
            "event_id": event_id,
            "badge_earned": score_int >= 70,
            "message": "ATS score recorded",
        }

    def consume_score_callback(self, token, sig, score, source="doketsrb"):
        if not token or not sig:
            return {"status": "error", "message": "Missing token or signature"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT candidate_id, target_role, expires_at, used_at, status,
                       (expires_at AT TIME ZONE 'UTC') > (now() AT TIME ZONE 'UTC') AS not_expired
                FROM charvak_doketsrb_score_tokens WHERE token = %s
            ''', (token,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"consume_score_callback lookup failed: {e}")
            return {"status": "error", "message": "Could not verify token"}

        if not row:
            return {"status": "error", "message": "Unknown token"}
        candidate_id, target_role, expires_at, used_at, status, not_expired = row

        if used_at or status == "used":
            return {"status": "error", "message": "Token already used"}
        if not not_expired:
            return {"status": "error", "message": "Token expired"}

        expected = self._sign_token(f"{token}:{candidate_id}")
        if not hmac.compare_digest(expected, sig):
            return {"status": "error", "message": "Bad signature"}

        result = self.record_external_score(candidate_id, score, source=source, target_role=target_role)
        if result.get("status") != "success":
            return result

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_doketsrb_score_tokens
                SET used_at = CURRENT_TIMESTAMP, status = 'used'
                WHERE token = %s
            ''', (token,))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"consume_score_callback mark-used failed: {e}")

        return result

    def _call_doketsrb_score(self, resume_text, target_role):
        return {"status": "not_implemented",
                "message": "DoketsRB scoring API not configured; use deep-link flow"}


doketsrb_integration = DoketsRBIntegration()