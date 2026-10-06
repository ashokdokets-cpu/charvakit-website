"""
Jobs Unified Engine (Session 31).

Read-only aggregation of the three job sources into one normalized feed:

  - charvak_jobs          (public job board)
  - charvak_client_roles  (CBREX-mediated staffing, sanitized)
  - charvak_micro_projects (gig/contract projects)

One call = one feed. Sanitization by construction — the public shape
never includes private fields (client_name, vendor refs, budgets for
staffing). Matching the /api/staffing/open contract.

Public API:
- get_unified_jobs(source=None, q=None, limit=100) -> dict

Design principles:
- Read-only. No writes.
- Each source wrapped in a safe section (a failure never breaks others).
- Normalized shape: one item structure regardless of source.
- Pre-formatted compensation.display for the frontend.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

VALID_SOURCES = {"job_board", "staffing", "micro_project"}
DEFAULT_LIMIT = 100
MAX_LIMIT = 200


class JobsUnifiedEngine:
    def __init__(self):
        pass

    # ------------------------------------------------------------ public

    def get_unified_jobs(
        self,
        source: Optional[str] = None,
        q: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
    ) -> Dict:
        """
        Return a unified feed of jobs from all three sources.

        source: optional comma-separated list from VALID_SOURCES
        q:      optional title substring (case-insensitive)
        limit:  1..MAX_LIMIT
        """
        # Parse filters
        wanted = None
        if source:
            wanted = {s.strip() for s in str(source).split(",") if s.strip()}
            invalid = wanted - VALID_SOURCES
            if invalid:
                return {
                    "status": "error",
                    "message": f"Invalid source(s): {sorted(invalid)}",
                    "valid_sources": sorted(VALID_SOURCES),
                }

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = DEFAULT_LIMIT
        limit = max(1, min(MAX_LIMIT, limit))

        q_norm = (q or "").strip().lower()

        # Fetch each source
        all_items = []
        source_counts = {"job_board": 0, "staffing": 0, "micro_project": 0}

        sections = [
            ("job_board", self._job_board),
            ("staffing", self._staffing),
            ("micro_project", self._micro_projects),
        ]
        for source_key, fn in sections:
            if wanted and source_key not in wanted:
                continue
            try:
                items = fn() or []
            except Exception as e:
                logger.warning(f"[jobs_unified] {source_key} failed: {e}")
                items = []
            source_counts[source_key] = len(items)
            all_items.extend(items)

        # Optional title filter
        if q_norm:
            all_items = [
                it for it in all_items
                if q_norm in (it.get("title") or "").lower()
            ]

        # Sort: posted_at DESC, then source ASC for stability
        def _sort_key(it):
            return (it.get("posted_at") or "", it.get("source") or "")

        all_items.sort(key=_sort_key, reverse=True)

        # Limit
        all_items = all_items[:limit]

        return {
            "status": "success",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "count": len(all_items),
            "sources": source_counts,
            "filters": {
                "source": sorted(list(wanted)) if wanted else None,
                "q": q_norm or None,
                "limit": limit,
            },
            "items": all_items,
        }

    # -------------------------------------------------------- source: job_board

    def _job_board(self) -> List[Dict]:
        from database import db
        conn = db.get_connection(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT job_id, title, company, job_type, location, salary,
                       description, skills, posted_date, status, created_at
                FROM charvak_jobs
                WHERE status IS NULL OR LOWER(status) IN ('active', 'open')
                ORDER BY created_at DESC NULLS LAST
                LIMIT 200
            """)
            items = []
            for r in cur.fetchall():
                skills = self._split_skills(r[7])
                items.append(self._normalize({
                    "id": r[0],
                    "source": "job_board",
                    "source_label": "Job Board",
                    "title": r[1],
                    "company": r[2],
                    "location": r[4],
                    "type": (r[3] or "permanent").lower(),
                    "skills": skills,
                    "compensation_display": (r[5] or "").strip() or None,
                    "compensation_min_inr": None,
                    "compensation_max_inr": None,
                    "posted_at": self._to_iso(r[10], r[8]),
                    "detail_url": f"/job-board/{r[0]}",
                }))
            return items
        finally:
            cur.close(); conn.close()

    # --------------------------------------------------------- source: staffing

    def _staffing(self) -> List[Dict]:
        from database import db
        conn = db.get_connection(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT role_id, title, location, experience_min_years,
                       experience_max_years, skills_required, job_type,
                       priority, created_at, submission_deadline
                FROM charvak_client_roles
                WHERE LOWER(status) IN ('sourcing', 'open', 'active')
                ORDER BY created_at DESC NULLS LAST
                LIMIT 200
            """)
            items = []
            for r in cur.fetchall():
                # Sanitization by construction:
                #  - client_name is never selected
                #  - budget_min_inr / budget_max_inr are never selected
                #  - company is forced to "via Charvak"
                skills = self._split_skills(r[5])
                items.append(self._normalize({
                    "id": r[0],
                    "source": "staffing",
                    "source_label": "via Charvak",
                    "title": r[1],
                    "company": "via Charvak",
                    "location": r[2],
                    "type": (r[6] or "permanent").lower(),
                    "priority": r[7],
                    "skills": skills,
                    "experience": {
                        "min_years": r[3],
                        "max_years": r[4],
                    },
                    "compensation_display": None,   # budgets hidden per /open-roles policy
                    "compensation_min_inr": None,
                    "compensation_max_inr": None,
                    "posted_at": self._to_iso(r[8], None),
                    "submission_deadline": r[9].isoformat() if r[9] else None,
                    "detail_url": f"/open-roles/{r[0]}",
                }))
            return items
        finally:
            cur.close(); conn.close()

    # --------------------------------------------------- source: micro_projects

    def _micro_projects(self) -> List[Dict]:
        from database import db
        conn = db.get_connection(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT project_id, title, category, difficulty, duration_weeks,
                       budget_inr, budget_usd, skills_required, description,
                       company_name, status, created_at
                FROM charvak_micro_projects
                WHERE LOWER(status) IN ('open', 'active', 'in_progress')
                ORDER BY created_at DESC NULLS LAST
                LIMIT 200
            """)
            items = []
            for r in cur.fetchall():
                skills = self._jsonb_skills(r[7])
                budget_inr = float(r[5]) if r[5] is not None else None
                budget_usd = float(r[6]) if r[6] is not None else None
                items.append(self._normalize({
                    "id": r[0],
                    "source": "micro_project",
                    "source_label": "Gig",
                    "title": r[1],
                    "company": r[9] or "via Charvak",
                    "location": "Remote",
                    "type": "gig",
                    "category": r[2],
                    "difficulty": r[3],
                    "duration_weeks": r[4],
                    "skills": skills,
                    "compensation_display": self._format_inr(budget_inr),
                    "compensation_min_inr": int(budget_inr) if budget_inr is not None else None,
                    "compensation_max_inr": int(budget_inr) if budget_inr is not None else None,
                    "compensation_usd": budget_usd,
                    "posted_at": self._to_iso(r[11], None),
                    "detail_url": f"/micro-internship/{r[0]}",
                }))
            return items
        finally:
            cur.close(); conn.close()

    # --------------------------------------------------------------- helpers

    def _normalize(self, item: Dict) -> Dict:
        """Enforce the unified shape: every item has the same required keys."""
        required_defaults = {
            "priority": None,
            "experience": None,
            "submission_deadline": None,
            "category": None,
            "difficulty": None,
            "duration_weeks": None,
            "compensation_usd": None,
        }
        for k, v in required_defaults.items():
            item.setdefault(k, v)
        # Trim null description; the detail page shows it
        item.pop("description", None)
        return item

    def _split_skills(self, raw) -> List[str]:
        """Comma- or pipe-separated string -> list of trimmed strings."""
        if not raw:
            return []
        if isinstance(raw, list):
            return [str(s).strip() for s in raw if str(s).strip()]
        s = str(raw)
        # Try comma first, fall back to pipe
        parts = s.split(",") if "," in s else s.split("|")
        return [p.strip() for p in parts if p.strip()][:20]

    def _jsonb_skills(self, raw) -> List[str]:
        if raw is None:
            return []
        if isinstance(raw, list):
            return [str(s).strip() for s in raw if str(s).strip()][:20]
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(s).strip() for s in parsed if str(s).strip()][:20]
            except Exception:
                pass
            return self._split_skills(raw)
        return []

    def _to_iso(self, created_at, fallback_text) -> Optional[str]:
        """Return an ISO 8601 timestamp. Prefer created_at (timestamp), fall
        back to a text date."""
        if created_at is not None and hasattr(created_at, "isoformat"):
            return created_at.isoformat()
        if fallback_text:
            return str(fallback_text).strip() or None
        return None

    def _format_inr(self, amount: Optional[float]) -> Optional[str]:
        if amount is None:
            return None
        try:
            n = float(amount)
        except (TypeError, ValueError):
            return None
        # Indian numbering: 1,00,000
        s = f"{int(n):,}"
        # Simple grouping by 2 for the last 3 digits (naive but adequate)
        return f"\u20b9{s}"


# Singleton, matching the codebase convention.
jobs_unified_engine = JobsUnifiedEngine()