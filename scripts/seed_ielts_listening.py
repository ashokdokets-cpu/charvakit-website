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


SECTION_SPECS = {
    1: {
        "name": "Section 1 — Conversation",
        "desc": ("Section 1 is a conversation between two speakers on a practical, everyday topic "
                 "(e.g., booking accommodation, enquiring about a course, planning a trip). "
                 "The transcript should be about 400-500 words with clear speaker turns. "
                 "Format speaker turns as 'SPEAKER A:' and 'SPEAKER B:' on separate lines."),
        "qtypes": "specific details (names, numbers, dates, prices), and simple inference.",
    },
    2: {
        "name": "Section 2 — Monologue",
        "desc": ("Section 2 is a single-speaker monologue on a general/non-academic topic "
                 "(e.g., a tour guide describing a facility, an announcement about an event). "
                 "The transcript should be about 400-500 words."),
        "qtypes": "specific facts, directions, times, and details from the announcement.",
    },
    3: {
        "name": "Section 3 — Academic Discussion",
        "desc": ("Section 3 is a discussion between two or three students and possibly a tutor, "
                 "on an academic topic (e.g., planning a research project, discussing an assignment). "
                 "Format speaker turns as 'STUDENT 1:', 'STUDENT 2:', 'TUTOR:' etc. "
                 "The transcript should be about 450-550 words."),
        "qtypes": "opinions, agreements/disagreements, reasoning, and specific details.",
    },
    4: {
        "name": "Section 4 — Academic Lecture",
        "desc": ("Section 4 is a single academic lecture (monologue) of about 3-4 minutes spoken "
                 "(roughly 500-650 words written) on a scientific or academic topic."),
        "qtypes": "main idea, specific facts, and inference from the lecture.",
    },
}


def generate_section(section_num, topic_hint=None):
    """Ask OpenAI for one transcript + 10 MCQs for the given section. Returns dict or None."""
    spec = SECTION_SPECS.get(section_num)
    if not spec:
        return None

    hint = f"Focus on the topic: {topic_hint}." if topic_hint else "Choose a fresh topic suitable for this section."

    prompt = (
        f"You are an IELTS Academic Listening {spec['name']} generator. "
        f"{spec['desc']} "
        f"{hint}\n\n"
        "Return ONLY valid JSON:\n"
        "{\n"
        '  "title": "short descriptive title",\n'
        '  "topic": "1-3 word topic label",\n'
        '  "transcript": "full transcript text",\n'
        '  "questions": [\n'
        '    {"q": "question text", "options": ["A text","B text","C text","D text"], "correct_idx": 0, "explanation": "why"},\n'
        "    ... exactly 10 questions ...\n"
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        f"- 10 questions total, testing {spec['qtypes']}\n"
        "- Each question MUST have exactly 4 options.\n"
        "- correct_idx is 0-3 (index into options).\n"
        "- Do NOT include the answers in the transcript.\n"
        "- The transcript must be suitable for reading aloud (no markdown, no bullet points, no stage directions).\n"
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
    sid = f"IELTS-L{section_num}-{secrets.token_hex(4).upper()}"
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
    ap.add_argument("--section", type=int, default=4, choices=[1, 2, 3, 4])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set")
        return

    sec = args.section
    have = existing_count(sec)
    print(f"Section-{sec} sections in DB: {have}")
    if have >= args.count and not args.force:
        print(f"Already have {have} >= {args.count}. Use --force to add more.")
        return

    to_add = args.count if args.force else (args.count - have)
    print(f"Generating {to_add} new Section-{sec} sections...\n")

    for i in range(1, to_add + 1):
        try:
            lec = generate_section(sec)
            if not lec:
                print(f"  [{i}/{to_add}] FAILED validation - skipping")
                continue
            sid = insert_section(sec, lec)
            print(f"  [{i}/{to_add}] OK {sid}  topic={lec['topic']}  words={len(lec['transcript'].split())}  qs={len(lec['questions'])}")
        except Exception as e:
            print(f"  [{i}/{to_add}] ERROR: {e}")

    print(f"\nDone. Section-{sec} total now: {existing_count(sec)}")


if __name__ == "__main__":
    main()