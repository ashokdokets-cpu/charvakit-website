# question_rotator.py
# Session 103b: Prevent question copying across attempts.
#
# Function: given a user + assessment context, fetch prior questions,
# hash them, and help the AI exclude them from the next batch.

import hashlib
import json
from typing import Dict, List, Set, Tuple


def hash_question_text(question_text: str) -> str:
    """Stable hash of question text. Normalized for case/whitespace."""
    if not question_text:
        return ""
    normalized = " ".join(question_text.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def get_prior_question_hashes(
    email: str, role: str, industry: str, level: str, fmt: str
) -> Set[str]:
    """
    Return set of question hashes from ALL prior attempts by this user
    for the same (role, industry, level, format).
    """
    email = (email or "").strip().lower()
    if not email:
        return set()

    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT questions_json FROM charvak_career_assessments
            WHERE LOWER(email) = %s AND role = %s AND industry = %s
              AND level = %s AND format = %s
              AND questions_json IS NOT NULL
        """, (email, role, industry, level, fmt))

        hashes: Set[str] = set()
        for row in cur.fetchall():
            questions = row[0]
            if isinstance(questions, str):
                try:
                    questions = json.loads(questions)
                except Exception:
                    continue
            if not isinstance(questions, list):
                continue
            for q in questions:
                if isinstance(q, dict):
                    text = q.get("q") or q.get("question") or q.get("scenario") or ""
                    h = hash_question_text(text)
                    if h:
                        hashes.add(h)

        cur.close()
        conn.close()
        return hashes
    except Exception:
        return set()


def build_exclude_prompt_snippet(prior_hashes: Set[str]) -> str:
    """
    Build a prompt-block string that instructs the AI to avoid
    reproducing prior questions.
    """
    if not prior_hashes:
        return ""

    sample = list(prior_hashes)[:20]

    return f"""
IMPORTANT — FRESH QUESTIONS REQUIRED:

This candidate has already attempted this assessment {len(prior_hashes)}
question(s) previously. You MUST generate entirely NEW questions that
test the same skills from different angles.

Rules:
- Do NOT reproduce any question similar to the hashes below
- Same skill area is fine; same wording is NOT
- Vary scenarios, numbers, and framing
- Test the same competency from a fresh angle

Prior question hashes to exclude (first 20):
{', '.join(sample)}

Generate {len(sample) if sample else 'fresh'} unique questions that
do NOT duplicate these.
"""


def detect_duplicates(new_questions: List[Dict], prior_hashes: Set[str]) -> List[Dict]:
    """Return list of new questions that are duplicates of prior ones."""
    if not prior_hashes or not new_questions:
        return []

    duplicates = []
    for q in new_questions:
        if not isinstance(q, dict):
            continue
        text = q.get("q") or q.get("question") or q.get("scenario") or ""
        h = hash_question_text(text)
        if h in prior_hashes:
            duplicates.append({"q": text, "hash": h})
    return duplicates


def remove_duplicates(
    new_questions: List[Dict], prior_hashes: Set[str]
) -> Tuple[List[Dict], int]:
    """Remove duplicates, return (clean_list, count_removed)."""
    if not prior_hashes or not new_questions:
        return (new_questions, 0)

    clean = []
    removed = 0
    for q in new_questions:
        if not isinstance(q, dict):
            clean.append(q)
            continue
        text = q.get("q") or q.get("question") or q.get("scenario") or ""
        h = hash_question_text(text)
        if h in prior_hashes:
            removed += 1
            continue
        clean.append(q)

    return (clean, removed)