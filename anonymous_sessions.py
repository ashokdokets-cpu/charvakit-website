"""
anonymous_sessions.py - Session 43-A1.5a

Allows users to take career assessments before registering.
Sessions are stored in charvak_anonymous_assessment_sessions.

Flow:
  1. User starts assessment without auth → we generate a token
  2. User answers questions with the token
  3. User sees their score
  4. To save the certificate, they register
  5. The token is claimed → assessment migrated to their real email

Design notes:
  - Tokens are 32-char hex (secrets.token_hex(16))
  - TTL: 24 hours
  - Placeholder emails use "@anon.charvak.local" suffix
  - Claimed tokens keep the assessment_id link for audit
  - Cleanup: rows older than 30 days can be pruned (cron, future)
"""

import secrets
from datetime import datetime, timedelta, timezone


TOKEN_TTL_HOURS = 24
PLACEHOLDER_SUFFIX = "@anon.charvak.local"


def _ensure_table() -> None:
    """Self-healing DDL. Safe to call on every request."""
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS charvak_anonymous_assessment_sessions (
            token             TEXT PRIMARY KEY,
            assessment_id     TEXT NOT NULL,
            created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            expires_at        TIMESTAMPTZ NOT NULL,
            claimed_by_email  TEXT,
            claimed_at        TIMESTAMPTZ
        )
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_anon_sessions_assessment
        ON charvak_anonymous_assessment_sessions (assessment_id)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_anon_sessions_expires
        ON charvak_anonymous_assessment_sessions (expires_at)
    """)
    conn.commit()
    cur.close()
    conn.close()


def create_session(assessment_id: str) -> str:
    """Generate a new anonymous token for the given assessment_id."""
    if not assessment_id:
        raise ValueError("assessment_id required")

    _ensure_table()
    token = secrets.token_hex(16)  # 32 hex chars
    expires_at = datetime.now(timezone.utc) + timedelta(hours=TOKEN_TTL_HOURS)

    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO charvak_anonymous_assessment_sessions
            (token, assessment_id, expires_at)
        VALUES (%s, %s, %s)
    """, (token, assessment_id, expires_at))
    conn.commit()
    cur.close()
    conn.close()
    return token


def resolve_token(token: str) -> dict:
    """
    Validate a token. Returns {assessment_id, placeholder_email, expires_at}.

    Raises ValueError if token is missing, malformed, not found, expired, or claimed.
    """
    if not token or not isinstance(token, str) or len(token) != 32:
        raise ValueError("invalid token format")

    _ensure_table()
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT assessment_id, expires_at, claimed_by_email
        FROM charvak_anonymous_assessment_sessions
        WHERE token = %s
    """, (token,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise ValueError("token not found")

    assessment_id, expires_at, claimed_by_email = row

    if claimed_by_email:
        raise ValueError("token already claimed")

    # Normalize to timezone-aware comparison
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise ValueError("token expired")

    return {
        "assessment_id": assessment_id,
        "placeholder_email": f"anon-{token}{PLACEHOLDER_SUFFIX}",
    }


def get_placeholder_email(token: str) -> str:
    """Convenience wrapper used by route handlers."""
    return resolve_token(token)["placeholder_email"]


def claim_token(token: str, email: str) -> dict:
    """
    Migrate the anonymous assessment to a real user's email.

    Idempotent: claiming an already-claimed token by the SAME email is a no-op.
    Raises ValueError if token is claimed by a different user, or not found.
    """
    email = (email or "").strip().lower()
    if not email:
        raise ValueError("email required")
    if not token or len(token) != 32:
        raise ValueError("invalid token format")

    _ensure_table()
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT assessment_id, claimed_by_email
        FROM charvak_anonymous_assessment_sessions
        WHERE token = %s
    """, (token,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        raise ValueError("token not found")

    assessment_id, claimed_by = row
    if claimed_by and claimed_by != email:
        cur.close()
        conn.close()
        raise ValueError("token already claimed by a different user")

    # Migrate the assessment's email if it's still a placeholder
    cur.execute("""
        UPDATE charvak_career_assessments
        SET email = %s
        WHERE assessment_id = %s
          AND email LIKE '%%@anon.charvak.local'
    """, (email, assessment_id))

    # Mark the token claimed
    cur.execute("""
        UPDATE charvak_anonymous_assessment_sessions
        SET claimed_by_email = %s, claimed_at = NOW()
        WHERE token = %s
    """, (email, token))

    conn.commit()
    cur.close()
    conn.close()

    return {"assessment_id": assessment_id, "email": email}