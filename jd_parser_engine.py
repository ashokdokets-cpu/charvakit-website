"""
JD Parser Engine
Session 55 (2026-10-19) - Track D Phase A, item A

Parses a job description into structured data for downstream
assessment design. Uses openai_compat shim (Sessions 53-54) for
model-aware API calls.

Design:
- No database. No tables. Pure function.
- Uses httpx sync client (no async complexity).
- Sanitizes AI output: whitelist seniority, whitelist formats,
  dedupe skills, cap list sizes, clamp years to sane ranges.
- Returns {status: "success", parsed: {...}} or {status: "error", message: ...}
- Safe on garbage input: returns error dict, never raises.
"""

import json
import logging
import os
import re
from typing import Dict, List, Optional

import httpx

from openai_compat import build_payload
from global_config import OPENAI_MODEL

logger = logging.getLogger("charvakit.jd_parser")


# Controlled vocabularies
SENIORITY_LEVELS = [
    "intern", "junior", "mid", "senior", "staff", "manager", "executive"
]

ASSESSMENT_FORMATS = [
    "mcq", "short_answer", "numeracy", "situational_judgment",
    "behavioral", "system_design", "debugging", "case_study",
    "coding", "sql"
]

ASSESSMENT_DIFFICULTIES = ["junior", "mid", "senior", "staff"]


def _build_prompt(jd_text: str) -> str:
    """Build the extraction prompt."""
    return f"""You are an expert job description parser. Extract structured
information from the following job description.

JOB DESCRIPTION:
\"\"\"
{jd_text}
\"\"\"

Return ONLY valid JSON with this exact schema:
{{
  "title": "<role title>",
  "company": "<company name or empty string>",
  "seniority": "<one of: intern, junior, mid, senior, staff, manager, executive>",
  "domain": "<industry/function e.g. 'AI/ML', 'FinTech', 'Healthcare'>",
  "skills_required": ["<skill 1>", "<skill 2>", ...],
  "skills_nice_to_have": ["<skill>", ...],
  "experience_years_min": <integer or null>,
  "experience_years_max": <integer or null>,
  "responsibilities": ["<resp 1>", "<resp 2>", ...],
  "success_signals": ["<what 'good' looks like, 1 phrase each>"],
  "assessment_relevance": {{
    "topics": ["<topic the JD emphasizes>", ...],
    "formats": ["<suggested assessment format from: mcq, short_answer, numeracy, situational_judgment, behavioral, system_design, debugging, case_study, coding, sql>"],
    "difficulty": "<junior | mid | senior | staff>"
  }}
}}

Rules:
- title: exact role title as written in the JD
- company: ONLY if the JD explicitly names the hiring company. Most JDs do NOT state this — return "" in that case. Do NOT guess.
- seniority: infer from title + years of experience mentioned
- skills_required: skills the JD says MUST have or explicitly requires
- skills_nice_to_have: skills the JD mentions but doesn't require
- experience_years_min/max: extract from "X+ years" or "X-Y years" mentions.
  Return null if not stated.
- responsibilities: key actions/responsibilities (5-10 most important)
- success_signals: 3-5 phrases describing what success looks like
- assessment_relevance.topics: 5-10 topics the assessment should cover
  (extract from skills + responsibilities)
- assessment_relevance.formats: 1-4 formats that best test this role.
  Guessing rules:
  - coding/AI/backend roles -> ["mcq", "coding", "system_design"]
  - data roles -> ["mcq", "sql", "case_study"]
  - business/HR/sales roles -> ["mcq", "behavioral", "case_study"]
  - hardware/embedded roles -> ["mcq", "debugging", "system_design"]
  - design roles -> ["mcq", "short_answer", "case_study"]
- assessment_relevance.difficulty: junior (<2 yrs), mid (2-5 yrs),
  senior (5-10 yrs), staff (10+)

Return ONLY the JSON object. No prose, no markdown fences.
"""


def _clean_string_list(items, cap: int = 30, item_max: int = 100) -> List[str]:
    """Deduplicate, trim, cap a list of strings."""
    if not isinstance(items, list):
        return []
    seen = set()
    result = []
    for item in items:
        s = str(item or "").strip()[:item_max]
        if s and s.lower() not in seen:
            seen.add(s.lower())
            result.append(s)
            if len(result) >= cap:
                break
    return result


def _safe_int(value, lo: int = 0, hi: int = 50) -> Optional[int]:
    """Parse an int safely with clamping."""
    if value is None:
        return None
    try:
        n = int(value)
    except (ValueError, TypeError):
        return None
    return max(lo, min(n, hi))


def _sanitize_result(data: Dict) -> Optional[Dict]:
    """Sanitize parsed result: normalize, validate whitelists, fill defaults."""
    if not isinstance(data, dict):
        return None

    title = str(data.get("title") or "").strip()[:200]
    if not title:
        return None  # title is required

    company = str(data.get("company") or "").strip()[:200]  # often empty - JD usually doesn't name the employer

    seniority = str(data.get("seniority") or "").strip().lower()
    if seniority not in SENIORITY_LEVELS:
        seniority = "mid"

    domain = str(data.get("domain") or "").strip()[:100]

    skills_required = _clean_string_list(data.get("skills_required"), cap=30)
    skills_nice = _clean_string_list(data.get("skills_nice_to_have"), cap=20)

    min_y = _safe_int(data.get("experience_years_min"))
    max_y = _safe_int(data.get("experience_years_max"))
    if min_y is not None and max_y is not None and min_y > max_y:
        min_y, max_y = max_y, min_y

    responsibilities = _clean_string_list(data.get("responsibilities"), cap=10, item_max=300)
    success_signals = _clean_string_list(data.get("success_signals"), cap=5, item_max=200)

    ar = data.get("assessment_relevance") or {}
    if not isinstance(ar, dict):
        ar = {}

    topics = _clean_string_list(ar.get("topics"), cap=10, item_max=50)
    formats_raw = _clean_string_list(ar.get("formats"), cap=5, item_max=30)
    formats = [f.lower() for f in formats_raw if f.lower() in ASSESSMENT_FORMATS]
    if not formats:
        formats = ["mcq"]

    difficulty = str(ar.get("difficulty") or "mid").strip().lower()
    if difficulty not in ASSESSMENT_DIFFICULTIES:
        difficulty = "mid"

    return {
        "title": title,
        "company": company,
        "seniority": seniority,
        "domain": domain,
        "skills_required": skills_required,
        "skills_nice_to_have": skills_nice,
        "experience_years_min": min_y,
        "experience_years_max": max_y,
        "responsibilities": responsibilities,
        "success_signals": success_signals,
        "assessment_relevance": {
            "topics": topics,
            "formats": formats,
            "difficulty": difficulty,
        },
    }


def parse_jd(jd_text: str) -> Dict:
    """
    Parse a job description into structured data.

    Args:
        jd_text: raw JD text (50-20,000 chars)

    Returns:
        {status: "success", parsed: {11 fields}} on success
        {status: "error", message: "<reason>"} on failure
    """
    if not jd_text or not isinstance(jd_text, str):
        return {"status": "error", "message": "jd_text is required"}

    jd_text = jd_text.strip()
    if len(jd_text) < 50:
        return {"status": "error", "message": "jd_text too short (min 50 chars)"}
    if len(jd_text) > 20000:
        return {"status": "error", "message": "jd_text too long (max 20,000 chars)"}

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"status": "error", "message": "OPENAI_API_KEY not set"}

    try:
        prompt = _build_prompt(jd_text)
        messages = [{"role": "user", "content": prompt}]
        payload = build_payload(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=2000,
            temperature=0.1,   # low temp for structured extraction
            json_mode=True,
        )

        with httpx.Client(timeout=45.0) as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            data = response.json()

        if "choices" not in data or not data["choices"]:
            err = data.get("error", {}).get("message", "no response from OpenAI")
            return {"status": "error", "message": f"API error: {err}"}

        raw = data["choices"][0]["message"]["content"] or ""

        # Defensive: strip markdown fences even in JSON mode
        raw = raw.strip()
        if raw.startswith("```"):
            parts = raw.split("```", 2)
            if len(parts) >= 2:
                raw = parts[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

        parsed_raw = json.loads(raw)
        sanitized = _sanitize_result(parsed_raw)
        if sanitized is None:
            return {"status": "error", "message": "Invalid parsed structure (no title)"}

        logger.info(
            f"JD parsed: title={sanitized['title']!r}, "
            f"seniority={sanitized['seniority']}, "
            f"skills_req={len(sanitized['skills_required'])}, "
            f"formats={sanitized['assessment_relevance']['formats']}"
        )

        return {"status": "success", "parsed": sanitized}

    except json.JSONDecodeError as e:
        logger.warning(f"JD parse JSON decode error: {e}")
        return {"status": "error", "message": "AI returned invalid JSON"}
    except Exception as e:
        logger.warning(f"JD parse error: {type(e).__name__}: {e}")
        return {"status": "error", "message": str(e)}