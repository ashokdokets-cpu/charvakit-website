#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pre-generate questions for Indian exams into charvak_exam_question_bank.
Uses exam_prep_engine.generate_questions - the same path users hit.

Idempotent, resumable, throttled. Writes only to the exam question bank.

Usage:
    python scripts/seed_exam_question_bank.py --phase 1              # top 10 (fast test)
    python scripts/seed_exam_question_bank.py --phase 2              # all Indian exams
    python scripts/seed_exam_question_bank.py --phase 2 --resume     # skip already-seeded pairs
    python scripts/seed_exam_question_bank.py --phase 2 --questions 30
"""
import argparse
import os
import sys
import time
from datetime import datetime

# Make repo root importable when run as "python scripts/seed_exam_question_bank.py"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exam_prep_engine import exam_prep_engine

# Top 10 Indian exams by likely traffic - used by --phase 1
PHASE_1_EXAMS = [
    "ssc_cgl", "ibps_po", "gate", "cat", "jee_main",
    "neet_pg", "cuet_ug", "afcat", "ssc_chsl", "ssc_mts",
]

QUESTIONS_PER_PAIR = 50
THROTTLE_SECONDS = 3


def collect_pairs(phase):
    """Return list of (exam_id, topic) tuples for the requested phase."""
    pairs = []
    for cat in exam_prep_engine.exams.values():
        for e in cat.get("exams", []):
            exam_id = e["id"]
            if phase == 1 and exam_id not in PHASE_1_EXAMS:
                continue
            for topic in e.get("sections", []):
                pairs.append((exam_id, topic))
    return pairs


def already_seeded(exam_id, topic):
    """Return count of existing questions for (exam_id, topic)."""
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM charvak_exam_question_bank
            WHERE exam_id = %s AND topic = %s
        """, (exam_id, topic))
        count = cur.fetchone()[0]
        cur.close(); conn.close()
        return count
    except Exception as e:
        print(f"  WARN: already_seeded check failed: {e}")
        return 0


def seed_one(exam_id, topic, count, resume):
    """Seed one (exam, topic). Returns (status, message)."""
    if resume:
        existing = already_seeded(exam_id, topic)
        if existing >= count:
            return "skip", f"already has {existing}"

    try:
        result = exam_prep_engine.generate_questions(exam_id, topic, count=count)
        if result.get("status") == "success":
            return "ok", f"generated {len(result.get('questions', []))}"
        return "fail", f"error: {result.get('message', 'unknown')}"
    except Exception as e:
        return "fail", f"exception: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", type=int, default=2, choices=[1, 2],
                    help="1 = top 10 exams, 2 = all Indian exams")
    ap.add_argument("--questions", type=int, default=QUESTIONS_PER_PAIR)
    ap.add_argument("--resume", action="store_true",
                    help="skip pairs that already have >= N questions")
    ap.add_argument("--throttle", type=float, default=THROTTLE_SECONDS)
    args = ap.parse_args()

    pairs = collect_pairs(args.phase)
    print(f"Phase {args.phase}: {len(pairs)} (exam, topic) pairs")
    print(f"Questions per pair: {args.questions}")
    print(f"Throttle: {args.throttle}s")
    print(f"Resume: {args.resume}")
    print()

    t0 = datetime.now()
    ok = skip = fail = 0

    for i, (exam_id, topic) in enumerate(pairs, 1):
        print(f"[{i}/{len(pairs)}] {exam_id}/{topic}", end=" ... ", flush=True)
        status, msg = seed_one(exam_id, topic, args.questions, args.resume)
        if status == "ok":
            ok += 1; print(f"OK ({msg})")
        elif status == "skip":
            skip += 1; print(f"SKIP ({msg})")
        else:
            fail += 1; print(f"FAIL ({msg})")
        if i < len(pairs):
            time.sleep(args.throttle)

    elapsed = (datetime.now() - t0).total_seconds()
    print()
    print(f"=== Done in {elapsed:.0f}s ===")
    print(f"  Succeeded: {ok}")
    print(f"  Skipped:   {skip}")
    print(f"  Failed:    {fail}")


if __name__ == "__main__":
    main()