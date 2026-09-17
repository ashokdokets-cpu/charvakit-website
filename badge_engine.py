"""
Charvak Badge & Certification Engine
Handles verified badges, skill certifications, and shareable credentials
(DB-backed - Session D/1)
"""
import hashlib
import json
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.badges")


class BadgeLevel:
    VERIFIED = "verified"
    PREMIUM = "premium"
    EXPERT = "expert"
    MASTER = "master"


class BadgeEngine:
    """Handles all badges and certifications (DB-backed)."""

    BADGE_TYPES = {
        "skill_twin": {"name": "Skill-Twin Verified", "levels": [BadgeLevel.VERIFIED, BadgeLevel.PREMIUM]},
        "micro_internship": {"name": "Micro-Internship Complete", "levels": [BadgeLevel.VERIFIED]},
        "background_check": {"name": "Background Verified", "levels": [BadgeLevel.VERIFIED, BadgeLevel.PREMIUM]},
        "course_completion": {"name": "Course Certificate", "levels": [BadgeLevel.VERIFIED]},
        "top_performer": {"name": "Top Performer", "levels": [BadgeLevel.EXPERT, BadgeLevel.MASTER]},
    }

    BADGE_COLORS = {
        BadgeLevel.VERIFIED: "#3ba591",
        BadgeLevel.PREMIUM: "#6366f1",
        BadgeLevel.EXPERT: "#f59e0b",
        BadgeLevel.MASTER: "#ef4444",
    }

    def __init__(self):
        self._ensure_tables()
        logger.info("Badge Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_badges (
                    badge_id           TEXT PRIMARY KEY,
                    badge_name         TEXT,
                    level              TEXT,
                    color              TEXT DEFAULT '#3ba591',
                    user_name          TEXT,
                    user_email         TEXT NOT NULL,
                    score              INTEGER,
                    skills             JSONB DEFAULT '[]'::jsonb,
                    badge_type         TEXT,
                    issued_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    valid_until        TIMESTAMP,
                    verification_hash  TEXT,
                    share_url          TEXT,
                    linkedin_url       TEXT
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_badges_user_email ON charvak_badges(user_email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_badges_level      ON charvak_badges(level)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_badges_type       ON charvak_badges(badge_type)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_badges_valid      ON charvak_badges(valid_until)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"badge tables init failed: {e}")

    # ============================================================
    # BADGE ROW <-> DICT
    # ============================================================

    @staticmethod
    def _row_to_badge(row) -> Dict:
        if not row:
            return {}
        (badge_id, badge_name, level, color, user_name, user_email,
         score, skills, badge_type, issued_at, valid_until,
         verification_hash, share_url, linkedin_url) = row

        skills_parsed = skills if isinstance(skills, list) else (json.loads(skills) if skills else [])

        return {
            "badge_id": badge_id,
            "badge_name": badge_name,
            "level": level,
            "color": color,
            "user_name": user_name,
            "user_email": user_email,
            "score": score,
            "skills": skills_parsed,
            "badge_type": badge_type,
            "issued_at": issued_at.isoformat() if hasattr(issued_at, "isoformat") else str(issued_at),
            "valid_until": valid_until.isoformat() if hasattr(valid_until, "isoformat") else str(valid_until),
            "verification_hash": verification_hash,
            "share_url": share_url,
            "linkedin_url": linkedin_url,
        }

    _SELECT_COLS = """badge_id, badge_name, level, color, user_name, user_email,
                      score, skills, badge_type, issued_at, valid_until,
                      verification_hash, share_url, linkedin_url"""

    # ============================================================
    # ISSUE
    # ============================================================

    def issue_badge(self, data: Dict) -> Dict:
        """
        Issue a badge to a user.

        data = {
            "user_name": str,
            "user_email": str,
            "badge_type": str,
            "level": str,
            "score": int (optional),
            "skills": List[str] (optional)
        }
        """
        badge_id = f"BADGE-{secrets.token_hex(6).upper()}"
        badge_type = data.get("badge_type", "skill_twin")
        level = data.get("level", BadgeLevel.VERIFIED)

        badge_info = self.BADGE_TYPES.get(badge_type, self.BADGE_TYPES["skill_twin"])

        now = datetime.now()
        valid_until = now + timedelta(days=365)

        badge = {
            "badge_id": badge_id,
            "badge_name": badge_info["name"],
            "level": level,
            "color": self.BADGE_COLORS.get(level, "#3ba591"),
            "user_name": data.get("user_name"),
            "user_email": data.get("user_email"),
            "score": data.get("score"),
            "skills": data.get("skills", []),
            "badge_type": badge_type,
            "issued_at": now.isoformat(),
            "valid_until": valid_until.isoformat(),
            "verification_hash": hashlib.sha256(f"{badge_id}:{data.get('user_email')}".encode()).hexdigest()[:16],
            "share_url": f"https://charvakit.com/badge?ref={badge_id}",
            "linkedin_url": (
                "https://www.linkedin.com/profile/add?startTask=CERTIFICATION_NAME"
                f"&name={badge_info['name']}&organizationName=Charvak+IT+Consulting"
                f"&issueYear={now.year}&certId={badge_id}"
            ),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_badges (
                    badge_id, badge_name, level, color, user_name, user_email,
                    score, skills, badge_type, issued_at, valid_until,
                    verification_hash, share_url, linkedin_url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s)
            ''', (
                badge_id, badge["badge_name"], badge["level"], badge["color"],
                badge["user_name"], badge["user_email"], badge["score"],
                json.dumps(badge["skills"]), badge["badge_type"],
                now, valid_until,
                badge["verification_hash"], badge["share_url"], badge["linkedin_url"],
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"issue_badge failed: {e}")
            return {"status": "error", "message": "Could not issue badge"}

        logger.info(f"Badge issued: {badge_id} | {badge_info['name']} -> {data.get('user_name')}")

        return {
            "status": "success",
            "badge": badge,
            "message": f"{badge_info['name']} badge issued!",
            "share_text": f"I just earned the {badge_info['name']} ({level}) from Charvak IT Consulting! \U0001F3C6",
        }

    # ============================================================
    # VERIFY
    # ============================================================

    def verify_badge(self, badge_id: str) -> Dict:
        """Verify a badge is authentic."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(f'''
                SELECT {self._SELECT_COLS}
                FROM charvak_badges WHERE badge_id = %s
            ''', (badge_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"verify_badge failed: {e}")
            return {"status": "error", "verified": False, "message": "Badge not found"}

        if not row:
            return {"status": "error", "verified": False, "message": "Badge not found"}

        badge = self._row_to_badge(row)
        is_valid = datetime.fromisoformat(badge["valid_until"]) > datetime.now()

        return {
            "status": "success",
            "verified": is_valid,
            "badge": badge if is_valid else None,
            "message": "Badge verified" if is_valid else "Badge expired",
        }

    # ============================================================
    # USER BADGES
    # ============================================================

    def get_user_badges(self, email: str) -> Dict:
        """Get all active badges for a user."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(f'''
                SELECT {self._SELECT_COLS}
                FROM charvak_badges
                WHERE user_email = %s AND valid_until > NOW()
                ORDER BY issued_at DESC
            ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_user_badges failed: {e}")
            return {"status": "success", "badges": [], "count": 0, "display": []}

        user_badges = [self._row_to_badge(r) for r in rows]

        return {
            "status": "success",
            "badges": user_badges,
            "count": len(user_badges),
            "display": [
                {
                    "name": b["badge_name"],
                    "level": b["level"],
                    "color": b["color"],
                    "badge_id": b["badge_id"],
                    "share_url": b["share_url"],
                }
                for b in user_badges
            ],
        }

    # ============================================================
    # REVOKE
    # ============================================================

    def revoke_badge(self, badge_id: str) -> Dict:
        """Revoke a badge (sets valid_until to now)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_badges SET valid_until = NOW() WHERE badge_id = %s
            ''', (badge_id,))
            affected = cur.rowcount
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"revoke_badge failed: {e}")
            return {"status": "error", "message": "Could not revoke badge"}

        if affected == 0:
            return {"status": "error", "message": "Badge not found"}

        logger.info(f"Badge revoked: {badge_id}")
        return {"status": "success", "message": "Badge revoked"}

    # ============================================================
    # STATS
    # ============================================================

    def get_stats(self) -> Dict:
        """Get badge statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT COUNT(*) FROM charvak_badges')
            total = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_badges WHERE valid_until > NOW()')
            active = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(DISTINCT user_email) FROM charvak_badges')
            users_badged = int(cur.fetchone()[0] or 0)

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "total_badges_issued": total,
                "active_badges": active,
                "badge_types": list(self.BADGE_TYPES.keys()),
                "users_badged": users_badged,
            },
        }


badge_engine = BadgeEngine()