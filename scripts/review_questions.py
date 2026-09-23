#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Charvak Question Review CLI (C13.4)

Interactive approval workflow for charvak_exam_question_bank.

Usage:
    python scripts/review_questions.py --exam ssc_cgl --topic Reasoning --limit 30
    python scripts/review_questions.py --exam uppsc_pcs --topic "UP Special" --random
    python scripts/review_questions.py --exam cat                  # all topics
    python scripts/review_questions.py --topic General             # all exams

Actions:
    [a]pprove  — mark reviewed = TRUE
    [r]eject   — DELETE from bank
    [e]dit     — edit question text / options / correct / explanation
    [s]kip     — leave unreviewed, move on
    [b]ack     — show previous question again (no state change)
    [q]uit     — save progress and exit

Safe: Ctrl+C exits gracefully. Approvals are committed one at a time.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import psycopg2


def db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


# ---------- fetching ----------
def fetch_unreviewed(exam, topic, limit, randomize, reported_only=False):
    sql = """
        SELECT question_id, exam_id, topic, question_text, options,
               correct_index, explanation, difficulty, generated_by, created_at,
               reported, report_reason, reported_by
        FROM charvak_exam_question_bank
        WHERE reviewed = FALSE
    """
    params = []
    if reported_only:
        sql = sql.replace("WHERE reviewed = FALSE", "WHERE reported = TRUE")
    if exam:
        sql += " AND exam_id = %s"
        params.append(exam)
    if topic:
        sql += " AND topic = %s"
        params.append(topic)
    sql += " ORDER BY " + ("RANDOM()" if randomize else "created_at")
    sql += " LIMIT %s"
    params.append(limit)

    conn = db()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    out = []
    for r in rows:
        out.append({
            "question_id": r[0],
            "exam_id": r[1],
            "topic": r[2],
            "question_text": r[3],
            "options": r[4] if isinstance(r[4], list) else json.loads(r[4] or "[]"),
            "correct_index": r[5],
            "explanation": r[6],
            "difficulty": r[7],
            "generated_by": r[8],
            "created_at": r[9].isoformat() if r[9] else None,
            "reported": r[10] if len(r) > 10 else False,
            "report_reason": r[11] if len(r) > 11 else None,
            "reported_by": r[12] if len(r) > 12 else None,
        })
    return out


# ---------- actions ----------
def approve(qid):
    conn = db()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""
        UPDATE charvak_exam_question_bank
        SET reviewed = TRUE, reviewed_at = NOW()
        WHERE question_id = %s
    """, (qid,))
    cur.close()
    conn.close()


def reject(qid):
    conn = db()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DELETE FROM charvak_exam_question_bank WHERE question_id = %s", (qid,))
    cur.close()
    conn.close()


def update_question(qid, qtext, options, correct_idx, explanation):
    conn = db()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""
        UPDATE charvak_exam_question_bank
        SET question_text = %s,
            options = %s::jsonb,
            correct_index = %s,
            explanation = %s,
            reviewed = TRUE,
            reviewed_at = NOW(),
            reviewer_notes = COALESCE(reviewer_notes, '') || ' [edited]'
        WHERE question_id = %s
    """, (qtext, json.dumps(options), correct_idx, explanation, qid))
    cur.close()
    conn.close()


# ---------- display ----------
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def show(q, idx, total):
    clear()
    print("=" * 72)
    print(f"  [{idx}/{total}]   {q['exam_id']}  /  {q['topic']}   [id: {q['question_id']}]")
    print("=" * 72)
    print()
    print(f"  Q: {q['question_text']}")
    print()
    for i, opt in enumerate(q["options"]):
        marker = "  ← correct" if i == q["correct_index"] else ""
        print(f"    [{i + 1}] {opt}{marker}")
    print()
    if q.get("explanation"):
        print(f"  Explanation: {q['explanation']}")
        print()
    print(f"  Difficulty: {q.get('difficulty') or '-'}  |  Source: {q.get('generated_by') or '-'}  |  Created: {(q.get('created_at') or '-')[:19]}")
    if q.get("reported"):
        print()
        print(f"  ⚠ REPORTED by {q.get('reported_by') or 'anonymous'}")
        print(f"    Reason: {q.get('report_reason') or '(no reason given)'}")
    print()
    print("-" * 72)
    print("  [a]pprove   [r]eject   [e]dit   [s]kip   [b]ack   [q]uit")
    print("-" * 72)


# ---------- edit ----------
def edit_inline(q):
    """Edit question text, options, correct index, explanation."""
    print()
    print("EDIT MODE  (press Enter to keep current value)")
    print()

    new_text = input(f"  Question [{q['question_text'][:60]}...]:\n  > ").strip()
    if new_text:
        q["question_text"] = new_text

    new_options = []
    for i, opt in enumerate(q["options"]):
        raw = input(f"  Option {i + 1} [{opt}]:\n  > ").strip()
        new_options.append(raw if raw else opt)
    q["options"] = new_options

    correct = input(f"  Correct index (0-based) [{q['correct_index']}]:\n  > ").strip()
    if correct.isdigit() and 0 <= int(correct) < len(new_options):
        q["correct_index"] = int(correct)

    new_expl = input(f"  Explanation [{q.get('explanation', '')[:60]}]:\n  > ").strip()
    if new_expl:
        q["explanation"] = new_expl

    print()
    print("  Saving edited question...")
    update_question(
        q["question_id"],
        q["question_text"],
        q["options"],
        q["correct_index"],
        q.get("explanation", ""),
    )
    print("  ✅ Saved + approved")


# ---------- main loop ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exam", default=None, help="Filter by exam_id (exact match)")
    ap.add_argument("--topic", default=None, help="Filter by topic (exact match)")
    ap.add_argument("--limit", type=int, default=20, help="Max questions to review (default 20)")
    ap.add_argument("--random", action="store_true", help="Randomize order")
    ap.add_argument("--reported", action="store_true", help="Only show user-reported questions")
    args = ap.parse_args()

    mode = "user-reported" if args.reported else "unreviewed"
    print(f"\nFetching {mode} questions (exam={args.exam or 'any'}, topic={args.topic or 'any'}, limit={args.limit})...")
    questions = fetch_unreviewed(args.exam, args.topic, args.limit, args.random, reported_only=args.reported)

    if not questions:
        print("\nNo unreviewed questions found for the given filters.")
        print("Try different filters, or seed new questions first.\n")
        return

    print(f"Loaded {len(questions)} questions. Starting review...\n")
    input("Press Enter to begin...")

    approved = 0
    rejected = 0
    skipped = 0
    edited = 0

    idx = 0
    while idx < len(questions):
        q = questions[idx]
        show(q, idx + 1, len(questions))

        try:
            choice = input("  > ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Interrupted. Progress saved (approvals committed so far).")
            print(f"  Approved: {approved}  Rejected: {rejected}  Skipped: {skipped}  Edited: {edited}\n")
            return

        if choice == "a":
            approve(q["question_id"])
            approved += 1
            idx += 1
        elif choice == "r":
            confirm = input(f"  Delete {q['question_id']}? [y/N] > ").strip().lower()
            if confirm == "y":
                reject(q["question_id"])
                rejected += 1
                idx += 1
        elif choice == "e":
            edit_inline(q)
            edited += 1
            idx += 1
        elif choice == "s":
            skipped += 1
            idx += 1
        elif choice == "b":
            if idx > 0:
                idx -= 1
        elif choice == "q":
            print(f"\n  Quitting.\n  Approved: {approved}  Rejected: {rejected}  Skipped: {skipped}  Edited: {edited}\n")
            return
        else:
            print("  Unknown command. Try again.")

    print(f"\n  ✅ Review session complete.")
    print(f"     Approved: {approved}")
    print(f"     Rejected: {rejected}")
    print(f"     Skipped:  {skipped}")
    print(f"     Edited:   {edited}\n")


if __name__ == "__main__":
    main()