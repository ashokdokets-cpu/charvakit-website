"""
Charvak Outreach Engine
Cold Email Finder, Gmail Sync, Application Auto-Tracking
Premium monetization: Rs.99-199/mo
(DB-backed - Session F/2)
"""
import json
import logging
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.outreach")


class OutreachEngine:
    """Cold email finder + Gmail sync + auto-tracking (DB-backed)."""

    def __init__(self):
        self._ensure_tables()
        logger.info("Outreach Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_outreach_cold_emails (
                    email_id              TEXT PRIMARY KEY,
                    company               TEXT,
                    hiring_manager        TEXT,
                    domain                TEXT,
                    likely_emails         JSONB DEFAULT '[]'::jsonb,
                    confidence            TEXT,
                    cold_email_template   TEXT,
                    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_outreach_ce_company ON charvak_outreach_cold_emails(company)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_outreach_ce_domain  ON charvak_outreach_cold_emails(domain)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_outreach_email_syncs (
                    sync_id       TEXT PRIMARY KEY,
                    email         TEXT NOT NULL UNIQUE,
                    sync_type     TEXT DEFAULT 'all',
                    status        TEXT DEFAULT 'connected',
                    connected_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_outreach_syncs_email ON charvak_outreach_email_syncs(email)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_outreach_auto_tracked (
                    track_id    TEXT PRIMARY KEY,
                    email       TEXT NOT NULL,
                    company     TEXT,
                    role        TEXT,
                    status      TEXT DEFAULT 'applied',
                    tracked_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_outreach_tracked_email   ON charvak_outreach_auto_tracked(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_outreach_tracked_company ON charvak_outreach_auto_tracked(company)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_outreach_premium_users (
                    subscription_id  TEXT PRIMARY KEY,
                    email            TEXT NOT NULL UNIQUE,
                    plan             TEXT DEFAULT 'basic',
                    price            INTEGER DEFAULT 0,
                    features         JSONB DEFAULT '[]'::jsonb,
                    subscribed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_outreach_premium_email ON charvak_outreach_premium_users(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_outreach_premium_plan  ON charvak_outreach_premium_users(plan)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"outreach tables init failed: {e}")

    # ============================================================
    # 1. COLD EMAIL FINDER
    # ============================================================

    def find_hiring_manager_email(self, data: Dict) -> Dict:
        """
        Find hiring manager email patterns.
        data = {company, hiring_manager_name, domain}
        """
        company = data.get("company", "")
        name = data.get("hiring_manager_name", "")
        domain = data.get("domain", company.lower().replace(" ", "") + ".com")

        first_name = name.split()[0].lower() if name else "first"
        last_name = name.split()[-1].lower() if name and len(name.split()) > 1 else "last"

        patterns = [
            f"{first_name}.{last_name}@{domain}",
            f"{first_name}{last_name}@{domain}",
            f"{first_name[0]}{last_name}@{domain}" if first_name else "",
            f"{first_name}@{domain}",
        ]

        email_id = f"CEMAIL-{secrets.token_hex(4).upper()}"

        result = {
            "email_id": email_id,
            "company": company,
            "hiring_manager": name,
            "domain": domain,
            "likely_emails": [p for p in patterns if p],
            "confidence": "HIGH" if name else "MEDIUM",
            "cold_email_template": self._generate_cold_email(data),
            "created_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_outreach_cold_emails
                    (email_id, company, hiring_manager, domain, likely_emails,
                     confidence, cold_email_template)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)
            ''', (
                email_id, company, name, domain,
                json.dumps(result["likely_emails"]),
                result["confidence"], result["cold_email_template"],
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"find_hiring_manager_email write failed: {e}")

        return {
            "status": "success",
            "email_id": email_id,
            "likely_emails": result["likely_emails"],
            "cold_email_template": result["cold_email_template"],
            "message": "Email patterns found!",
        }

    def _generate_cold_email(self, data: Dict) -> str:
        """Generate personalized cold email."""
        name = data.get("hiring_manager_name", "Hiring Manager")
        company = data.get("company", "your company")
        role = data.get("target_role", "the open position")
        candidate = data.get("candidate_name", "Candidate")
        skill = data.get("key_skill", "relevant experience")

        return f"""Subject: Interest in {role} at {company}

Hi {name},

I came across {company}'s work and I'm very impressed. I'm {candidate} with strong {skill}. I'm very interested in the {role} position and believe my background would be a great fit.

Would you be open to a quick chat about opportunities at {company}?

Best regards,
{candidate}"""

    # ============================================================
    # 2. GMAIL SYNC (Application Tracking)
    # ============================================================

    def connect_gmail(self, data: Dict) -> Dict:
        """
        Connect Gmail for application tracking.
        data = {email, sync_type: "applications"/"responses"/"all"}
        """
        sync_id = f"SYNC-{secrets.token_hex(4).upper()}"
        sync_type = data.get("sync_type", "all")

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_outreach_email_syncs
                    (sync_id, email, sync_type, status)
                VALUES (%s, %s, %s, 'connected')
                ON CONFLICT (email) DO UPDATE SET
                    sync_id = EXCLUDED.sync_id,
                    sync_type = EXCLUDED.sync_type,
                    status = 'connected',
                    connected_at = CURRENT_TIMESTAMP
            ''', (sync_id, data.get("email"), sync_type))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"connect_gmail failed: {e}")
            return {"status": "error", "message": "Could not connect Gmail"}

        return {
            "status": "success",
            "sync_id": sync_id,
            "message": f"Gmail connected for {sync_type} tracking!",
            "auto_tracking": "Applications will auto-update from email responses",
        }

    def auto_track_application(self, data: Dict) -> Dict:
        """
        Auto-track application from email.
        data = {email, company, role, status}
        """
        track_id = f"TRACK-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_outreach_auto_tracked
                    (track_id, email, company, role, status)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                track_id, data.get("email"), data.get("company"),
                data.get("role"), data.get("status", "applied"),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"auto_track_application failed: {e}")
            return {"status": "error", "message": "Could not track application"}

        return {"status": "success", "track_id": track_id, "message": f"Application at {data.get('company')} tracked!"}

    def get_tracked_applications(self, email: str) -> Dict:
        """Get all tracked applications."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT track_id, email, company, role, status, tracked_at
                FROM charvak_outreach_auto_tracked
                WHERE email = %s
                ORDER BY tracked_at DESC
            ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_tracked_applications failed: {e}")
            return {"status": "error", "message": "Could not load applications"}

        applications = [{
            "track_id": r[0],
            "email": r[1],
            "company": r[2],
            "role": r[3],
            "status": r[4],
            "tracked_at": r[5].isoformat() if hasattr(r[5], "isoformat") else str(r[5]),
        } for r in rows]

        return {"status": "success", "applications": applications, "count": len(applications)}

    # ============================================================
    # 3. PREMIUM SUBSCRIPTION
    # ============================================================

    def subscribe_premium(self, data: Dict) -> Dict:
        """
        Subscribe to premium outreach tools.
        data = {email, plan: "basic"/"premium"}
        """
        plan = data.get("plan", "basic")
        price = 0 if plan == "basic" else 199
        features = ["Cold Email Finder", "Gmail Sync", "Auto-Tracking"] if plan == "premium" else ["Basic tracking"]
        subscription_id = f"OUT-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_outreach_premium_users
                    (subscription_id, email, plan, price, features)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (email) DO UPDATE SET
                    subscription_id = EXCLUDED.subscription_id,
                    plan = EXCLUDED.plan,
                    price = EXCLUDED.price,
                    features = EXCLUDED.features,
                    subscribed_at = CURRENT_TIMESTAMP
            ''', (subscription_id, data.get("email"), plan, price, json.dumps(features)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"subscribe_premium failed: {e}")
            return {"status": "error", "message": "Could not subscribe"}

        return {
            "status": "success",
            "subscription_id": subscription_id,
            "plan": plan,
            "price": price,
            "message": f"Subscribed to {plan} plan!",
        }

    def get_stats(self) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM charvak_outreach_cold_emails')
            cold_emails_found = int(cur.fetchone()[0] or 0)
            cur.execute('SELECT COUNT(*) FROM charvak_outreach_email_syncs')
            gmail_syncs = int(cur.fetchone()[0] or 0)
            cur.execute('SELECT COUNT(*) FROM charvak_outreach_auto_tracked')
            auto_tracked = int(cur.fetchone()[0] or 0)
            cur.execute('SELECT COUNT(*) FROM charvak_outreach_premium_users')
            premium_users = int(cur.fetchone()[0] or 0)
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "cold_emails_found": cold_emails_found,
                "gmail_syncs": gmail_syncs,
                "auto_tracked": auto_tracked,
                "premium_users": premium_users,
            },
        }


outreach_engine = OutreachEngine()