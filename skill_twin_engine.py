"""
Skill Twin Challenges Engine (Session 46-B, Wave 1 of the flywheel)

Viral loop: a passport holder creates a shareable "beat my score"
challenge. Friends open the link, take a quick assessment, and see
a side-by-side comparison. Both sides are tracked for credits.
"""

import os
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

from database import db

logger = logging.getLogger("charvakit.skill_twin")


# ---------------------------------------------------------------
# Session 46-B: field normalization helpers
# Reject invalid role/industry/level from leaking into challenges.
# ---------------------------------------------------------------

_SAFE_ROLE_FALLBACKS = ["Backend Engineer", "Full-Stack Engineer",
                        "Frontend Engineer", "Data Analyst"]
_SAFE_INDUSTRY_FALLBACK = "IT / Tech (general)"
_SAFE_LEVEL_FALLBACK = "mid"


def _normalize_career_field(field: str, value: str) -> str:
    """
    Validate a role/industry/level string against career_assessment_engine's
    catalog. Returns the value if valid, else a safe fallback.
    Never raises — worst case, returns the fallback.
    """
    if not value or not isinstance(value, str):
        return {"role": "Backend Engineer",
                "industry": _SAFE_INDUSTRY_FALLBACK,
                "level": _SAFE_LEVEL_FALLBACK}.get(field, "")

    try:
        from career_assessment_engine import (
            career_assessment_engine as cae,
            CAREER_ROLES, CAREER_INDUSTRIES, CAREER_LEVELS,
        )

        if field == "role":
            all_roles = []
            for cat_roles in CAREER_ROLES.values():
                all_roles.extend(cat_roles)
            if value in all_roles:
                return value
            lower = value.lower()
            for r in all_roles:
                if r.lower() == lower:
                    return r
            for r in all_roles:
                if lower in r.lower() or r.lower() in lower:
                    return r
            for fb in _SAFE_ROLE_FALLBACKS:
                if fb in all_roles:
                    return fb
            return all_roles[0] if all_roles else "Backend Engineer"

        elif field == "industry":
            if value in CAREER_INDUSTRIES:
                return value
            lower = value.lower()
            for i in CAREER_INDUSTRIES:
                if i.lower() == lower:
                    return i
            for i in CAREER_INDUSTRIES:
                if lower in i.lower() or i.lower() in lower:
                    return i
            if _SAFE_INDUSTRY_FALLBACK in CAREER_INDUSTRIES:
                return _SAFE_INDUSTRY_FALLBACK
            return CAREER_INDUSTRIES[0] if CAREER_INDUSTRIES else _SAFE_INDUSTRY_FALLBACK

        elif field == "level":
            valid_keys = [l["key"] for l in CAREER_LEVELS]
            v = value.lower().strip()
            if v in valid_keys:
                return v
            alias = {
                "intern/student": "intern", "intern / student": "intern",
                "entry": "junior", "entry-level": "junior",
                "mid-level": "mid", "midlevel": "mid",
                "sr": "senior", "sr.": "senior",
                "staff/principal": "staff", "principal": "staff",
                "manager/director": "manager", "director": "manager",
                "executive": "executive", "vp": "executive", "c-level": "executive",
            }
            if v in alias and alias[v] in valid_keys:
                return alias[v]
            return _SAFE_LEVEL_FALLBACK if _SAFE_LEVEL_FALLBACK in valid_keys else valid_keys[0]

    except Exception as e:
        logger.warning(f"_normalize_career_field({field}={value!r}) failed: {e}")

    return {"role": "Backend Engineer",
            "industry": _SAFE_INDUSTRY_FALLBACK,
            "level": _SAFE_LEVEL_FALLBACK}.get(field, "")


# ---------------------------------------------------------------
# Create challenge
# ---------------------------------------------------------------

def create_challenge(owner_email: str, role: str = "", industry: str = "",
                     level: str = "", expires_days: int = 7) -> Dict:
    """
    Owner (passport holder) creates a challenge link.
    Captures their current passport score snapshot.
    """
    owner_email = (owner_email or "").strip().lower()
    if not owner_email or "@" not in owner_email:
        return {"status": "error", "message": "Valid email required"}

    # Session 46-B: normalize role/industry/level against career_assessment_engine catalog
    role = _normalize_career_field("role", role)
    industry = _normalize_career_field("industry", industry)
    level = _normalize_career_field("level", level)

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        # Load owner's passport
        cur.execute("""
            SELECT handle, charvak_score FROM charvak_passports
            WHERE email = %s
        """, (owner_email,))
        row = cur.fetchone()
        if not row:
            cur.close(); conn.close()
            return {"status": "error", "message": "You need to create a passport first"}

        owner_handle, owner_score = row[0], row[1] or 0

        # Create challenge
        challenge_id = secrets.token_urlsafe(10)
        expires_at = datetime.utcnow() + timedelta(days=expires_days)

        cur.execute("""
            INSERT INTO charvak_skill_twin_challenges
              (challenge_id, owner_email, owner_handle, owner_score,
               role, industry, level, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (challenge_id, owner_email, owner_handle, owner_score,
              role or None, industry or None, level or None, expires_at))
        conn.commit()
        cur.close(); conn.close()

        site = os.getenv("SITE_URL", "https://www.charvakit.com").rstrip("/")
        return {
            "status": "success",
            "challenge_id": challenge_id,
            "challenge_url": f"{site}/skill-twin/{challenge_id}",
            "owner_handle": owner_handle,
            "owner_score": owner_score,
            "expires_at": expires_at.isoformat(),
            "expires_days": expires_days,
        }
    except Exception as e:
        logger.error(f"create_challenge failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


# ---------------------------------------------------------------
# Fetch challenge
# ---------------------------------------------------------------

def get_challenge(challenge_id: str, count_click: bool = True) -> Dict:
    """Return the challenge state. Optionally increments click counter."""
    challenge_id = (challenge_id or "").strip()
    if not challenge_id:
        return {"status": "error", "message": "challenge_id required"}

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        if count_click:
            cur.execute("""
                UPDATE charvak_skill_twin_challenges
                SET clicked_count = clicked_count + 1
                WHERE challenge_id = %s AND status = 'pending'
            """, (challenge_id,))
            conn.commit()

        cur.execute("""
            SELECT challenge_id, owner_email, owner_handle, owner_score,
                   role, industry, level, status,
                   challenger_email, challenger_score, challenger_pct,
                   winner, credits_owner, credits_challenger,
                   created_at, accepted_at, expires_at, clicked_count
            FROM charvak_skill_twin_challenges WHERE challenge_id = %s
        """, (challenge_id,))
        row = cur.fetchone()
        cur.close(); conn.close()

        if not row:
            return {"status": "error", "message": "Challenge not found"}

        # Check expiry
        expires_at = row[16]
        is_expired = expires_at and datetime.utcnow() > expires_at

        return {
            "status": "success",
            "challenge": {
                "challenge_id": row[0],
                "owner_email": row[1],
                "owner_handle": row[2],
                "owner_score": row[3],
                "role": row[4],
                "industry": row[5],
                "level": row[6],
                "challenge_status": row[7],
                "challenger_email": row[8],
                "challenger_score": row[9],
                "challenger_pct": row[10],
                "winner": row[11],
                "credits_owner": row[12],
                "credits_challenger": row[13],
                "created_at": row[14].isoformat() if row[14] else None,
                "accepted_at": row[15].isoformat() if row[15] else None,
                "expires_at": expires_at.isoformat() if expires_at else None,
                "clicked_count": row[17],
                "is_expired": is_expired,
            },
        }
    except Exception as e:
        logger.error(f"get_challenge failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


# ---------------------------------------------------------------
# Start the challenger's assessment
# ---------------------------------------------------------------

def start_challenger_assessment(challenge_id: str,
                                 challenger_email: str = "") -> Dict:
    """
    Initiate a 10-question MCQ assessment for the challenger.
    Reuses the career_assessment_engine's quick MCQ path but
    associates it with this challenge.

    Returns: {assessment_id, questions, challenge}
    """
    challenge_id = (challenge_id or "").strip()
    if not challenge_id:
        return {"status": "error", "message": "challenge_id required"}

    # Load the challenge (don't count click twice)
    ch = get_challenge(challenge_id, count_click=False)
    if ch.get("status") != "success":
        return ch

    c = ch["challenge"]
    if c.get("challenge_status") != "pending":
        return {"status": "error", "message": "Challenge already completed or expired"}
    if c.get("is_expired"):
        return {"status": "error", "message": "This challenge has expired"}

    # Use the career assessment engine for question generation
    try:
        from career_assessment_engine import career_assessment_engine

        # Defaults if challenge has no role/level
        role = c.get("role") or "Backend Engineer"
        industry = c.get("industry") or "IT / Tech (general)"
        level = c.get("level") or "mid"

        # Session 46-B: normalize again (defense in depth — older challenge rows
        # may have invalid values from before the create_challenge fix)
        role = _normalize_career_field("role", role)
        industry = _normalize_career_field("industry", industry)
        level = _normalize_career_field("level", level)
        logger.info(f"skill_twin start: normalized role={role!r} industry={industry!r} level={level!r}")

        # Compute an email-like token for the challenger (anonymous OK)
        # The assessment engine needs a unique email per attempt
        attempt_email = challenger_email or f"challenge-{challenge_id}-{secrets.token_hex(4)}@charvak.local"

        result = career_assessment_engine.start_assessment({
            "email": attempt_email,
            "role": role,
            "industry": industry,
            "level": level,
            "format": "mcq",
            "size": "quick",
        })

        if result.get("status") != "success":
            return result

        # Session 46-B: persist the attempt email so submit can match ownership
        try:
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE charvak_skill_twin_challenges
                SET challenger_attempt_email = %s
                WHERE challenge_id = %s
            """, (attempt_email, challenge_id))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.warning(f"could not persist attempt_email: {e}")

        # Session 46-B: questions are nested under result["assessment"]["questions"]
        assessment_payload = result.get("assessment") or {}
        questions = assessment_payload.get("questions") or result.get("questions") or []

        return {
            "status": "success",
            "challenge_id": challenge_id,
            "assessment_id": result.get("assessment_id"),
            "attempt_email": attempt_email,
            "questions": questions,
            "challenge": c,
        }
    except Exception as e:
        logger.error(f"start_challenger_assessment failed: {e}")
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------------
# Submit challenger answers + record the challenge result
# ---------------------------------------------------------------

def submit_challenger(challenge_id: str, assessment_id: str,
                       challenger_email: str = "", answers: list = None) -> Dict:
    """
    Submit the challenger's answers, score the assessment,
    compare against owner_score, set winner, track credits.
    """
    challenge_id = (challenge_id or "").strip()
    assessment_id = (assessment_id or "").strip()
    if not challenge_id or not assessment_id:
        return {"status": "error", "message": "challenge_id and assessment_id required"}

    # Load the challenge (don't count click)
    ch = get_challenge(challenge_id, count_click=False)
    if ch.get("status") != "success":
        return ch
    c = ch["challenge"]
    if c.get("challenge_status") != "pending":
        return {"status": "error", "message": "Challenge already completed"}
    if c.get("is_expired"):
        return {"status": "error", "message": "Challenge expired"}

    # Submit answers via career_assessment_engine
    try:
        from career_assessment_engine import career_assessment_engine

        # Load the persisted attempt email (set at start)
        attempt_email = None
        try:
            conn_chk = db.get_connection()
            cur_chk = conn_chk.cursor()
            cur_chk.execute("""
                SELECT challenger_attempt_email FROM charvak_skill_twin_challenges
                WHERE challenge_id = %s
            """, (challenge_id,))
            r_chk = cur_chk.fetchone()
            cur_chk.close(); conn_chk.close()
            if r_chk:
                attempt_email = r_chk[0]
        except Exception as e:
            logger.warning(f"could not read attempt_email: {e}")

        if not attempt_email:
            attempt_email = c.get("challenger_email") or f"challenge-{challenge_id}@charvak.local"

        # Complete the assessment to get the score
        submit_result = career_assessment_engine.complete_assessment({
            "assessment_id": assessment_id,
            "email": attempt_email,
            "answers": answers or [],
        })

        if submit_result.get("status") != "success":
            return submit_result

        # Raw percentage 0-100
        raw_pct = submit_result.get("score", 0)
        if not isinstance(raw_pct, (int, float)):
            raw_pct = 0

        # Normalize to 0-1000 to compare with owner_score
        challenger_score = int(round(raw_pct * 10))

        # Determine winner
        owner_score = c.get("owner_score", 0)
        if challenger_score > owner_score:
            winner = "challenger"
            credits_owner = 0
            credits_challenger = 5
        elif challenger_score < owner_score:
            winner = "owner"
            credits_owner = 5
            credits_challenger = 0
        else:
            winner = "tie"
            credits_owner = 3
            credits_challenger = 3

        # Update the challenge row
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE charvak_skill_twin_challenges
            SET status = 'completed',
                challenger_email = %s,
                challenger_score = %s,
                challenger_pct = %s,
                challenger_assessment_id = %s,
                winner = %s,
                credits_owner = %s,
                credits_challenger = %s,
                accepted_at = NOW()
            WHERE challenge_id = %s AND status = 'pending'
        """, (challenger_email or None, challenger_score, int(raw_pct),
              assessment_id, winner, credits_owner, credits_challenger,
              challenge_id))
        conn.commit()
        cur.close(); conn.close()

        return {
            "status": "success",
            "challenge_id": challenge_id,
            "owner_score": owner_score,
            "challenger_score": challenger_score,
            "challenger_pct": int(raw_pct),
            "winner": winner,
            "credits_owner": credits_owner,
            "credits_challenger": credits_challenger,
            "owner_handle": c.get("owner_handle"),
        }
    except Exception as e:
        logger.error(f"submit_challenger failed: {e}")
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------------
# Owner-facing list
# ---------------------------------------------------------------

def list_challenges(owner_email: str, limit: int = 20) -> Dict:
    """Owner sees their challenge history."""
    owner_email = (owner_email or "").strip().lower()
    if not owner_email:
        return {"status": "error", "message": "email required"}

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT challenge_id, owner_score, status, winner,
                   challenger_score, created_at, clicked_count,
                   credits_owner, credits_challenger
            FROM charvak_skill_twin_challenges
            WHERE owner_email = %s
            ORDER BY created_at DESC LIMIT %s
        """, (owner_email, limit))
        rows = cur.fetchall()
        cur.close(); conn.close()

        items = []
        for r in rows:
            items.append({
                "challenge_id": r[0],
                "owner_score": r[1],
                "status": r[2],
                "winner": r[3],
                "challenger_score": r[4],
                "created_at": r[5].isoformat() if r[5] else None,
                "clicked_count": r[6],
                "credits_owner": r[7],
                "credits_challenger": r[8],
            })

        return {"status": "success", "challenges": items, "count": len(items)}
    except Exception as e:
        logger.error(f"list_challenges failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


skill_twin_engine = None  # module-level functions


def __getattr__(name):
    import sys
    return sys.modules[__name__]