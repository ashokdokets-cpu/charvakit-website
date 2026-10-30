# jd_calibration.py
# Session 105: Check if a JD is within Charvak's calibrated skill range.
# Also validate that generated assessment questions match the JD.

from typing import Dict, List
from calibrated_skills import canonicalize, is_calibrated
import json
import re

# Session 106 follow-up: suffix-stripping for skill name normalization.
# Parser returns phrases like "Kubernetes deployment" or "HIPAA compliance";
# the catalog has base skills. Strip decorative suffixes before lookup.
_SUFFIXES = [
    " deployment", " deployments", " deployment experience",
    " compliance", " compliance experience",
    " architecture",
    " experience", " experience required",
    " knowledge", " knowledge required",
    " skills", " skills required",
    " proficiency", " proficiency required",
    " development", " development experience",
    " engineer", " engineer experience", " engineering",
    " specialist", " specialist experience",
    " design", " design skills", " design experience",
    " optimization", " optimization skills", " optimization experience",
    " frameworks", " framework", " framework experience",
    " libraries", " library",
    " integration", " integration experience",
    " databases", " database", " database experience",
    " analytics", " analytics database", " analytics database experience",
    " tools", " tool", " tooling",
    " orchestration", " pipeline", " pipelines",
    " (or similar)", " (or equivalent)", " or similar", " or equivalent",
]

def _strip_year_decorators(s: str) -> str:
    """Strip year decorations: '5+ years', '5-10 years', ', 3 years', '- 5 yrs', etc."""
    if not s:
        return s
    # Remove patterns: number(+/-dash/space)years/yrs, optional +/-
    s = re.sub(r"\s*[,;\-]?\s*\d+\s*\+?\s*(?:-\s*\d+\s*)?\s*(?:years?|yrs?)\b", "", s, flags=re.IGNORECASE)
    # Remove leading "5+ years" (already handled by above) — also leading digits+years
    s = re.sub(r"^\s*\d+\s*\+?\s*(?:-\s*\d+\s*)?\s*(?:years?|yrs?)\s*", "", s, flags=re.IGNORECASE)
    # Collapse multiple spaces and strip
    return re.sub(r"\s+", " ", s).strip()

def _strip_suffixes(skill_name: str) -> str:
    """Return a list of candidate names by progressively stripping suffixes."""
    if not skill_name:
        return ""
    s = skill_name.strip().lower()
    # Strip year decorations FIRST
    s = _strip_year_decorators(s)
    # Strip leading "experience in" / "expert in" / "strong" / "deep"
    for prefix in ["experience in ", "expert in ", "expert ", "strong ", "deep ", "advanced ", "senior "]:
        if s.startswith(prefix):
            s = s[len(prefix):]
    return s

# Session 106 follow-up: connector words to split on when looking for sub-skills.
_CONNECTORS = [
    " api ", " api integration", " api ", " or similar", " or equivalent",
    " with ", " for ", " and ", " using ", " via ", " through ",
    " (", " vs ", " versus ", " over ", " in ", " on ",
]

def _split_on_connectors(phrase: str) -> list:
    """Split a compound phrase into sub-phrases on connector words.
    E.g. 'GPT-4o API integration' -> ['gpt-4o', 'api integration']
    Returns list of stripped lowercase chunks."""
    if not phrase:
        return []
    s = phrase.lower()
    # Split on each connector, keep unique non-empty chunks
    chunks = {s}
    for conn in _CONNECTORS:
        parts = s.split(conn)
        for p in parts:
            p = p.strip()
            if p and len(p) > 1:
                chunks.add(p)
    # Strip suffixes from each chunk too
    expanded = set()
    for chunk in chunks:
        expanded.add(chunk)
        current = chunk
        for suffix in _SUFFIXES:
            if current.endswith(suffix):
                stripped = current[: -len(suffix)].strip()
                if stripped:
                    expanded.add(stripped)
                current = stripped
    return list(expanded)

def _skill_variants(skill_name: str) -> list:
    """Return a list of variants to try (from most-specific to base name)."""
    if not skill_name:
        return []
    base = _strip_suffixes(skill_name)
    variants = [skill_name.strip(), base]
    # Strip parentheticals: "Pinecone (vector database)" -> "Pinecone"
    paren = re.sub(r"\s*\([^)]*\)", "", base).strip()
    if paren and paren != base:
        variants.append(paren)
    # Strip suffixes progressively
    current = base
    for suffix in _SUFFIXES:
        if current.endswith(suffix):
            stripped = current[: -len(suffix)].strip()
            if stripped and stripped not in variants:
                variants.append(stripped)
            current = stripped
    # Try each variant with suffix stripping (some prefixes may not match cleanly)
    for v in list(variants):
        cleaned = re.sub(r"\s+(or similar|or equivalent).*$", "", v).strip()
        if cleaned and cleaned not in variants:
            variants.append(cleaned)
    # NEW: Add connector-split chunks as last resort
    for chunk in _split_on_connectors(skill_name):
        if chunk not in variants:
            variants.append(chunk)
    # NEW: Add dot<->space variants: "React JS" <-> "React.js", "Node.js backend" <-> "Node.js"
    for v in list(variants):
        if " " in v:
            dotted = v.replace(" ", ".")
            if dotted not in variants:
                variants.append(dotted)
            # Also try first word only (e.g. "Node.js backend" -> "node")
            first = v.split()[0].strip(".,;:-")
            if first and len(first) > 1 and first not in variants:
                variants.append(first)
        if "." in v:
            spaced = v.replace(".", " ")
            if spaced not in variants:
                variants.append(spaced)
    return variants

def _is_calibrated_including_db(skill_name: str) -> bool:
    """Check built-in catalog (BOTH modules), then DB extensions."""
    if not skill_name:
        return False

    # NEW: Check skill_catalog (518-skill catalog) with suffix-stripping variants
    variants = _skill_variants(skill_name)
    try:
        from skill_catalog import is_known as _catalog_is_known
        for variant in variants:
            if _catalog_is_known(variant):
                return True
    except Exception:
        pass

    # Then check calibrated_skills (legacy 142-skill catalog, backward compat)
    try:
        for variant in variants:
            if is_calibrated(variant):
                return True
    except Exception:
        pass

    # Then check DB extensions (auto-calibrated skills) — try each variant
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        for variant in variants:
            cur.execute("""
                SELECT 1 FROM charvak_skill_extensions
                WHERE LOWER(canonical_name) = %s
                   OR aliases::text ILIKE %s
                LIMIT 1
            """, (variant.strip().lower(), f'%"{variant.strip().lower()}"%'))
            row = cur.fetchone()
            if row is not None:
                cur.close()
                conn.close()
                return True
        cur.close()
        conn.close()
        return False
    except Exception:
        # Table might not exist, or DB down -> fall back
        return False


def check_jd_coverage(jd_parsed: Dict) -> Dict:
    """
    Check if a parsed JD is within Charvak's calibrated skill range.

    Returns:
        {
            "status": "calibrated" | "partial" | "not_calibrated",
            "coverage": 0-100,
            "covered": [str],
            "not_covered": [str],
            "action": "proceed" | "partial_assessment" | "decline",
            "message": str,
            "total_skills": int,
        }
    """
    skills_required = jd_parsed.get("skills_required", []) or []

    if isinstance(skills_required, str):
        skills_required = [s.strip() for s in skills_required.split(",") if s.strip()]

    if not skills_required:
        return {
            "status": "not_calibrated",
            "coverage": 0,
            "covered": [],
            "not_covered": [],
            "action": "decline",
            "message": "No skills detected in this JD. Unable to calibrate.",
            "total_skills": 0,
        }

    covered = []
    not_covered = []
    seen = set()

    for skill in skills_required:
        skill_lower = skill.strip().lower()
        if skill_lower in seen:
            continue
        seen.add(skill_lower)

        if _is_calibrated_including_db(skill):
            covered.append(skill)
        else:
            not_covered.append(skill)

    total = len(covered) + len(not_covered)
    coverage_pct = round((len(covered) / total) * 100) if total > 0 else 0

    if coverage_pct >= 80:
        status = "calibrated"
        action = "proceed"
        message = (
            f"All key skills calibrated. Ready to run assessment covering "
            f"{len(covered)} skills."
        )
    elif coverage_pct >= 50:
        status = "partial"
        action = "partial_assessment"
        not_cov_short = ", ".join(not_covered[:3])
        message = (
            f"Partial coverage: {coverage_pct}%. We can verify {len(covered)} of "
            f"{total} skills. For the remaining {len(not_covered)} ({not_cov_short}), "
            f"we recommend a second-round technical screen by your team."
        )
    else:
        status = "not_calibrated"
        action = "decline"
        not_cov_short = ", ".join(not_covered[:5])
        message = (
            f"Not enough calibrated skills (only {coverage_pct}% coverage). "
            f"This role includes skills outside our current scope: {not_cov_short}. "
            f"We recommend waiting until we expand coverage, or using an "
            f"alternative assessment method."
        )

    return {
        "status": status,
        "coverage": coverage_pct,
        "covered": covered,
        "not_covered": not_covered,
        "total_skills": total,
        "action": action,
        "message": message,
    }


def validate_generated_questions(questions: List[Dict], jd_parsed: Dict) -> Dict:
    """
    After AI generates assessment questions, validate they're calibrated.

    Returns:
        {
            "validated": bool,
            "accuracy": 0-100,
            "valid_count": int,
            "invalid_count": int,
            "action": "ship" | "regenerate",
        }
    """
    skills_required = jd_parsed.get("skills_required", []) or []
    if isinstance(skills_required, str):
        skills_required = [s.strip() for s in skills_required.split(",") if s.strip()]

    required_canonical = {canonicalize(s) for s in skills_required}
    required_canonical.discard("")

    if not required_canonical or not questions:
        return {
            "validated": False,
            "accuracy": 0,
            "valid_count": 0,
            "invalid_count": len(questions) if questions else 0,
            "action": "regenerate",
        }

    valid = 0
    invalid = 0

    for q in questions:
        q_skills = q.get("skills_tested", []) or []
        q_canonical = {canonicalize(s) for s in q_skills}
        q_canonical.discard("")

        if q_canonical & required_canonical:
            valid += 1
        else:
            invalid += 1

    accuracy = round((valid / len(questions)) * 100) if questions else 0

    return {
        "validated": accuracy >= 80,
        "accuracy": accuracy,
        "valid_count": valid,
        "invalid_count": invalid,
        "action": "ship" if accuracy >= 80 else "regenerate",
    }