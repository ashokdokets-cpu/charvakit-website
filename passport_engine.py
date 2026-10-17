"""
Career Passport v1 Engine (Session 46, Wave 1 of the flywheel)

Aggregates verified signals from across Charvak into a single
composite "Charvak Score" (0-1000) and a public passport page.

Design principles:
  - Read-only aggregation. No new state beyond the passport row itself.
  - Score is computed on demand; cached in `charvak_score`.
  - Handles are auto-generated and unique.
  - Public by default; users can hide later (is_public flag).
  - Reuses candidate_profile_engine for cross-product data.
"""

import os
import secrets
import logging
from datetime import datetime
from typing import Dict, Optional

from database import db

logger = logging.getLogger("charvakit.passport")


# ---------------------------------------------------------------
# Handles
# ---------------------------------------------------------------

def _slugify(text: str) -> str:
    """Lowercase alnum + hyphen. Empty string on failure."""
    if not text:
        return ""
    out = []
    for c in text.lower():
        if c.isalnum():
            out.append(c)
        elif c in (" ", "-", "_", "."):
            out.append("-")
    return "".join(out).strip("-")[:20]


def _derive_handle_seed(email: str, name: str = "") -> str:
    """Build a human-readable seed for the handle."""
    if name:
        # "John Doe" -> "john-doe" (then truncated)
        slug = _slugify(name)
        if slug:
            return slug
    # Fall back to email local-part
    if email and "@" in email:
        return _slugify(email.split("@")[0])[:16]
    return "user"


def _ensure_unique_handle(cur, seed: str, max_attempts: int = 10) -> str:
    """Try `{seed}-{4hex}` until unique. Returns final handle."""
    for _ in range(max_attempts):
        candidate = f"{seed}-{secrets.token_hex(2)}"  # 2 bytes = 4 hex chars
        cur.execute("SELECT 1 FROM charvak_passports WHERE handle = %s LIMIT 1", (candidate,))
        if not cur.fetchone():
            return candidate
    # Fallback: fully random
    return f"user-{secrets.token_hex(4)}"


# ---------------------------------------------------------------
# Score
# ---------------------------------------------------------------

def _score_tier(score: int) -> str:
    """Map 0-1000 score to a human-readable tier."""
    if score >= 900:
        return "elite"
    if score >= 700:
        return "strong"
    if score >= 500:
        return "solid"
    if score >= 300:
        return "developing"
    return "foundation"


def _compute_charvak_score(email: str) -> Dict:
    """
    Compute the composite Charvak Score (0-1000).

    Weights:
      40% - best readiness cert score (0-100)
      25% - best career assessment score (0-100)
      15% - breadth (distinct assessment count, capped at 10)
      20% - integrity cleanliness (100 if clean, drops with events)

    Returns:
      {score, tier, components: {readiness, career, breadth, integrity},
       breakdown: {...}}
    """
    components = {"readiness": 0, "career": 0, "breadth": 0, "integrity": 100}
    breakdown = {}

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        # Readiness: best score
        cur.execute("""
            SELECT MAX(readiness_score) FROM charvak_readiness_certificates
            WHERE email = %s
        """, (email,))
        row = cur.fetchone()
        readiness_best = (row[0] if row and row[0] is not None else 0) or 0
        components["readiness"] = int(readiness_best)
        breakdown["readiness_best"] = readiness_best

        # Career: best score (only completed)
        cur.execute("""
            SELECT MAX(score) FROM charvak_career_assessments
            WHERE email = %s AND status = 'completed'
        """, (email,))
        row = cur.fetchone()
        career_best = (row[0] if row and row[0] is not None else 0) or 0
        components["career"] = int(career_best)
        breakdown["career_best"] = career_best

        # Breadth: distinct assessment types
        cur.execute("""
            SELECT COUNT(DISTINCT assessment_type) FROM charvak_assessment_results
            WHERE email = %s
        """, (email,))
        row = cur.fetchone()
        distinct_types = (row[0] if row and row[0] is not None else 0) or 0

        # Add career format diversity
        cur.execute("""
            SELECT COUNT(DISTINCT format) FROM charvak_career_assessments
            WHERE email = %s AND status = 'completed'
        """, (email,))
        row = cur.fetchone()
        distinct_career_formats = (row[0] if row and row[0] is not None else 0) or 0

        breadth_count = distinct_types + distinct_career_formats
        breadth_pct = min(100, int(breadth_count * 10))  # 10 types = 100%
        components["breadth"] = breadth_pct
        breakdown["breadth_count"] = breadth_count
        breakdown["breadth_pct"] = breadth_pct

        # Integrity: 100 if no events, drops with events
        # Try to query integrity events
        integrity_score = 100
        try:
            cur.execute("""
                SELECT COUNT(*) FROM charvak_assessment_integrity_events
                WHERE email = %s
            """, (email,))
            row = cur.fetchone()
            total_events = (row[0] if row and row[0] is not None else 0) or 0
            breakdown["integrity_events"] = total_events
            if total_events == 0:
                integrity_score = 100
            elif total_events <= 5:
                integrity_score = 90
            elif total_events <= 15:
                integrity_score = 75
            else:
                integrity_score = 50
        except Exception as e:
            logger.warning(f"integrity check unavailable for {email}: {e}")
            breakdown["integrity_events"] = "unavailable"

        components["integrity"] = integrity_score

        cur.close()
    except Exception as e:
        logger.error(f"_compute_charvak_score failed for {email}: {e}")
    finally:
        if conn:
            try: conn.close()
            except Exception: pass

    # Weighted composite, scaled to 0-1000
    weighted = (
        components["readiness"] * 0.40 +
        components["career"] * 0.25 +
        components["breadth"] * 0.15 +
        components["integrity"] * 0.20
    )
    final = max(0, min(1000, int(round(weighted * 10))))

    return {
        "score": final,
        "tier": _score_tier(final),
        "components": components,
        "breakdown": breakdown,
    }


# ---------------------------------------------------------------
# Aggregate data for the passport page
# ---------------------------------------------------------------

def _get_aggregate_data(email: str) -> Dict:
    """
    Fetch the raw data needed to render a passport.
    Read-only. Reuses tables directly for clarity.
    """
    data = {
        "certificates": [],
        "career_assessments": [],
        "other_assessments": [],
        "courses": [],
        "integrity": {"total_events": 0, "risk_level": "clean"},
    }

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        # Readiness certificates
        cur.execute("""
            SELECT certificate_id, role, industry, level, readiness_score,
                   verdict, certificate_hash, created_at
            FROM charvak_readiness_certificates
            WHERE email = %s ORDER BY created_at DESC LIMIT 20
        """, (email,))
        for r in cur.fetchall():
            data["certificates"].append({
                "id": r[0],
                "role": r[1],
                "industry": r[2],
                "level": r[3],
                "score": r[4],
                "verdict": r[5],
                "hash": r[6],
                "issued_at": r[7].isoformat() if r[7] else None,
            })

        # Career assessments (completed only)
        cur.execute("""
            SELECT assessment_id, role, industry, level, format, size,
                   score, passed, completed_at, integrity_summary
            FROM charvak_career_assessments
            WHERE email = %s AND status = 'completed'
            ORDER BY completed_at DESC LIMIT 20
        """, (email,))
        for r in cur.fetchall():
            data["career_assessments"].append({
                "id": r[0],
                "role": r[1],
                "industry": r[2],
                "level": r[3],
                "format": r[4],
                "size": r[5],
                "score": r[6],
                "passed": r[7],
                "completed_at": r[8].isoformat() if r[8] else None,
                "integrity": r[9] or {},
            })

        # Other assessment results (IELTS, Versant, Mock, CBAT)
        cur.execute("""
            SELECT assessment_type, assessment_name, percentage, passed, completed_at
            FROM charvak_assessment_results
            WHERE email = %s ORDER BY completed_at DESC LIMIT 30
        """, (email,))
        for r in cur.fetchall():
            data["other_assessments"].append({
                "type": r[0],
                "name": r[1],
                "score": float(r[2]) if r[2] is not None else 0,
                "passed": r[3],
                "completed_at": r[4].isoformat() if r[4] else None,
            })

        # Course certificates
        cur.execute("""
            SELECT certificate_id, course_name, duration_weeks, issued_at
            FROM charvak_certificates
            WHERE email = %s ORDER BY issued_at DESC LIMIT 20
        """, (email,))
        for r in cur.fetchall():
            data["courses"].append({
                "id": r[0],
                "course_name": r[1],
                "duration_weeks": r[2],
                "issued_at": r[3].isoformat() if r[3] else None,
            })

        # Integrity summary
        try:
            cur.execute("""
                SELECT COUNT(*) FROM charvak_assessment_integrity_events
                WHERE email = %s
            """, (email,))
            total = cur.fetchone()[0] or 0
            data["integrity"]["total_events"] = total
            data["integrity"]["risk_level"] = (
                "clean" if total == 0 else
                "minor" if total <= 5 else
                "moderate" if total <= 15 else
                "elevated"
            )
        except Exception:
            pass

        cur.close()
    except Exception as e:
        logger.error(f"_get_aggregate_data failed for {email}: {e}")
    finally:
        if conn:
            try: conn.close()
            except Exception: pass

    return data


# ---------------------------------------------------------------
# Public engine methods
# ---------------------------------------------------------------

def create_or_get_passport(email: str, display_name: str = "",
                            headline: str = "") -> Dict:
    """Create a passport for `email` if missing, else return existing."""
    # Defensive: accept either a string or a user dict (require_auth returns a dict)
    if isinstance(email, dict):
        email = email.get("email") or ""
    email = (email or "").strip().lower() if isinstance(email, str) else ""
    if not email or "@" not in email:
        return {"status": "error", "message": "Valid email required"}

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        # Check existing
        cur.execute("""
            SELECT passport_id, handle, email, display_name, headline,
                   charvak_score, score_tier, is_public, created_at
            FROM charvak_passports WHERE email = %s
        """, (email,))
        existing = cur.fetchone()

        if existing:
            cur.close()
            return {
                "status": "exists",
                "passport": {
                    "passport_id": existing[0],
                    "handle": existing[1],
                    "email": existing[2],
                    "display_name": existing[3],
                    "headline": existing[4],
                    "charvak_score": existing[5],
                    "score_tier": existing[6],
                    "is_public": existing[7],
                    "created_at": existing[8].isoformat() if existing[8] else None,
                },
            }

        # Generate handle
        seed = _derive_handle_seed(email, display_name)
        handle = _ensure_unique_handle(cur, seed)
        passport_id = f"PASS-{secrets.token_hex(6).upper()}"

        cur.execute("""
            INSERT INTO charvak_passports
              (passport_id, handle, email, display_name, headline)
            VALUES (%s, %s, %s, %s, %s)
        """, (passport_id, handle, email, display_name or None, headline or None))
        conn.commit()

        cur.close()
        return {
            "status": "created",
            "passport": {
                "passport_id": passport_id,
                "handle": handle,
                "email": email,
                "display_name": display_name or None,
                "headline": headline or None,
                "charvak_score": 0,
                "score_tier": "foundation",
                "is_public": True,
            },
        }
    except Exception as e:
        logger.error(f"create_or_get_passport failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


def get_passport_by_handle(handle: str, include_score: bool = True) -> Dict:
    """Full passport payload: identity + score + all aggregate data."""
    handle = (handle or "").strip().lower()
    if not handle:
        return {"status": "error", "message": "handle required"}

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT passport_id, handle, email, display_name, headline,
                   charvak_score, score_tier, is_public, created_at, updated_at
            FROM charvak_passports WHERE handle = %s
        """, (handle,))
        row = cur.fetchone()
        cur.close()
    except Exception as e:
        logger.error(f"get_passport_by_handle failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass

    if not row:
        return {"status": "error", "message": "Passport not found"}

    passport = {
        "passport_id": row[0],
        "handle": row[1],
        "email": row[2],
        "display_name": row[3],
        "headline": row[4],
        "charvak_score": row[5],
        "score_tier": row[6],
        "is_public": row[7],
        "created_at": row[8].isoformat() if row[8] else None,
        "updated_at": row[9].isoformat() if row[9] else None,
    }

    if not passport["is_public"]:
        return {"status": "error", "message": "This passport is private"}

    data = _get_aggregate_data(passport["email"])
    passport["certificates"] = data["certificates"]
    passport["career_assessments"] = data["career_assessments"]
    passport["other_assessments"] = data["other_assessments"]
    passport["courses"] = data["courses"]
    passport["integrity"] = data["integrity"]

    # Compute (or refresh) score
    if include_score:
        try:
            score_result = _compute_charvak_score(passport["email"])
            passport["charvak_score"] = score_result["score"]
            passport["score_tier"] = score_result["tier"]
            passport["score_breakdown"] = score_result["components"]
            passport["score_details"] = score_result["breakdown"]
            # Persist fresh score
            try:
                conn2 = db.get_connection()
                cur2 = conn2.cursor()
                cur2.execute("""
                    UPDATE charvak_passports
                    SET charvak_score = %s, score_tier = %s, score_updated_at = NOW()
                    WHERE handle = %s
                """, (score_result["score"], score_result["tier"], handle))
                conn2.commit()
                cur2.close()
                conn2.close()
            except Exception as e:
                logger.warning(f"score persist failed: {e}")
        except Exception as e:
            logger.warning(f"score compute failed: {e}")

    return {"status": "success", "passport": passport}


def get_passport_by_email(email: str) -> Dict:
    """Lookup passport by email; used for /passport/me."""
    # Defensive: accept either a string or a user dict (require_auth returns a dict)
    if isinstance(email, dict):
        email = email.get("email") or ""
    email = (email or "").strip().lower() if isinstance(email, str) else ""
    if not email:
        return {"status": "error", "message": "email required"}
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT handle FROM charvak_passports WHERE email = %s", (email,))
        row = cur.fetchone()
        cur.close()
    except Exception as e:
        logger.error(f"get_passport_by_email failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass
    if not row:
        return {"status": "error", "message": "No passport for this email"}
    return {"status": "success", "handle": row[0]}


passport_engine = None  # stateless; module-level functions


def __getattr__(name):
    """Lazy compat for singleton-style imports."""
    import sys
    return sys.modules[__name__]