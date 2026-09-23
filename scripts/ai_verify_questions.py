#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Charvak AI Question Verifier (C13 Layer 2)

Batches questions to OpenAI gpt-4o-mini and asks it to verify each one:
  - correct_index points to a genuinely correct answer
  - explanation consistent with the correct answer
  - question is clear, unambiguous, no nonsense
  - no duplicate/nonsensical options
  - numeric facts / dates correct

Modes:
  --report              dry run (no writes, counts only)
  --apply               mark "ok" as reviewed=TRUE, log bad IDs
  --apply --delete-bad  additionally DELETE bad questions
  --limit N             process at most N questions (default: all unreviewed)
  --batch-size N        questions per OpenAI call (default: 20)

Usage:
  python scripts/ai_verify_questions.py --report --limit 100
  python scripts/ai_verify_questions.py --apply --limit 100
  python scripts/ai_verify_questions.py --apply --delete-bad
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import psycopg2
import requests


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = "gpt-4o-mini"


def db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def fetch_unreviewed(limit=None, exam=None):
    sql = """
        SELECT question_id, exam_id, topic, question_text, options,
               correct_index, explanation, difficulty
        FROM charvak_exam_question_bank
        WHERE reviewed = FALSE
    """
    params = []
    if exam:
        sql += " AND exam_id = %s"
        params.append(exam)
    sql += " ORDER BY exam_id, topic, created_at"
    if limit:
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
        opts = r[4] if isinstance(r[4], list) else json.loads(r[4] or "[]")
        out.append({
            "question_id": r[0],
            "exam_id": r[1],
            "topic": r[2],
            "question_text": r[3],
            "options": opts,
            "correct_index": r[5],
            "explanation": r[6] or "",
            "difficulty": r[7],
        })
    return out


def build_prompt(batch):
    items = []
    for q in batch:
        items.append({
            "id": q["question_id"],
            "q": q["question_text"],
            "opts": q["options"],
            "correct": q["correct_index"],
            "expl": q["explanation"],
        })

    prompt = (
        "You are a strict quality reviewer for a multiple-choice question bank "
        "for Indian competitive exams (SSC, UPSC, CAT, JEE, NEET, bank exams, etc.).\n\n"
        "For each question below, evaluate:\n"
        "  1. correct_index points to a genuinely correct answer (index is 0-based).\n"
        "  2. The explanation (if present) is consistent with the correct answer.\n"
        "  3. The question is clear, meaningful, and not nonsense.\n"
        "  4. Options are distinct, non-empty, and plausible.\n"
        "  5. Any numeric facts, dates, or names are accurate.\n\n"
        "Be tolerant of minor style issues (option prefixes, phrasing) — only flag "
        "genuine correctness or clarity problems.\n\n"
        "Return ONLY valid JSON, no markdown, no prose outside JSON:\n"
        "{\n"
        '  "results": [\n'
        '    {"id": "<question_id>", "verdict": "ok"},\n'
        '    {"id": "<question_id>", "verdict": "bad", "reason": "<short reason>"}\n'
        "  ]\n"
        "}\n\n"
        f"Questions ({len(items)}):\n"
        + json.dumps(items, ensure_ascii=False, indent=2)
    )
    return prompt


def call_openai(prompt, timeout=90):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing")
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "max_tokens": 2000,
        },
        timeout=timeout,
    )
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def parse_verdicts(parsed, batch_ids):
    """Return {id: ("ok"|"bad", reason)}"""
    out = {}
    results = parsed.get("results", [])
    if not isinstance(results, list):
        return out
    for r in results:
        if not isinstance(r, dict):
            continue
        qid = r.get("id")
        verdict = (r.get("verdict") or "").lower()
        reason = r.get("reason") or ""
        if qid and verdict in ("ok", "bad"):
            out[qid] = (verdict, reason)

    # Mark unreturned IDs as "unknown" (should not happen, but be safe)
    for qid in batch_ids:
        if qid not in out:
            out[qid] = ("unknown", "no verdict returned")
    return out


def mark_reviewed(ids):
    if not ids:
        return
    conn = db()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""
        UPDATE charvak_exam_question_bank
        SET reviewed = TRUE, reviewed_at = NOW(),
            reviewer_notes = COALESCE(reviewer_notes, '') || ' [ai-verified]'
        WHERE question_id = ANY(%s)
    """, (ids,))
    cur.close()
    conn.close()


def delete_ids(ids):
    if not ids:
        return
    conn = db()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM charvak_exam_question_bank WHERE question_id = ANY(%s)",
        (ids,)
    )
    cur.close()
    conn.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--delete-bad", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--batch-size", type=int, default=20)
    ap.add_argument("--exam", default=None)
    args = ap.parse_args()

    if not (args.report or args.apply):
        print("Specify --report or --apply")
        return

    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set")
        return

    print(f"\nFetching unreviewed questions (limit={args.limit or 'all'}, exam={args.exam or 'any'})...")
    questions = fetch_unreviewed(limit=args.limit, exam=args.exam)
    total = len(questions)
    print(f"Loaded {total} questions.\n")

    if total == 0:
        print("Nothing to verify.")
        return

    batches = [questions[i:i + args.batch_size] for i in range(0, total, args.batch_size)]
    print(f"Verifying in {len(batches)} batches of {args.batch_size}...\n")

    t_start = time.time()
    total_ok = 0
    total_bad = 0
    total_unknown = 0
    bad_examples = []
    processed = 0
    failures = 0

    for bi, batch in enumerate(batches, 1):
        batch_ids = [q["question_id"] for q in batch]
        try:
            prompt = build_prompt(batch)
            parsed = call_openai(prompt)
            verdicts = parse_verdicts(parsed, batch_ids)

            ok_ids = []
            bad_ids = []
            for qid, (v, reason) in verdicts.items():
                if v == "ok":
                    ok_ids.append(qid)
                    total_ok += 1
                elif v == "bad":
                    bad_ids.append(qid)
                    total_bad += 1
                    if len(bad_examples) < 20:
                        # find the question for context
                        ctx = next((q for q in batch if q["question_id"] == qid), None)
                        bad_examples.append((qid, reason, ctx["question_text"][:70] if ctx else ""))
                else:
                    total_unknown += 1

            if args.apply:
                mark_reviewed(ok_ids)
                if args.delete_bad:
                    delete_ids(bad_ids)

            processed += len(batch)
            elapsed = time.time() - t_start
            rate = processed / max(elapsed, 1)
            eta = (total - processed) / rate if rate > 0 else 0
            print(f"  [{bi}/{len(batches)}] processed={processed}/{total} "
                  f"ok={total_ok} bad={total_bad} "
                  f"rate={rate:.1f}/s ETA={eta:.0f}s")
            time.sleep(0.5)

        except Exception as e:
            failures += 1
            print(f"  BATCH {bi} FAILED: {e}")
            time.sleep(2)
            continue

    elapsed = time.time() - t_start
    print()
    print("=" * 72)
    print(f"  DONE in {elapsed:.0f}s")
    print(f"  Total:      {total}")
    print(f"  ✅ OK:       {total_ok}")
    print(f"  ❌ BAD:      {total_bad}")
    print(f"  ⚠ Unknown:  {total_unknown}")
    print(f"  Failed batches: {failures}")
    print("=" * 72)

    if bad_examples:
        print(f"\nSample rejected questions ({len(bad_examples)}):")
        for qid, reason, snippet in bad_examples:
            print(f"  [{qid[:12]}] {reason}")
            print(f"    Q: {snippet}")

    if args.report:
        print("\n(DRY RUN — no writes. Rerun with --apply to commit.)")
    elif args.apply:
        if args.delete_bad:
            print(f"\n✅ Applied: marked {total_ok} as reviewed, deleted {total_bad} bad.")
        else:
            print(f"\n✅ Applied: marked {total_ok} as reviewed. {total_bad} bad remain in bank.")
            print("   Run with --delete-bad to remove them.")


if __name__ == "__main__":
    main()