"""
Daily Drills + Streaks Engine (Session 47, Wave 1 of the flywheel)

Habit loop: one 5-question drill per day, per user. Streaks, credits,
passport score updates. Reuses career_assessment_engine for question
generation. Tracked credits get deposited later (same pattern as
share rewards).
"""

import os
import json
import secrets
import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from database import db

logger = logging.getLogger("charvakit.drills")

DRILL_QUESTIONS = 5
CREDITS_PER_DRILL = 2
MILESTONE_BONUSES = {7: 5, 30: 20, 100: 50}


# ---------------------------------------------------------------
# Topic selection
# ---------------------------------------------------------------

def _get_weakest_topic(email: str) -> Optional[str]:
    """Read latest readiness cert skill gap. Return the weakest topic name."""
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT payload_json FROM charvak_readiness_certificates
            WHERE email = %s AND payload_json IS NOT NULL
            ORDER BY created_at DESC LIMIT 1
        """, (email,))
        row = cur.fetchone()
        cur.close()
        if not row:
            return None
        payload = row[0]
        if isinstance(payload, str):
            payload = json.loads(payload)
        skill_gap = (payload or {}).get("skill_gap") or []
        # Sort weakest first (lowest score)
        weak = [s for s in skill_gap if isinstance(s, dict) and s.get("score") is not None]
        if not weak:
            return None
        weak.sort(key=lambda x: x["score"])
        return weak[0].get("topic") or None
    except Exception as e:
        logger.warning(f"_get_weakest_topic failed: {e}")
        return None
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


def _get_user_context(email: str) -> Dict:
    """Get role/industry/level from the most recent completed assessment or default."""
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT role, industry, level FROM charvak_career_assessments
            WHERE email = %s AND status = 'completed'
            ORDER BY completed_at DESC LIMIT 1
        """, (email,))
        row = cur.fetchone()
        cur.close()
        if row:
            return {"role": row[0], "industry": row[1], "level": row[2]}
    except Exception as e:
        logger.warning(f"_get_user_context failed: {e}")
    finally:
        if conn:
            try: conn.close()
            except Exception: pass
    return {
        "role": "Backend Engineer",
        "industry": "IT / Tech (general)",
        "level": "mid",
    }


def _pick_topic(email: str, role: str) -> str:
    """Weakest topic first, else role-based rotation."""
    weak = _get_weakest_topic(email)
    if weak:
        return weak
    # Rotation fallback
    try:
        from career_assessment_engine import _topic_vocabulary_for_role
        vocab = _topic_vocabulary_for_role(role)
        if vocab:
            idx = date.today().toordinal() % len(vocab)
            return vocab[idx]
    except Exception:
        pass
    return "General Knowledge"


# ---------------------------------------------------------------
# Question generation
# ---------------------------------------------------------------

def _generate_drill_questions(email: str, role: str, industry: str,
                               level: str, topic: str) -> List[Dict]:
    """Reuse career_assessment_engine's batch generator."""
    try:
        from career_assessment_engine import career_assessment_engine as cae
        # Get level label/blurb
        try:
            from career_assessment_engine import CAREER_LEVELS
            level_obj = next((l for l in CAREER_LEVELS if l["key"] == level.lower()), None)
            level_label = level_obj["label"] if level_obj else level
            level_blurb = level_obj["blurb"] if level_obj else ""
        except Exception:
            level_label = level
            level_blurb = ""

        raw = cae._generate_one_batch(
            format_key="mcq",
            role=role,
            industry=industry,
            level_key=level.lower(),
            level_label=level_label,
            level_blurb=level_blurb,
            count=DRILL_QUESTIONS,
            difficulty_hint="baseline",
        )
        # Normalize + strip answers for storage
        cleaned = []
        for raw_q in raw:
            q = cae._normalize_question("mcq", raw_q)
            if q:
                cleaned.append(q)
        if not cleaned:
            return []
        return cleaned[:DRILL_QUESTIONS]
    except Exception as e:
        logger.error(f"drill question generation failed: {e}")
        return []


# ---------------------------------------------------------------
# Today's drill
# ---------------------------------------------------------------

def get_or_create_today_drill(email: str) -> Dict:
    """Return today's drill for `email`. Creates if not exists. Idempotent per day."""
    email = (email or "").strip().lower()
    if not email:
        return {"status": "error", "message": "email required"}

    today = date.today()

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        # Check if drill exists
        cur.execute("""
            SELECT drill_id, topic, questions_json, completed, score, correct_count
            FROM charvak_daily_drills
            WHERE email = %s AND drill_date = %s
        """, (email, today))
        row = cur.fetchone()

        if row:
            drill_id, topic, questions_json, completed, score, correct_count = row
            if isinstance(questions_json, str):
                questions_json = json.loads(questions_json)
            # Strip correct_index for the client
            safe_qs = []
            for q in (questions_json or []):
                safe_qs.append({
                    "q": q.get("q"),
                    "options": q.get("options") or [],
                    "topics": q.get("topics") or [],
                })
            cur.close()
            return {
                "status": "success",
                "already_exists": True,
                "completed": bool(completed),
                "score": score,
                "correct_count": correct_count,
                "drill": {
                    "drill_id": drill_id,
                    "topic": topic,
                    "questions": safe_qs,
                    "total_questions": len(safe_qs),
                    "drill_date": today.isoformat(),
                },
            }

        # Create new drill
        ctx = _get_user_context(email)
        topic = _pick_topic(email, ctx["role"])
        questions = _generate_drill_questions(email, ctx["role"], ctx["industry"], ctx["level"], topic)
        if not questions:
            cur.close()
            return {"status": "error", "message": "Could not generate drill questions. Please try again."}

        drill_id = f"DRILL-{secrets.token_hex(6).upper()}"
        cur.execute("""
            INSERT INTO charvak_daily_drills
              (drill_id, email, drill_date, topic, role_context, industry_context,
               level_context, questions_json, total_questions)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
        """, (drill_id, email, today, topic, ctx["role"], ctx["industry"],
              ctx["level"], json.dumps(questions), len(questions)))
        conn.commit()
        cur.close()

        # Strip answers for the client
        safe_qs = [{"q": q.get("q"), "options": q.get("options") or [],
                    "topics": q.get("topics") or []} for q in questions]

        return {
            "status": "success",
            "already_exists": False,
            "completed": False,
            "drill": {
                "drill_id": drill_id,
                "topic": topic,
                "questions": safe_qs,
                "total_questions": len(safe_qs),
                "drill_date": today.isoformat(),
            },
        }
    except Exception as e:
        logger.error(f"get_or_create_today_drill failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


# ---------------------------------------------------------------
# Streak math
# ---------------------------------------------------------------

def _update_streak(email: str, drill_date: date,
                    total_drills: int = 0, total_correct: int = 0,
                    total_questions: int = 0) -> Dict:
    """
    Update streak on drill completion.
    Returns: {new_streak, longest, milestone_bonus, current_credits}
    """
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT current_streak, longest_streak, last_drill_date, streak_credits
            FROM charvak_user_streaks WHERE email = %s
        """, (email,))
        row = cur.fetchone()

        if row is None:
            current, longest, last_date, credits = 0, 0, None, 0
        else:
            current, longest, last_date, credits = row

        # Determine new streak
        if last_date is None:
            new_streak = 1
        elif last_date == drill_date:
            # Same day — don't change (idempotent protection)
            cur.close()
            return {"new_streak": current, "longest": longest,
                    "milestone_bonus": 0, "credits_earned": 0}
        elif last_date == drill_date - timedelta(days=1):
            new_streak = (current or 0) + 1
        else:
            new_streak = 1

        new_longest = max(longest or 0, new_streak)
        milestone_bonus = MILESTONE_BONUSES.get(new_streak, 0)
        total_credits_earned = CREDITS_PER_DRILL + milestone_bonus
        new_credits_total = (credits or 0) + total_credits_earned

        if row is None:
            # Session 47: first drill for this user — set counters to match this completion
            cur.execute("""
                INSERT INTO charvak_user_streaks
                  (email, current_streak, longest_streak, last_drill_date,
                   total_drills, total_correct, total_questions, streak_credits, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (email, new_streak, new_longest, drill_date,
                  total_drills or 0, total_correct or 0, total_questions or 0,
                  new_credits_total))
        else:
            cur.execute("""
                UPDATE charvak_user_streaks
                SET current_streak = %s,
                    longest_streak = %s,
                    last_drill_date = %s,
                    streak_credits = %s,
                    updated_at = NOW()
                WHERE email = %s
            """, (new_streak, new_longest, drill_date, new_credits_total, email))

        conn.commit()
        cur.close()
        return {
            "new_streak": new_streak,
            "longest": new_longest,
            "milestone_bonus": milestone_bonus,
            "credits_earned": total_credits_earned,
            "total_streak_credits": new_credits_total,
        }
    except Exception as e:
        logger.error(f"_update_streak failed: {e}")
        return {"new_streak": 0, "longest": 0, "milestone_bonus": 0, "credits_earned": 0}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


# ---------------------------------------------------------------
# Submit
# ---------------------------------------------------------------

def submit_drill(email: str, drill_id: str, answers: List) -> Dict:
    """Score the drill, update streak, track credits. Idempotent."""
    email = (email or "").strip().lower()
    if not email or not drill_id:
        return {"status": "error", "message": "email and drill_id required"}

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT drill_id, drill_date, questions_json, completed, score, correct_count
            FROM charvak_daily_drills
            WHERE drill_id = %s AND email = %s
        """, (drill_id, email))
        row = cur.fetchone()
        if not row:
            cur.close()
            return {"status": "error", "message": "Drill not found"}

        _, drill_date, questions_json, completed, score, correct_count = row
        if completed:
            cur.close()
            # Load current streak for the response
            streak_info = _get_streak_info(email)
            return {
                "status": "success",
                "already_completed": True,
                "score": score,
                "correct_count": correct_count,
                "streak": streak_info.get("current_streak", 0),
                "message": "You already completed today's drill",
            }

        if isinstance(questions_json, str):
            questions_json = json.loads(questions_json)
        total = len(questions_json or [])

        # Score
        correct = 0
        for i, q in enumerate(questions_json or []):
            user_ans = answers[i] if i < len(answers) else None
            correct_idx = q.get("correct_index")
            if isinstance(user_ans, int) and user_ans == correct_idx:
                correct += 1

        pct = int(round(100 * correct / total)) if total else 0

        # Update drill row
        cur.execute("""
            UPDATE charvak_daily_drills
            SET answers_json = %s::jsonb,
                score = %s,
                correct_count = %s,
                completed = TRUE,
                completed_at = NOW()
            WHERE drill_id = %s
        """, (json.dumps(answers), pct, correct, drill_id))

        # Update total counters on streak row
        cur.execute("""
            UPDATE charvak_user_streaks
            SET total_drills = total_drills + 1,
                total_correct = total_correct + %s,
                total_questions = total_questions + %s,
                updated_at = NOW()
            WHERE email = %s
        """, (correct, total, email))
        conn.commit()
        cur.close()

        # Update streak
        streak = _update_streak(email, drill_date, total_drills=1, total_correct=correct, total_questions=total)

        return {
            "status": "success",
            "already_completed": False,
            "score": pct,
            "correct_count": correct,
            "total_questions": total,
            "streak": streak["new_streak"],
            "longest_streak": streak["longest"],
            "milestone_bonus": streak["milestone_bonus"],
            "credits_earned": streak["credits_earned"],
        }
    except Exception as e:
        logger.error(f"submit_drill failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


# ---------------------------------------------------------------
# Streak stats
# ---------------------------------------------------------------

def _get_streak_info(email: str) -> Dict:
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT current_streak, longest_streak, last_drill_date,
                   total_drills, total_correct, total_questions, streak_credits
            FROM charvak_user_streaks WHERE email = %s
        """, (email,))
        row = cur.fetchone()
        cur.close()
        if not row:
            return {"current_streak": 0, "longest_streak": 0, "last_drill_date": None,
                    "total_drills": 0, "total_correct": 0, "total_questions": 0,
                    "streak_credits": 0, "accuracy_pct": 0}
        return {
            "current_streak": row[0],
            "longest_streak": row[1],
            "last_drill_date": row[2].isoformat() if row[2] else None,
            "total_drills": row[3],
            "total_correct": row[4],
            "total_questions": row[5],
            "streak_credits": row[6],
            "accuracy_pct": int(round(100 * row[4] / row[5])) if row[5] else 0,
        }
    except Exception as e:
        logger.warning(f"_get_streak_info failed: {e}")
        return {"current_streak": 0, "longest_streak": 0, "last_drill_date": None,
                "total_drills": 0, "total_correct": 0, "total_questions": 0,
                "streak_credits": 0, "accuracy_pct": 0}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


def get_streak_stats(email: str) -> Dict:
    """Return streak + recent drill history."""
    email = (email or "").strip().lower()
    if not email:
        return {"status": "error", "message": "email required"}

    stats = _get_streak_info(email)

    # Recent drills
    recent = []
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT drill_date, topic, score, correct_count, total_questions, completed
            FROM charvak_daily_drills
            WHERE email = %s
            ORDER BY drill_date DESC LIMIT 14
        """, (email,))
        for r in cur.fetchall():
            recent.append({
                "drill_date": r[0].isoformat() if r[0] else None,
                "topic": r[1],
                "score": r[2],
                "correct_count": r[3],
                "total_questions": r[4],
                "completed": bool(r[5]),
            })
        cur.close()
    except Exception as e:
        logger.warning(f"recent drills failed: {e}")
    finally:
        if conn:
            try: conn.close()
            except Exception: pass

    return {
        "status": "success",
        "streak": stats,
        "recent_drills": recent,
    }


drills_engine = None  # stateless


def __getattr__(name):
    import sys
    return sys.modules[__name__]