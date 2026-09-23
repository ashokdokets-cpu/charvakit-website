#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Seed IELTS Academic Reading passages.

Generates N unique passages per passage_num (1, 2, or 3).
Passage 1: ~700 words, easier
Passage 2: ~800 words, medium
Passage 3: ~900 words, harder (inference-heavy)

Idempotent: skips if enough passages already exist.

Usage:
  python scripts/seed_ielts_reading.py --passage-num 1 --count 3
  python scripts/seed_ielts_reading.py --passage-num 2 --count 3
  python scripts/seed_ielts_reading.py --passage-num 3 --count 3
  python scripts/seed_ielts_reading.py --passage-num 1 --count 3 --force
"""
import argparse
import json
import os
import secrets
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import requests
import psycopg2


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = "gpt-4o-mini"


PASSAGE_SPECS = {
    1: {
        "target_words": 700,
        "difficulty": "easiest",
        "desc": ("Passage 1 is the easiest of the three IELTS Academic Reading passages. "
                 "It is a factual, descriptive text on a general-interest topic "
                 "(e.g., an animal species, a historical site, a common technology). "
                 "Aim for about 700 words."),
        "qtypes": "factual detail, main idea, and simple inference",
    },
    2: {
        "target_words": 800,
        "difficulty": "medium",
        "desc": ("Passage 2 is medium difficulty. It often describes a scientific, "
                 "technological, or social topic with some analysis. "
                 "Aim for about 800 words."),
        "qtypes": "specific facts, cause/effect, comparisons, and inference",
    },
    3: {
        "target_words": 900,
        "difficulty": "hardest",
        "desc": ("Passage 3 is the hardest passage. It presents an argument or "
                 "complex academic discussion with abstract ideas, multiple viewpoints, "
                 "or nuanced claims. Aim for about 900 words."),
        "qtypes": "author's opinion, argument structure, abstract inference, and vocabulary in context",
    },
}


def db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def existing_count(passage_num):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM charvak_ielts_reading_passages WHERE passage_num = %s",
        (passage_num,)
    )
    n = cur.fetchone()[0]
    cur.close()
    conn.close()
    return n


def generate_passage(passage_num):
    """Ask OpenAI for one passage + 10 MCQs. Returns dict or None."""
    spec = PASSAGE_SPECS.get(passage_num)
    if not spec:
        return None

    prompt = (
        f"You are an IELTS Academic Reading Passage {passage_num} generator. "
        f"{spec['desc']} "
        "Choose a fresh academic or general-interest topic.\n\n"
        "Return ONLY valid JSON:\n"
        "{\n"
        '  "title": "short descriptive title",\n'
        '  "topic": "1-3 word topic label",\n'
        '  "content": "full passage text (matching the target word count)",\n'
        '  "questions": [\n'
        '    {"q": "question text", "options": ["A text","B text","C text","D text"], '
        '"correct_idx": 0, "explanation": "why this is correct"},\n'
        "    ... exactly 10 questions ...\n"
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- 10 questions total.\n"
        f"- Questions test {spec['qtypes']}\n"
        "- Each question MUST have exactly 4 options.\n"
        "- correct_idx is 0-3 (index into options).\n"
        "- Do NOT include the answers in the passage text.\n"
        "- The passage MUST be suitable for a 700-900 word academic reading.\n"
        "- No markdown, no bullet points, no tables - plain prose only.\n"
    )

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "response_format": {"type": "json_object"},
            "max_tokens": 4000,
        },
        timeout=150,
    )
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    parsed = json.loads(content)

    if not parsed.get("content") or not parsed.get("questions"):
        return None
    qs = parsed["questions"]
    if not isinstance(qs, list) or len(qs) < 10:
        return None

    clean_qs = []
    for q in qs[:10]:
        opts = q.get("options") or []
        if len(opts) != 4:
            return None
        try:
            ci = int(q.get("correct_idx", 0))
        except Exception:
            ci = 0
        if ci < 0 or ci > 3:
            return None
        clean_qs.append({
            "q": str(q.get("q") or "").strip(),
            "options": [str(o).strip() for o in opts],
            "correct_idx": ci,
            "explanation": str(q.get("explanation") or "").strip(),
        })

    content_text = str(parsed["content"]).strip()
    word_count = len(content_text.split())

    return {
        "title": str(parsed.get("title") or "Reading Passage").strip(),
        "topic": str(parsed.get("topic") or "General").strip(),
        "content": content_text,
        "word_count": word_count,
        "questions": clean_qs,
    }


def insert_passage(passage_num, passage):
    sid = f"IELTS-R{passage_num}-{secrets.token_hex(4).upper()}"
    conn = db()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO charvak_ielts_reading_passages
            (passage_id, passage_num, title, topic, content, word_count, questions_json)
        VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
    """, (
        sid, passage_num, passage["title"], passage["topic"],
        passage["content"], passage["word_count"],
        json.dumps(passage["questions"])
    ))
    cur.close()
    conn.close()
    return sid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument("--passage-num", type=int, default=1, choices=[1, 2, 3])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set")
        return

    pn = args.passage_num
    have = existing_count(pn)
    print(f"Passage-{pn} in DB: {have}")
    if have >= args.count and not args.force:
        print(f"Already have {have} >= {args.count}. Use --force to add more.")
        return

    to_add = args.count if args.force else (args.count - have)
    print(f"Generating {to_add} new Passage-{pn} passages...\n")

    for i in range(1, to_add + 1):
        try:
            p = generate_passage(pn)
            if not p:
                print(f"  [{i}/{to_add}] FAILED validation - skipping")
                continue
            sid = insert_passage(pn, p)
            print(f"  [{i}/{to_add}] OK {sid}  topic={p['topic']}  words={p['word_count']}  qs={len(p['questions'])}")
        except Exception as e:
            print(f"  [{i}/{to_add}] ERROR: {e}")

    print(f"\nDone. Passage-{pn} total now: {existing_count(pn)}")


if __name__ == "__main__":
    main()