"""
Charvak <-> DoketsRB Integration Engine
Deep links, cross-promotion, bundle pricing
(DB-backed - Session J/1)
"""
import json
import logging
import secrets
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


doketsrb_integration = DoketsRBIntegration()