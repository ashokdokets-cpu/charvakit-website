# skill_auto_calibrator.py
# Session 106: Auto-calibrate unknown skills via OpenAI.
# When a JD has a skill not in skill_catalog, this generates a
# calibrated entry on the fly and persists it to charvak_skill_extensions.
#
# Flow:
#   1. Check skill_catalog.py (142 hardcoded skills) -> instant return
#   2. Check charvak_skill_extensions (DB, prior auto-calibrations) -> instant return
#   3. Call OpenAI to analyze + generate task classes -> ~5 seconds
#   4. Persist to DB for future requests -> instant next time

import os
import json
from typing import Dict


def auto_calibrate_skill(skill_name: str) -> Dict:
    """
    Attempt to auto-calibrate an unknown skill.

    Returns:
        {
            "status": "success" | "already_calibrated" | "cannot_calibrate",
            "skill": {...},        # canonical + metadata
            "task_classes": [...], # specific subtopics to test
            "reason": str,         # if cannot_calibrate
        }
    """
    if not skill_name or not skill_name.strip():
        return {"status": "cannot_calibrate", "reason": "empty skill name"}

    skill_name = skill_name.strip()

    # --- Step 1: Already in built-in catalog? ---
    try:
        from skill_catalog import get_skill
        existing = get_skill(skill_name)
        if existing:
            return {
                "status": "already_calibrated",
                "skill": existing,
                "task_classes": [],
            }
    except Exception as e:
        return {"status": "cannot_calibrate", "reason": f"catalog error: {e}"}

    # --- Step 2: Already in DB extensions? ---
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT canonical_name, category, test_type, judge0_language_id,
                   task_classes, aliases
            FROM charvak_skill_extensions
            WHERE LOWER(canonical_name) = %s
            LIMIT 1
        """, (skill_name.lower(),))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            task_classes = row[4] if isinstance(row[4], list) else json.loads(row[4] or "[]")
            aliases = row[5] if isinstance(row[5], list) else json.loads(row[5] or "[]")
            return {
                "status": "already_calibrated",
                "skill": {
                    "canonical": row[0],
                    "category": row[1],
                    "test_type": row[2],
                    "judge0_id": row[3],
                    "aliases": aliases,
                    "source": "db_extension",
                },
                "task_classes": task_classes,
            }
    except Exception:
        # Table may not exist yet - that is fine, fall through to OpenAI
        pass

    # --- Step 3: Ask OpenAI to analyze + calibrate ---
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return {
            "status": "cannot_calibrate",
            "reason": "OPENAI_API_KEY not set - auto-calibration unavailable",
        }

    try:
        import requests
        from global_config import OPENAI_MODEL
    except Exception as e:
        return {"status": "cannot_calibrate", "reason": f"import error: {e}"}

    prompt = (
        'You are a skill calibration expert for a technical assessment platform. '
        'Analyze this skill name: "' + skill_name + '"\n\n'
        'Return ONLY valid JSON with this exact shape (no markdown, no explanation):\n'
        '{\n'
        '  "is_valid_skill": true,\n'
        '  "canonical_name": "Proper Name",\n'
        '  "category": "language|framework|database|cloud|orm|devops|testing|ml|mobile|security|blockchain|concept|behavioral|domain|other",\n'
        '  "test_type": "mcq|coding|sql|behavioral",\n'
        '  "judge0_language_id": null,\n'
        '  "task_classes": ["subtopic 1", "subtopic 2", "subtopic 3", "subtopic 4", "subtopic 5"],\n'
        '  "reason_if_invalid": ""\n'
        '}\n\n'
        'Rules:\n'
        '- If the name is gibberish or not a real skill, set is_valid_skill=false and explain in reason_if_invalid\n'
        'CRITICAL: choose test_type correctly based on skill nature:\n'
        '- If skill is a PROGRAMMING LANGUAGE (Python, JavaScript, Java, C++, Go, Rust, Kotlin, Swift, Ruby, PHP, C#, Scala, R, etc.): test_type="coding" and judge0_language_id = matching Judge0 CE id\n'
        '- If skill is a FRAMEWORK or LIBRARY (Django, Django REST Framework, React, Spring Boot, FastAPI, Express, Hibernate, etc.): test_type="mcq", judge0_language_id=null. Frameworks are tested via conceptual MCQ (e.g. "how does DRF serializer validation work?"), NOT via code execution.\n'
        '- If skill is a DATABASE or SQL variant: test_type="sql", judge0_language_id=82\n'
        '- If skill is a CONCEPT (algorithms, system design, OOP, microservices): test_type="mcq", judge0_language_id=null\n'
        '- If skill is BEHAVIORAL (communication, leadership): test_type="behavioral", judge0_language_id=null\n'
        '- If skill is a CLOUD SERVICE or DEVOPS tool (AWS Lambda, K8s, Docker, Terraform): test_type="mcq", judge0_language_id=null\n'
        '- If test_type is coding but the language is NOT supported by Judge0 (Rust, Elixir, OCaml, Zig, Haskell, Nim, Crystal), set test_type="mcq" and judge0_language_id=null, add note in reason_if_invalid explaining code execution is unavailable\n'
        '- task_classes must be SPECIFIC subtopics, not generic categories\n'
        '- Return between 3 and 6 task_classes\n'
        '- Example for Hibernate: ["session-management", "lazy-loading", "hql", "transactions", "caching"]\n'
        '- Example for Rust: ["ownership", "borrowing", "lifetimes", "traits", "pattern-matching"]\n'
    )

    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": OPENAI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )
        data = resp.json()
        content = (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()

        # Strip markdown fences if present
        if content.startswith("```"):
            content = content.split("```", 2)[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        analysis = json.loads(content)
    except Exception as e:
        return {"status": "cannot_calibrate", "reason": f"openai error: {e}"}

    if not analysis.get("is_valid_skill", False):
        return {
            "status": "cannot_calibrate",
            "reason": analysis.get("reason_if_invalid", "Not a valid skill"),
        }

    # --- Step 4: Build skill entry ---
    canonical = (analysis.get("canonical_name") or skill_name).strip()
    category = (analysis.get("category") or "other").strip().lower()
    test_type = (analysis.get("test_type") or "mcq").strip().lower()
    judge0_id = analysis.get("judge0_language_id")
    task_classes = analysis.get("task_classes") or []
    fallback_note = analysis.get("reason_if_invalid", "")

    # Validate task_classes
    if not isinstance(task_classes, list) or len(task_classes) < 3:
        return {
            "status": "cannot_calibrate",
            "reason": "OpenAI returned insufficient task classes",
        }

    skill_meta = {
        "canonical": canonical,
        "aliases": [skill_name.lower()],
        "category": category,
        "test_type": test_type,
        "judge0_id": judge0_id,
        "task_classes": task_classes,
        "auto_generated": True,
    }
    if fallback_note:
        skill_meta["fallback_note"] = fallback_note

    # --- Step 5: Persist to charvak_skill_extensions ---
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()

        # Self-healing DDL
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charvak_skill_extensions (
                skill_id TEXT PRIMARY KEY,
                canonical_name TEXT NOT NULL UNIQUE,
                aliases JSONB,
                category TEXT,
                test_type TEXT,
                judge0_language_id INTEGER,
                task_classes JSONB,
                auto_generated BOOLEAN DEFAULT TRUE,
                validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        import secrets
        skill_id = "SKL-" + secrets.token_hex(6).upper()

        cur.execute("""
            INSERT INTO charvak_skill_extensions
                (skill_id, canonical_name, aliases, category, test_type,
                 judge0_language_id, task_classes, auto_generated)
            VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s::jsonb, TRUE)
            ON CONFLICT (canonical_name) DO NOTHING
        """, (
            skill_id,
            canonical,
            json.dumps([skill_name.lower()]),
            category,
            test_type,
            judge0_id,
            json.dumps(task_classes),
        ))
        conn.commit()
        cur.close()
        conn.close()
        skill_meta["skill_id"] = skill_id
    except Exception as e:
        # Non-fatal: skill still works for this request even if DB fails
        skill_meta["db_persist_error"] = str(e)

    return {
        "status": "success",
        "skill": skill_meta,
        "task_classes": task_classes,
    }


def batch_auto_calibrate(skill_names: list) -> Dict:
    """
    Auto-calibrate a list of skills. Returns per-skill results.
    Used by the /ai-assessment UI when multiple skills are missing.
    """
    results = []
    for name in (skill_names or []):
        try:
            r = auto_calibrate_skill(name)
            results.append({
                "requested_name": name,
                "status": r.get("status"),
                "canonical": r.get("skill", {}).get("canonical", name) if r.get("skill") else name,
                "task_classes": r.get("task_classes", []),
                "reason": r.get("reason"),
                "fallback_note": r.get("skill", {}).get("fallback_note") if r.get("skill") else None,
            })
        except Exception as e:
            results.append({
                "requested_name": name,
                "status": "cannot_calibrate",
                "reason": str(e),
            })

    succeeded = sum(1 for r in results if r["status"] in ("success", "already_calibrated"))
    return {
        "status": "complete",
        "results": results,
        "total": len(results),
        "succeeded": succeeded,
        "failed": len(results) - succeeded,
    }