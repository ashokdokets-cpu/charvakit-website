# attempt_tracker.py
# Track and enforce attempt limits per user per assessment.
# Prevents retake abuse (user taking 100 times to game the score).

from typing import Dict
from datetime import datetime, timedelta


MAX_ATTEMPTS = 3                # max takes per (email, role, industry, level, format)
ATTEMPT_WINDOW_DAYS = 90        # attempts reset after 90 days


def _get_conn():
    from database import db
    return db.get_connection()


def count_attempts(email: str, role: str, industry: str, level: str, fmt: str = "mcq") -> Dict:
    """
    Count how many attempts a user has made for this exact assessment.

    Returns:
        {
            "attempts_used": int,
            "attempts_max": int,
            "attempts_remaining": int,
            "oldest_attempt_days_ago": int | None,
            "can_retake": bool,
            "reason": str
        }
    """
    email = (email or "").strip().lower()
    if not email:
        return {
            "attempts_used": 0,
            "attempts_max": MAX_ATTEMPTS,
            "attempts_remaining": MAX_ATTEMPTS,
            "oldest_attempt_days_ago": None,
            "can_retake": False,
            "reason": "Email required",
        }

    conn = _get_conn()
    cur = conn.cursor()

    try:
        # Only count attempts within the window
        cutoff = datetime.utcnow() - timedelta(days=ATTEMPT_WINDOW_DAYS)
        cur.execute("""
            SELECT COUNT(*), MIN(started_at)
            FROM charvak_career_assessments
            WHERE LOWER(email) = %s
              AND role = %s
              AND industry = %s
              AND level = %s
              AND format = %s
              AND started_at >= %s
        """, (email, role, industry, level, fmt, cutoff))
        row = cur.fetchone()
        attempts_used = int(row[0]) if row and row[0] else 0
        oldest = row[1] if row else None

        oldest_days_ago = None
        if oldest:
            oldest_days_ago = (datetime.utcnow() - oldest).days

        remaining = max(0, MAX_ATTEMPTS - attempts_used)

        if remaining == 0:
            reason = (
                f"You have used all {MAX_ATTEMPTS} attempts for this assessment. "
                f"Attempts reset after {ATTEMPT_WINDOW_DAYS} days. "
                f"Contact support if you need an exception."
            )
            can_retake = False
        else:
            reason = f"{remaining} attempt{'s' if remaining != 1 else ''} remaining."
            can_retake = True

        return {
            "attempts_used": attempts_used,
            "attempts_max": MAX_ATTEMPTS,
            "attempts_remaining": remaining,
            "oldest_attempt_days_ago": oldest_days_ago,
            "can_retake": can_retake,
            "reason": reason,
        }

    except Exception as e:
        # Don't block on error — default to allowed
        return {
            "attempts_used": 0,
            "attempts_max": MAX_ATTEMPTS,
            "attempts_remaining": MAX_ATTEMPTS,
            "oldest_attempt_days_ago": None,
            "can_retake": True,
            "reason": f"Attempt check unavailable ({e}); proceeding.",
        }
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass