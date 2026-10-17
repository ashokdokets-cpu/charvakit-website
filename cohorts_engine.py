"""
Session 48: Cohort Mode engine.

Batch leaderboards for college cohorts, coaching groups, and corporate
training batches. The atomic viral unit in India is not the individual,
it is the batch.

Design principles:
  - Composite score = passport.score*0.6 + streak*5 + weekly_drills*10
    (fast query, one row per member, no N+1)
  - Weekly reset via ISO week Monday. Lazy refresh on read.
  - Public leaderboard read (shareable). Write requires auth.
  - Join code = 8 chars, no ambiguous characters (0/O, 1/I/L).
  - Self-healing DDL: _ensure_tables() creates on first use.

Reused signals:
  - charvak_passports.charvak_score        (identity)
  - charvak_user_streaks.current_streak    (habit)
  - charvak_daily_drills this ISO week     (engagement)
"""

import logging
import secrets
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from database import db

logger = logging.getLogger("charvakit.cohorts")

# Characters that are visually unambiguous (no 0/O, 1/I/L)
_JOIN_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def _ensure_tables() -> None:
    """Self-healing DDL. Safe to call on every request."""
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charvak_cohorts (
                cohort_id       TEXT PRIMARY KEY,
                name            TEXT NOT NULL,
                description     TEXT DEFAULT '',
                join_code       TEXT NOT NULL UNIQUE,
                created_by      TEXT NOT NULL,
                member_count    INTEGER NOT NULL DEFAULT 1,
                is_public       BOOLEAN NOT NULL DEFAULT FALSE,
                created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_refresh    TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charvak_cohort_members (
                cohort_id       TEXT NOT NULL,
                member_email    TEXT NOT NULL,
                role            TEXT NOT NULL DEFAULT 'member',
                joined_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (cohort_id, member_email)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charvak_cohort_leaderboard (
                cohort_id       TEXT NOT NULL,
                member_email    TEXT NOT NULL,
                composite_score INTEGER NOT NULL,
                rank            INTEGER NOT NULL,
                week_start      DATE NOT NULL,
                refreshed_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (cohort_id, member_email, week_start)
            )
        """)
        conn.commit()
        cur.close()
    except Exception as e:
        logger.warning(f"_ensure_tables: {e}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _week_start_iso(today: Optional[date] = None) -> date:
    """Return the Monday of the current ISO week."""
    d = today or date.today()
    return d - timedelta(days=d.weekday())


def _generate_join_code(cur) -> str:
    """Generate a unique 8-char join code. Retries on collision."""
    for _ in range(10):
        code = "".join(secrets.choice(_JOIN_ALPHABET) for _ in range(8))
        cur.execute(
            "SELECT 1 FROM charvak_cohorts WHERE join_code = %s LIMIT 1",
            (code,),
        )
        if not cur.fetchone():
            return code
    # Fallback: fully random, highly unlikely to collide
    return "".join(secrets.choice(_JOIN_ALPHABET) for _ in range(10))


def _generate_cohort_id() -> str:
    """Generate a cohort id with a recognizable prefix."""
    return f"COH-{secrets.token_hex(6).upper()}"


# ---------------------------------------------------------------
# Public API
# ---------------------------------------------------------------

def create_cohort(creator_email: str, name: str, description: str = "") -> Dict:
    """Create a cohort. Creator becomes the owner + first member."""
    creator_email = (creator_email or "").strip().lower()
    name = (name or "").strip()[:80]
    description = (description or "").strip()[:300]

    if not creator_email:
        return {"status": "error", "message": "creator_email required"}
    if not name:
        return {"status": "error", "message": "name required"}
    if len(name) < 3:
        return {"status": "error", "message": "name must be at least 3 characters"}

    _ensure_tables()

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        cohort_id = _generate_cohort_id()
        join_code = _generate_join_code(cur)

        cur.execute("""
            INSERT INTO charvak_cohorts
                (cohort_id, name, description, join_code, created_by, member_count)
            VALUES (%s, %s, %s, %s, %s, 1)
        """, (cohort_id, name, description, join_code, creator_email))

        cur.execute("""
            INSERT INTO charvak_cohort_members (cohort_id, member_email, role)
            VALUES (%s, %s, 'owner')
        """, (cohort_id, creator_email))

        conn.commit()
        cur.close()

        return {
            "status": "success",
            "cohort_id": cohort_id,
            "join_code": join_code,
            "join_url": f"/cohorts/join/{join_code}",
            "cohort_url": f"/cohorts/{cohort_id}",
        }
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        logger.warning(f"create_cohort: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def join_by_code(join_code: str, member_email: str) -> Dict:
    """Join a cohort via its share code. Idempotent - re-join returns success."""
    join_code = (join_code or "").strip().upper()
    member_email = (member_email or "").strip().lower()

    if not join_code:
        return {"status": "error", "message": "join_code required"}
    if not member_email:
        return {"status": "error", "message": "member_email required"}

    _ensure_tables()

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT cohort_id, name, member_count FROM charvak_cohorts WHERE join_code = %s",
            (join_code,),
        )
        row = cur.fetchone()
        if not row:
            cur.close()
            return {"status": "error", "message": "Invalid join code", "code": "invalid_code"}

        cohort_id, cohort_name, member_count = row

        # Idempotent re-join
        cur.execute("""
            SELECT 1 FROM charvak_cohort_members
            WHERE cohort_id = %s AND member_email = %s
        """, (cohort_id, member_email))
        if cur.fetchone():
            cur.close()
            return {
                "status": "success",
                "cohort_id": cohort_id,
                "cohort_name": cohort_name,
                "already_member": True,
            }

        # Insert member + bump count
        cur.execute("""
            INSERT INTO charvak_cohort_members (cohort_id, member_email, role)
            VALUES (%s, %s, 'member')
        """, (cohort_id, member_email))
        cur.execute("""
            UPDATE charvak_cohorts
            SET member_count = member_count + 1
            WHERE cohort_id = %s
        """, (cohort_id,))

        conn.commit()
        cur.close()

        return {
            "status": "success",
            "cohort_id": cohort_id,
            "cohort_name": cohort_name,
            "already_member": False,
        }
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        logger.warning(f"join_by_code: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _compute_leaderboard(cohort_id: str, week_start: date) -> List[Dict]:
    """Compute leaderboard from live signals. One query, then Python ranking."""
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        # One query for all members + passport + streak + weekly drills
        cur.execute("""
            SELECT
                m.member_email,
                m.role,
                COALESCE(p.charvak_score, 0)           AS passport_score,
                COALESCE(p.handle, '')                 AS handle,
                COALESCE(p.display_name, '')           AS display_name,
                COALESCE(s.current_streak, 0)          AS streak,
                COALESCE(d.weekly_drills, 0)           AS weekly_drills
            FROM charvak_cohort_members m
            LEFT JOIN charvak_passports p
                ON p.email = m.member_email
            LEFT JOIN charvak_user_streaks s
                ON s.email = m.member_email
            LEFT JOIN (
                SELECT email, COUNT(*) AS weekly_drills
                FROM charvak_daily_drills
                WHERE drill_date >= %s AND completed = TRUE
                GROUP BY email
            ) d ON d.email = m.member_email
            WHERE m.cohort_id = %s
        """, (week_start, cohort_id))

        rows = cur.fetchall()
        cur.close()

        members = []
        for email, role, passport_score, handle, display_name, streak, weekly in rows:
            # Composite formula (weights documented in module docstring)
            composite = (
                int(passport_score * 0.6)
                + min(int(streak) * 5, 100)
                + min(int(weekly) * 10, 150)
            )
            members.append({
                "email": email,
                "role": role,
                "handle": handle,
                "display_name": display_name or (email.split("@")[0] if "@" in email else email),
                "passport_score": int(passport_score),
                "streak": int(streak),
                "weekly_drills": int(weekly),
                "composite_score": composite,
            })

        # Sort by composite descending, then by passport score descending (tiebreak)
        members.sort(key=lambda m: (-m["composite_score"], -m["passport_score"], m["email"]))

        for i, m in enumerate(members, start=1):
            m["rank"] = i

        return members
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def get_leaderboard(cohort_id: str, limit: int = 100) -> Dict:
    """Return the current-week leaderboard, cached in DB."""
    cohort_id = (cohort_id or "").strip()
    if not cohort_id:
        return {"status": "error", "message": "cohort_id required"}

    _ensure_tables()

    week_start = _week_start_iso()

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        # Fetch cohort meta
        cur.execute("""
            SELECT name, description, join_code, member_count, created_by
            FROM charvak_cohorts WHERE cohort_id = %s
        """, (cohort_id,))
        row = cur.fetchone()
        if not row:
            cur.close()
            return {"status": "error", "message": "Cohort not found", "code": "not_found"}

        name, description, join_code, member_count, created_by = row
        cur.close()

        # Try cache
        cur2 = conn.cursor()
        cur2.execute("""
            SELECT member_email, composite_score, rank
            FROM charvak_cohort_leaderboard
            WHERE cohort_id = %s AND week_start = %s
            ORDER BY rank ASC
        """, (cohort_id, week_start))
        cached = cur2.fetchall()
        cur2.close()

        if cached:
            # Cache hit: enrich with display info
            entries = []
            cur3 = conn.cursor()
            for email, composite, rank in cached:
                cur3.execute("""
                    SELECT COALESCE(handle, ''), COALESCE(display_name, '')
                    FROM charvak_passports WHERE email = %s
                """, (email,))
                p = cur3.fetchone()
                handle, display_name = p if p else ("", "")
                cur3.execute("""
                    SELECT COALESCE(current_streak, 0) FROM charvak_user_streaks WHERE email = %s
                """, (email,))
                s = cur3.fetchone()
                streak = s[0] if s else 0
                entries.append({
                    "email": email,
                    "handle": handle,
                    "display_name": display_name or email.split("@")[0],
                    "composite_score": composite,
                    "streak": int(streak),
                    "rank": rank,
                })
            cur3.close()

            return {
                "status": "success",
                "cohort_id": cohort_id,
                "name": name,
                "description": description,
                "join_code": join_code,
                "member_count": member_count,
                "week_start": week_start.isoformat(),
                "cached": True,
                "entries": entries[:limit],
            }

        # Cache miss: compute fresh
        members = _compute_leaderboard(cohort_id, week_start)

        # Persist cache
        if members:
            cur4 = conn.cursor()
            try:
                for m in members:
                    cur4.execute("""
                        INSERT INTO charvak_cohort_leaderboard
                            (cohort_id, member_email, composite_score, rank, week_start)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (cohort_id, member_email, week_start)
                        DO UPDATE SET
                            composite_score = EXCLUDED.composite_score,
                            rank = EXCLUDED.rank,
                            refreshed_at = CURRENT_TIMESTAMP
                    """, (cohort_id, m["email"], m["composite_score"], m["rank"], week_start))

                cur4.execute("""
                    UPDATE charvak_cohorts SET last_refresh = CURRENT_TIMESTAMP
                    WHERE cohort_id = %s
                """, (cohort_id,))
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.warning(f"leaderboard cache write failed: {e}")
            finally:
                cur4.close()

        return {
            "status": "success",
            "cohort_id": cohort_id,
            "name": name,
            "description": description,
            "join_code": join_code,
            "member_count": member_count,
            "week_start": week_start.isoformat(),
            "cached": False,
            "entries": members[:limit],
        }
    except Exception as e:
        logger.warning(f"get_leaderboard: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def list_my_cohorts(email: str) -> Dict:
    """Return all cohorts the caller belongs to, with their rank."""
    email = (email or "").strip().lower()
    if not email:
        return {"status": "error", "message": "email required"}

    _ensure_tables()

    week_start = _week_start_iso()

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT c.cohort_id, c.name, c.description, c.join_code,
                   c.member_count, m.role, c.created_at
            FROM charvak_cohorts c
            JOIN charvak_cohort_members m ON m.cohort_id = c.cohort_id
            WHERE m.member_email = %s
            ORDER BY c.created_at DESC
        """, (email,))
        rows = cur.fetchall()
        cur.close()

        cohorts = []
        for cohort_id, name, description, join_code, member_count, role, created_at in rows:
            # Fetch cached rank if available
            cur2 = conn.cursor()
            cur2.execute("""
                SELECT rank, composite_score FROM charvak_cohort_leaderboard
                WHERE cohort_id = %s AND member_email = %s AND week_start = %s
            """, (cohort_id, email, week_start))
            rank_row = cur2.fetchone()
            cur2.close()

            rank = rank_row[0] if rank_row else None
            composite = rank_row[1] if rank_row else None

            cohorts.append({
                "cohort_id": cohort_id,
                "name": name,
                "description": description,
                "join_code": join_code,
                "member_count": member_count,
                "role": role,
                "my_rank": rank,
                "my_score": composite,
                "created_at": created_at.isoformat() if created_at else None,
            })

        return {"status": "success", "cohorts": cohorts}
    except Exception as e:
        logger.warning(f"list_my_cohorts: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def refresh_leaderboard(cohort_id: str, caller_email: str) -> Dict:
    """Force-refresh leaderboard. Caller must be owner or admin."""
    cohort_id = (cohort_id or "").strip()
    caller_email = (caller_email or "").strip().lower()

    if not cohort_id or not caller_email:
        return {"status": "error", "message": "cohort_id and caller_email required"}

    _ensure_tables()

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        # Verify caller is owner or admin
        cur.execute("""
            SELECT role FROM charvak_cohort_members
            WHERE cohort_id = %s AND member_email = %s
        """, (cohort_id, caller_email))
        row = cur.fetchone()
        if not row or row[0] not in ("owner", "admin"):
            cur.close()
            return {"status": "error", "message": "Owner or admin only", "code": "forbidden"}

        cur.close()

        # Force recompute by deleting current-week cache then calling get_leaderboard
        cur2 = conn.cursor()
        cur2.execute("""
            DELETE FROM charvak_cohort_leaderboard
            WHERE cohort_id = %s AND week_start = %s
        """, (cohort_id, _week_start_iso()))
        conn.commit()
        cur2.close()

        return get_leaderboard(cohort_id)
    except Exception as e:
        logger.warning(f"refresh_leaderboard: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass