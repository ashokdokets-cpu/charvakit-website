"""
College portal config loader.
Each college is a JSON file in config/colleges/{slug}.json.
No database changes. No schema migration.
Adding a college = add a JSON file.
"""

import json
import os
import logging
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger("charvakit.college_config")

COLLEGE_DIR = Path(__file__).parent / "config" / "colleges"

# Cache: {slug: config_dict}
_cache: Dict[str, Dict] = {}
_cache_mtime: Dict[str, float] = {}


def _config_path(slug: str) -> Path:
    return COLLEGE_DIR / f"{slug}.json"


def _load_one(slug: str) -> Optional[Dict]:
    """Load a single college config. Reloads if file changed."""
    path = _config_path(slug)
    if not path.exists():
        return None

    try:
        mtime = path.stat().st_mtime
        if slug in _cache and _cache_mtime.get(slug) == mtime:
            return _cache[slug]

        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Validate required fields
        required = ["slug", "name"]
        for field in required:
            if field not in config:
                logger.error(f"College config {slug} missing required field: {field}")
                return None

        # Ensure slug matches filename
        if config["slug"] != slug:
            logger.warning(f"College config slug mismatch: file={slug}, config={config['slug']}")

        # Defaults
        config.setdefault("logo_url", "/static/images/logo.png")
        config.setdefault("primary_color", "#3ba591")
        config.setdefault("contact_email", "hr@charvakit.com")
        config.setdefault("plan", "pilot")
        config.setdefault("student_limit", 100)
        config.setdefault("students", [])
        config.setdefault("features", {})

        # Normalize features to explicit booleans
        default_features = {
            "assessments": True,
            "certificates": True,
            "cohort_analytics": False,
            "placement_api": False,
            "faculty_dashboard": False,
            "on_campus_training": False,
            "ai_tutor": False,
        }
        for k, v in default_features.items():
            config["features"].setdefault(k, v)

        _cache[slug] = config
        _cache_mtime[slug] = mtime
        logger.info(f"Loaded college config: {slug} ({config['name']})")
        return config
    except Exception as e:
        logger.error(f"Failed to load college config {slug}: {e}")
        return None


def get_college(slug: str) -> Optional[Dict]:
    """Get a college by its subdomain slug."""
    if not slug or not isinstance(slug, str):
        return None
    slug = slug.strip().lower()
    return _load_one(slug)


def list_colleges() -> List[str]:
    """List all configured college slugs."""
    if not COLLEGE_DIR.exists():
        return []
    return [p.stem for p in COLLEGE_DIR.glob("*.json") if p.stem != "template"]


def is_college_student(slug: str, email: str) -> bool:
    """Check if email is a registered student of this college."""
    config = get_college(slug)
    if not config:
        return False
    email = (email or "").strip().lower()
    students = config.get("students") or []
    return email in [s.lower() if isinstance(s, str) else s.get("email", "").lower() for s in students]


def get_reserved_subdomains() -> set:
    """Subdomains that should NOT be treated as college portals."""
    return {"www", "charvakit", "app", "api", "admin", "static", "docs", "blog", "jobs", "learn", "demo"}
