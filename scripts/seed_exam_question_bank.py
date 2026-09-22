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


def collect_pairs(phase, exam_filter=None):
    """Return list of (exam_id, topic) tuples for the requested phase.

    exam_filter: optional set of exam_ids to restrict to. If provided,
    overrides phase selection (still skips exams not in the catalog).
    """
    pairs = []
    for cat in exam_prep_engine.exams.values():
        for e in cat.get("exams", []):
            exam_id = e["id"]
            if exam_filter is not None:
                if exam_id not in exam_filter:
                    continue
            elif phase == 1 and exam_id not in PHASE_1_EXAMS:
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


def dedup_bank(exam_id, topic, threshold=0.15):
    """Delete near-duplicate questions for one (exam, topic).

    Uses pgvector cosine distance on the embedding column. Keeps the
    lowest question_id per semantic cluster. Idempotent.
    """
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM charvak_exam_question_bank t
            WHERE t.exam_id = %s AND t.topic = %s
              AND t.embedding IS NOT NULL
              AND EXISTS (
                  SELECT 1 FROM charvak_exam_question_bank k
                  WHERE k.exam_id = t.exam_id
                    AND k.topic = t.topic
                    AND k.embedding IS NOT NULL
                    AND k.question_id < t.question_id
                    AND k.embedding <=> t.embedding < %s
              )
        """, (exam_id, topic, threshold))
        deleted = cur.rowcount
        conn.commit()
        cur.close(); conn.close()
        return deleted
    except Exception as e:
        print(f"  WARN: dedup failed: {e}")
        return 0


def seed_one(exam_id, topic, count, resume):
    """Seed one (exam, topic). Returns (status, message)."""
    if resume:
        existing = already_seeded(exam_id, topic)
        if existing >= count:
            return "skip", f"already has {existing}"

    try:
        result = exam_prep_engine.generate_questions(exam_id, topic, count=count)
        if result.get("status") != "success":
            return "fail", f"error: {result.get('message', 'unknown')}"
        generated = len(result.get("questions", []))
        deleted = dedup_bank(exam_id, topic)
        if deleted:
            return "ok", f"generated {generated}, deduped {deleted}"
        return "ok", f"generated {generated}"
    except Exception as e:
        return "fail", f"exception: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", type=int, default=2, choices=[1, 2],
                    help="1 = top 10 exams, 2 = all Indian exams")
    ap.add_argument("--exam", type=str, default=None,
                    help="Comma-separated exam_ids to seed (overrides --phase). "
                         "Example: --exam upsc_prelims,neet_ug")
    ap.add_argument("--questions", type=int, default=QUESTIONS_PER_PAIR)
    ap.add_argument("--resume", action="store_true",
                    help="skip pairs that already have >= N questions")
    ap.add_argument("--throttle", type=float, default=THROTTLE_SECONDS)
    args = ap.parse_args()

    exam_filter = None
    if args.exam:
        exam_filter = {x.strip() for x in args.exam.split(",") if x.strip()}
        print(f"Exam filter: {sorted(exam_filter)}")

    pairs = collect_pairs(args.phase, exam_filter=exam_filter)

    if exam_filter and not pairs:
        print(f"WARNING: no (exam, topic) pairs matched filter {exam_filter}")
        print("Available exam_ids with matching prefix:")
        for cat in exam_prep_engine.exams.values():
            for e in cat.get("exams", []):
                if any(e["id"].startswith(f[:5]) for f in exam_filter):
                    print(f"  - {e['id']}")
        sys.exit(1)
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