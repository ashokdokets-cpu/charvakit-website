#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Charvak Question Validator (C13 Layer 1)

Deterministic structural checks against charvak_exam_question_bank.
Runs in seconds across the whole bank. No AI, no cost.

Checks:
  - correct_index in valid range
  - exactly 4 options
  - no duplicate options (normalized)
  - no empty options
  - question_text minimum length
  - explanation present
  - consistent option prefix style (all A./B. or none)

Modes:
  --report             show counts per exam/topic (no writes)
  --delete-invalid     delete failing rows

Usage:
  python scripts/validate_questions.py --report
  python scripts/validate_questions.py --delete-invalid
  python scripts/validate_questions.py --delete-invalid --exam ssc_cgl
"""
import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import psycopg2


def db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def normalize_option(o):
    return (o or "").strip().lower()


def has_prefix(o):
    """Return True if option looks like a real 'A. xxx' style prefix.

    Avoids false positives on Indian names like 'B. R. Ambedkar' or
    'C. Rajagopalachari' where the letter-dot sequence is an initial,
    not an option marker.
    """
    s = (o or "").strip()
    if len(s) < 4:
        return False
    if s[0].upper() not in "ABCD" or s[1] != ".":
        return False
    rest = s[2:].lstrip()
    if not rest:
        return False
    # If the word after the prefix starts with an uppercase letter followed
    # by a period (another initial like "R."), it's a name, not a prefix.
    if len(rest) >= 2 and rest[0].isupper() and rest[1] == ".":
        return False
    return True


def validate_question(q):
    """Return (ok: bool, reason: str)."""
    opts = q["options"]
    if not isinstance(opts, list):
        try:
            opts = json.loads(opts or "[]")
        except Exception:
            return False, "options_not_list"

    # 1. exactly 4 options
    if len(opts) != 4:
        return False, f"option_count_{len(opts)}"

    # 2. correct_index in range
    ci = q["correct_index"]
    if not isinstance(ci, int) or not (0 <= ci < 4):
        return False, f"correct_index_{ci}"

    # 3. no empty options
    if any(not (o or "").strip() for o in opts):
        return False, "empty_option"

    # 4. no duplicate options (case-insensitive, trimmed)
    norm = [normalize_option(o) for o in opts]
    if len(set(norm)) != 4:
        return False, "duplicate_options"

    # 5. question_text minimum length
    if len((q["question_text"] or "").strip()) < 15:
        return False, "question_too_short"

    # 6. explanation present
    expl = (q["explanation"] or "").strip()
    if len(expl) < 10:
        return False, "missing_explanation"

    # 7. prefix style check REMOVED (C13.1d)
    # Was producing false positives on options like "D. B. R. Ambedkar"
    # and "C. J.K. Rowling" where option prefix + person initial coexist.
    # The prefix style doesn't affect UX; users see text regardless.

    return True, "ok"


def fetch_questions(exam=None, topic=None):
    sql = """
        SELECT question_id, exam_id, topic, question_text, options,
               correct_index, explanation
        FROM charvak_exam_question_bank
    """
    params = []
    clauses = []
    if exam:
        clauses.append("exam_id = %s")
        params.append(exam)
    if topic:
        clauses.append("topic = %s")
        params.append(topic)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)

    conn = db()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="Show counts, no writes")
    ap.add_argument("--delete-invalid", action="store_true", help="Delete invalid rows")
    ap.add_argument("--exam", default=None, help="Filter by exam_id")
    ap.add_argument("--topic", default=None, help="Filter by topic")
    args = ap.parse_args()

    if not (args.report or args.delete_invalid):
        print("Specify --report or --delete-invalid")
        return

    print(f"\nFetching questions (exam={args.exam or 'any'}, topic={args.topic or 'any'})...")
    rows = fetch_questions(args.exam, args.topic)
    print(f"Loaded {len(rows)} questions.\n")

    valid_ids = []
    invalid_by_reason = Counter()
    invalid_details = []

    for r in rows:
        q = {
            "question_id": r[0],
            "exam_id": r[1],
            "topic": r[2],
            "question_text": r[3],
            "options": r[4],
            "correct_index": r[5],
            "explanation": r[6],
        }
        ok, reason = validate_question(q)
        if ok:
            valid_ids.append(q["question_id"])
        else:
            invalid_by_reason[reason] += 1
            invalid_details.append((q["question_id"], q["exam_id"], q["topic"], reason, q["question_text"][:60]))

    print("=" * 72)
    print(f"VALID:   {len(valid_ids)}")
    print(f"INVALID: {len(invalid_details)}")
    print("=" * 72)

    if invalid_by_reason:
        print("\nFailure reasons:")
        for reason, count in invalid_by_reason.most_common():
            print(f"  {reason:<35} {count}")

    if args.report and invalid_details:
        print("\nSample invalid questions (first 15):")
        for qid, exam, topic, reason, snippet in invalid_details[:15]:
            print(f"  [{qid[:12]}] {exam}/{topic} — {reason}")
            print(f"    Q: {snippet}")

    # C13.1c - define which failure reasons count as true defects
    TRUE_DEFECTS = {
        "option_count_5",
        "option_count_3",
        "option_count_2",
        "option_count_8",
        "correct_index_out_of_range",
        "empty_option",
        "duplicate_options",
        "question_too_short",
    }

    if args.delete_invalid and invalid_details:
        invalid_ids = [
            d[0] for d in invalid_details
            if d[3].startswith("correct_index_")
               or d[3].startswith("option_count_")
               or d[3] in TRUE_DEFECTS
        ]
        skipped = len(invalid_details) - len(invalid_ids)
        if skipped:
            print(f"\n  Skipping {skipped} non-defect issues (mixed prefix / missing explanation)")
        print(f"\nDeleting {len(invalid_ids)} invalid questions...")
        conn = db()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM charvak_exam_question_bank WHERE question_id = ANY(%s)",
            (invalid_ids,)
        )
        deleted = cur.rowcount
        cur.close()
        conn.close()
        print(f"  ✅ Deleted {deleted} rows")

    print("\nDone.")


if __name__ == "__main__":
    main()