#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Seed IELTS Listening Section 4 (Academic Lecture) sections.

Generates N unique lectures via OpenAI, each with:
  - A 400-600 word academic transcript (~3-4 min spoken)
  - 10 multiple-choice questions
  - Topic + title metadata

Idempotent: skips if enough Section-4 sections already exist.

Usage:
  python scripts/seed_ielts_listening.py --count 5
  python scripts/seed_ielts_listening.py --count 5 --force
"""
import argparse
import json
import os
import re
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


def db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def existing_count(section_num=4):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM charvak_ielts_listening_sections WHERE section_num = %s",
        (section_num,)
    )
    n = cur.fetchone()[0]
    cur.close()
    conn.close()
    return n


def generate_lecture(topic_hint=None):
    """Ask OpenAI for one transcript + 10 MCQs. Returns dict or None."""
    hint = f"Focus on the topic: {topic_hint}." if topic_hint else "Choose a fresh academic topic."
    prompt = (
        "You are an IELTS Academic Listening Section 4 generator. "
        "Section 4 is a single academic lecture (monologue) of about 3-4 minutes spoken "
        "(roughly 500-650 words written) on a scientific or academic topic. "
        f"{hint}\n\n"
        "Return ONLY valid JSON:\n"
        "{\n"
        '  "title": "short descriptive title",\n'
        '  "topic": "1-3 word topic label",\n'
        '  "transcript": "full lecture text (500-650 words)",\n'
        '  "questions": [\n'
        '    {"q": "question text", "options": ["A text","B text","C text","D text"], "correct_idx": 0, "explanation": "why"},\n'
        "    ... exactly 10 questions ...\n"
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- 10 questions total.\n"
        "- Each question MUST have exactly 4 options.\n"
        "- correct_idx is 0-3 (index into options).\n"
        "- Questions should test comprehension of the lecture (main idea, specific facts, inference).\n"
        "- Do NOT include the answers in the transcript.\n"
        "- The transcript must be suitable for reading aloud (no markdown, no bullet points).\n"
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
            "max_tokens": 2500,
        },
        timeout=120,
    )
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    parsed = json.loads(content)

    # Validate
    if not parsed.get("transcript") or not parsed.get("questions"):
        return None
    qs = parsed["questions"]
    if not isinstance(qs, list) or len(qs) < 10:
        return None
    # Normalize options to 4
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

    transcript = str(parsed["transcript"]).strip()
    duration = max(120, int(len(transcript.split()) / 2.5))  # ~150 wpm, min 120s

    return {
        "title": str(parsed.get("title") or "Academic Lecture").strip(),
        "topic": str(parsed.get("topic") or "Academic").strip(),
        "transcript": transcript,
        "duration_sec": duration,
        "questions": clean_qs,
    }


def insert_section(section_num, lecture):
    sid = f"IELTS-L4-{secrets.token_hex(4).upper()}"
    conn = db()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO charvak_ielts_listening_sections
            (section_id, section_num, title, topic, transcript, duration_sec, questions_json)
        VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
    """, (
        sid, section_num, lecture["title"], lecture["topic"],
        lecture["transcript"], lecture["duration_sec"],
        json.dumps(lecture["questions"])
    ))
    cur.close()
    conn.close()
    return sid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set")
        return

    have = existing_count(4)
    print(f"Section-4 lectures in DB: {have}")
    if have >= args.count and not args.force:
        print(f"Already have {have} >= {args.count}. Use --force to add more.")
        return

    to_add = args.count if args.force else (args.count - have)
    print(f"Generating {to_add} new Section-4 lectures...\n")

    for i in range(1, to_add + 1):
        try:
            lec = generate_lecture()
            if not lec:
                print(f"  [{i}/{to_add}] FAILED validation — skipping")
                continue
            sid = insert_section(4, lec)
            print(f"  [{i}/{to_add}] ✅ {sid}  topic={lec['topic']}  words={len(lec['transcript'].split())}  qs={len(lec['questions'])}")
        except Exception as e:
            print(f"  [{i}/{to_add}] ERROR: {e}")

    print(f"\nDone. Section-4 total now: {existing_count(4)}")


if __name__ == "__main__":
    main()