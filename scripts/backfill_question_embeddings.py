#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backfill embeddings for charvak_exam_question_bank.

Uses OpenAI text-embedding-3-small (1536 dims).
Batches 100 questions per API call. Idempotent.

Usage:
    python scripts/backfill_question_embeddings.py
    python scripts/backfill_question_embeddings.py --batch 200
    python scripts/backfill_question_embeddings.py --limit 500   # for testing
"""
import argparse
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from dotenv import load_dotenv
load_dotenv()


def get_openai_embeddings(texts, api_key, model="text-embedding-3-small"):
    """Return list of embedding vectors, same order as input texts."""
    r = requests.post(
        "https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "input": texts},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    # Preserve order — OpenAI returns in same order
    return [item["embedding"] for item in data["data"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=100)
    ap.add_argument("--limit", type=int, default=None,
                    help="Max questions to process (for testing)")
    ap.add_argument("--throttle", type=float, default=0.5,
                    help="Seconds between API calls")
    args = ap.parse_args()

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set")
        sys.exit(1)

    import psycopg2
    from psycopg2.extras import execute_values

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    # Count pending
    cur.execute("SELECT COUNT(*) FROM charvak_exam_question_bank WHERE embedding IS NULL")
    pending = cur.fetchone()[0]
    total = pending
    print(f"Questions missing embeddings: {pending}")
    if args.limit:
        pending = min(pending, args.limit)
        print(f"Limiting to: {pending}")

    if pending == 0:
        print("Nothing to do. All questions have embeddings.")
        conn.close()
        return

    processed = 0
    failed_batches = 0
    t_start = time.time()

    while processed < pending:
        to_fetch = min(args.batch, pending - processed)
        cur.execute("""
            SELECT question_id, question_text
            FROM charvak_exam_question_bank
            WHERE embedding IS NULL
            ORDER BY created_at
            LIMIT %s
        """, (to_fetch,))
        rows = cur.fetchall()
        if not rows:
            break

        qids = [r[0] for r in rows]
        texts = [r[1] for r in rows]

        try:
            t0 = time.time()
            embeddings = get_openai_embeddings(texts, api_key)
            t_api = time.time() - t0

            # Update rows in one statement per batch using execute_values
            update_data = [
                (qid, emb) for qid, emb in zip(qids, embeddings)
            ]

            # Use a temp table for batch update
            cur.execute("CREATE TEMP TABLE IF NOT EXISTS _emb_updates (qid text, emb vector(1536)) ON COMMIT DROP")
            execute_values(cur,
                "INSERT INTO _emb_updates (qid, emb) VALUES %s",
                update_data,
                template="(%s, %s::vector)"
            )
            cur.execute("""
                UPDATE charvak_exam_question_bank t
                SET embedding = u.emb
                FROM _emb_updates u
                WHERE t.question_id = u.qid
            """)
            conn.commit()

            processed += len(rows)
            elapsed = time.time() - t_start
            rate = processed / max(elapsed, 1)
            eta = (pending - processed) / rate if rate > 0 else 0
            print(f"[{processed}/{pending}] batch={len(rows)} api={t_api:.1f}s "
                  f"rate={rate:.1f}/s ETA={eta:.0f}s")

            time.sleep(args.throttle)

        except Exception as e:
            failed_batches += 1
            print(f"  BATCH FAILED: {e}")
            conn.rollback()
            # Skip this batch to avoid infinite loop
            cur.execute("""
                UPDATE charvak_exam_question_bank
                SET embedding = array_fill(0.0, ARRAY[1536])::vector
                WHERE question_id = ANY(%s) AND embedding IS NULL
            """, (qids,))
            conn.commit()
            processed += len(rows)
            time.sleep(2)

    elapsed = time.time() - t_start
    cur.execute("SELECT COUNT(*) FROM charvak_exam_question_bank WHERE embedding IS NULL")
    remaining = cur.fetchone()[0]

    print()
    print(f"=== Done in {elapsed:.0f}s ===")
    print(f"  Processed:       {processed}")
    print(f"  Failed batches:  {failed_batches}")
    print(f"  Remaining NULL:  {remaining}")

    conn.close()


if __name__ == "__main__":
    main()
