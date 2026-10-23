"""
engagement_engine.py
Session 81 A3 — Unified student engagement dashboard.
Aggregates streaks (drills_engine), passport (passport_engine), cohorts
(cohorts_engine) into one dashboard. Awards badges on milestones.
"""

import logging
import secrets
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.engagement")


BADGE_CATALOG = {
    "streak_3": {"name": "3-Day Streak", "icon": "🔥", "desc": "3 days in a row"},
    "streak_7": {"name": "Week Warrior", "icon": "🔥🔥", "desc": "7 days in a row"},
    "streak_14": {"name": "Fortnight Fighter", "icon": "⚡", "desc": "14 days in a row"},
    "streak_30": {"name": "Monthly Master", "icon": "👑", "desc": "30 days in a row"},
    "drills_10": {"name": "First Ten", "icon": "🎯", "desc": "10 drills completed"},
    "drills_50": {"name": "Half Century", "icon": "🏆", "desc": "50 drills completed"},
    "drills_100": {"name": "Century", "icon": "💯", "desc": "100 drills completed"},
    "passport_500": {"name": "Strong Candidate", "icon": "🌟", "desc": "Charvak score 500+"},
    "passport_750": {"name": "Elite Candidate", "icon": "💎", "desc": "Charvak score 750+"},
}


def _ensure_tables():
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charvak_student_preferences (
                email TEXT PRIMARY KEY,
                email_enabled BOOLEAN DEFAULT TRUE,
                in_app_enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS charvak_student_badges (
                badge_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                badge_key TEXT NOT NULL,
                badge_name TEXT NOT NULL,
                badge_icon TEXT DEFAULT '🏆',
                description TEXT,
                awarded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(email, badge_key)
            );
            CREATE TABLE IF NOT EXISTS charvak_engagement_events (
                event_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data JSONB DEFAULT '{}'::jsonb,
                points INTEGER DEFAULT 0,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.debug(f"_ensure_tables failed (will retry on use): {e}")


def get_or_create_preferences(email: str) -> Dict:
    """Get or create preferences for a student."""
    _ensure_tables()
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT email, email_enabled, in_app_enabled FROM charvak_student_preferences WHERE email = %s", (email,))
        row = cur.fetchone()
        if not row:
            cur.execute("""
                INSERT INTO charvak_student_preferences (email, email_enabled, in_app_enabled)
                VALUES (%s, TRUE, TRUE)
                ON CONFLICT (email) DO NOTHING
            """, (email,))
            conn.commit()
            return {"email": email, "email_enabled": True, "in_app_enabled": True}
        cur.close()
        conn.close()
        return {"email": row[0], "email_enabled": row[1], "in_app_enabled": row[2]}
    except Exception as e:
        logger.warning(f"get_or_create_preferences failed: {e}")
        return {"email": email, "email_enabled": True, "in_app_enabled": True}


def update_preferences(email: str, email_enabled: bool = None, in_app_enabled: bool = None) -> Dict:
    """Update preferences."""
    _ensure_tables()
    get_or_create_preferences(email)
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        if email_enabled is not None:
            cur.execute("UPDATE charvak_student_preferences SET email_enabled = %s, updated_at = NOW() WHERE email = %s", (email_enabled, email))
        if in_app_enabled is not None:
            cur.execute("UPDATE charvak_student_preferences SET in_app_enabled = %s, updated_at = NOW() WHERE email = %s", (in_app_enabled, email))
        conn.commit()
        cur.close()
        conn.close()
        return get_or_create_preferences(email)
    except Exception as e:
        logger.warning(f"update_preferences failed: {e}")
        return get_or_create_preferences(email)


def _award_badge(email: str, badge_key: str) -> bool:
    """Award a badge if not already earned. Returns True if newly awarded."""
    _ensure_tables()
    info = BADGE_CATALOG.get(badge_key)
    if not info:
        return False
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        badge_id = f"BADGE-{secrets.token_hex(6).upper()}"
        cur.execute("""
            INSERT INTO charvak_student_badges
                (badge_id, email, badge_key, badge_name, badge_icon, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (email, badge_key) DO NOTHING
        """, (badge_id, email, badge_key, info["name"], info["icon"], info["desc"]))
        awarded = cur.rowcount > 0
        conn.commit()
        cur.close()
        conn.close()
        if awarded:
            record_event(email, "badge_earned", {"badge_key": badge_key, "badge_name": info["name"]}, points=10)
        return awarded
    except Exception as e:
        logger.debug(f"_award_badge failed: {e}")
        return False


def record_event(email: str, event_type: str, event_data: Dict = None, points: int = 0) -> str:
    """Record an engagement event."""
    _ensure_tables()
    try:
        from database import db
        import json
        conn = db.get_connection()
        cur = conn.cursor()
        event_id = f"EVT-{secrets.token_hex(6).upper()}"
        cur.execute("""
            INSERT INTO charvak_engagement_events (event_id, email, event_type, event_data, points)
            VALUES (%s, %s, %s, %s::jsonb, %s)
        """, (event_id, email, event_type, json.dumps(event_data or {}), points))
        conn.commit()
        cur.close()
        conn.close()
        return event_id
    except Exception as e:
        logger.debug(f"record_event failed: {e}")
        return ""


def check_and_award_badges(email: str) -> List[str]:
    """Check all milestone conditions and award any earned badges. Returns newly awarded keys."""
    newly_awarded = []

    # Streak milestones
    try:
        import drills_engine as de
        streak_info = de.get_streak_stats(email) or {}
        streak = streak_info.get("current_streak", 0) or 0
        total = streak_info.get("total_drills", 0) or 0

        if streak >= 3: _award_badge(email, "streak_3") and newly_awarded.append("streak_3")
        if streak >= 7: _award_badge(email, "streak_7") and newly_awarded.append("streak_7")
        if streak >= 14: _award_badge(email, "streak_14") and newly_awarded.append("streak_14")
        if streak >= 30: _award_badge(email, "streak_30") and newly_awarded.append("streak_30")
        if total >= 10: _award_badge(email, "drills_10") and newly_awarded.append("drills_10")
        if total >= 50: _award_badge(email, "drills_50") and newly_awarded.append("drills_50")
        if total >= 100: _award_badge(email, "drills_100") and newly_awarded.append("drills_100")
    except Exception as e:
        logger.debug(f"streak badge check failed: {e}")

    # Passport milestones
    try:
        import passport_engine as pe
        passport = pe.get_passport_by_email(email) or {}
        score = (passport.get("passport") or {}).get("charvak_score", 0) or 0
        if score >= 500: _award_badge(email, "passport_500") and newly_awarded.append("passport_500")
        if score >= 750: _award_badge(email, "passport_750") and newly_awarded.append("passport_750")
    except Exception as e:
        logger.debug(f"passport badge check failed: {e}")

    # Dedupe list
    return list(set(newly_awarded))


def get_student_badges(email: str, limit: int = 20) -> List[Dict]:
    """Get all badges earned by a student."""
    _ensure_tables()
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT badge_key, badge_name, badge_icon, description, awarded_at
            FROM charvak_student_badges
            WHERE email = %s
            ORDER BY awarded_at DESC LIMIT %s
        """, (email, limit))
        badges = []
        for r in cur.fetchall():
            badges.append({
                "key": r[0], "name": r[1], "icon": r[2],
                "description": r[3],
                "awarded_at": r[4].isoformat() if r[4] else None
            })
        cur.close()
        conn.close()
        return badges
    except Exception as e:
        logger.debug(f"get_student_badges failed: {e}")
        return []


def get_global_leaderboard(limit: int = 20) -> List[Dict]:
    """Top students by Charvak score."""
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.handle, p.display_name, p.charvak_score, p.score_tier
            FROM charvak_passports p
            WHERE p.is_public = TRUE
            ORDER BY p.charvak_score DESC NULLS LAST
            LIMIT %s
        """, (limit,))
        results = []
        for r in cur.fetchall():
            results.append({
                "handle": r[0], "display_name": r[1],
                "score": r[2] or 0, "tier": r[3] or "foundation"
            })
        cur.close()
        conn.close()
        return results
    except Exception as e:
        logger.debug(f"get_global_leaderboard failed: {e}")
        return []


def get_student_dashboard(email: str) -> Dict:
    """Unified student dashboard — aggregates streaks, drills, passport, cohorts, badges."""
    _ensure_tables()

    # Streaks + drills
    streak_data = {}
    try:
        import drills_engine as de
        streak_data = de.get_streak_stats(email) or {}
    except Exception as e:
        logger.debug(f"streak data failed: {e}")

    # Passport
    passport_data = {}
    try:
        import passport_engine as pe
        passport_data = pe.get_passport_by_email(email) or {}
    except Exception as e:
        logger.debug(f"passport failed: {e}")

    # Cohorts
    cohort_data = {"cohorts": []}
    try:
        import cohorts_engine as ce
        cohort_data = ce.list_my_cohorts(email) or {"cohorts": []}
    except Exception as e:
        logger.debug(f"cohorts failed: {e}")

    # Badges (also triggers re-check)
    try:
        check_and_award_badges(email)
    except Exception:
        pass
    badges = get_student_badges(email)

    # Recent drills for 7-day strip
    recent_drills = []
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT drill_date::text, score, correct_count, total_questions, completed
            FROM charvak_daily_drills
            WHERE email = %s AND drill_date >= %s
            ORDER BY drill_date DESC
        """, (email, date.today() - timedelta(days=7)))
        for r in cur.fetchall():
            recent_drills.append({
                "date": r[0], "score": r[1],
                "correct": r[2], "total": r[3], "completed": r[4]
            })
        cur.close()
        conn.close()
    except Exception as e:
        logger.debug(f"recent drills failed: {e}")

    # Global leaderboard
    global_lb = get_global_leaderboard(limit=10)

    # Compute global rank
    my_score = (passport_data.get("passport") or {}).get("charvak_score", 0) or 0
    my_rank = None
    for idx, entry in enumerate(global_lb, start=1):
        if entry["score"] <= my_score:
            my_rank = idx
            break
    if my_rank is None and my_score > 0:
        my_rank = len(global_lb) + 1

    # Next milestone
    total_drills = streak_data.get("total_drills", 0) or 0
    next_milestone = None
    for milestone in [(10, "drills_10"), (50, "drills_50"), (100, "drills_100")]:
        if total_drills < milestone[0]:
            next_milestone = {
                "target": milestone[0],
                "current": total_drills,
                "badge": BADGE_CATALOG[milestone[1]]
            }
            break

    return {
        "status": "success",
        "email": email,
        "streak": {
            "current": streak_data.get("current_streak", 0) or 0,
            "longest": streak_data.get("longest_streak", 0) or 0,
            "total_drills": total_drills,
            "total_correct": streak_data.get("total_correct", 0) or 0,
            "last_drill_date": streak_data.get("last_drill_date"),
        },
        "passport": {
            "handle": (passport_data.get("passport") or {}).get("handle"),
            "score": my_score,
            "tier": (passport_data.get("passport") or {}).get("score_tier", "foundation"),
            "rank_global": my_rank,
        },
        "badges": badges,
        "recent_drills_7d": recent_drills,
        "cohorts": cohort_data.get("cohorts", []),
        "global_leaderboard": global_lb,
        "next_milestone": next_milestone,
        "preferences": get_or_create_preferences(email),
    }