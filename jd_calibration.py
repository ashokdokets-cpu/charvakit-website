# jd_calibration.py
# Session 105: Check if a JD is within Charvak's calibrated skill range.
# Also validate that generated assessment questions match the JD.

from typing import Dict, List
from calibrated_skills import canonicalize, is_calibrated
import json

def _is_calibrated_including_db(skill_name: str) -> bool:
    """Check built-in catalog first, then charvak_skill_extensions DB."""
    if not skill_name:
        return False
    # Check built-in (fast path)
    if is_calibrated(skill_name):
        return True
    # Check DB extensions
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 1 FROM charvak_skill_extensions
            WHERE LOWER(canonical_name) = %s
               OR aliases::text ILIKE %s
            LIMIT 1
        """, (skill_name.strip().lower(), f'%"{skill_name.strip().lower()}"%'))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row is not None
    except Exception:
        # Table might not exist, or DB down -> fall back to catalog-only
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