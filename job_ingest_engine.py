"""
Job Ingest Engine — multi-source job board ingestion (Session 107)

Pulls jobs from:
- Remotive (free public API, worldwide remote tech)
- Arbeitnow (free public API, worldwide + EU)

Filters to US-eligible jobs only (H1B/OPT/H4 EAD candidates cannot
apply to region-restricted jobs).

Design:
- Adapter pattern: each source is a separate ingest_<source>() method
- Idempotent: dedupe by (source, external_job_id)
- US-eligible filter: reject EU-only, UK-only, etc.
- Never raises: always returns {status, inserted, skipped, errors}
- Self-healing DDL: safe to call on fresh DB
"""

import os
import json
import logging
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# US-eligibility keywords (allow)
US_LOCATION_KEYWORDS = [
    "usa", "united states", "u.s.", "us only", "us remote", "us-based",
    "worldwide", "anywhere", "global", "remote - us",
]

# Region-restricted keywords (reject unless US also mentioned)
EU_LOCATION_KEYWORDS = [
    "eu only", "europe only", "uk only", "germany only", "france only",
    "netherlands only", "spain only", "italy only", "poland only",
    "portugal only", "ireland only",
]

# Non-US continents/regions (reject)
NON_US_REGIONS = [
    "asia only", "africa only", "south america only", "latin america only",
    "australia only", "new zealand only", "middle east only", "india only",
]


class JobIngestEngine:
    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self):
        """Self-healing DDL — ensures all columns exist."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                ALTER TABLE charvak_jobs
                    ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual',
                    ADD COLUMN IF NOT EXISTS external_job_id TEXT,
                    ADD COLUMN IF NOT EXISTS raw_json JSONB,
                    ADD COLUMN IF NOT EXISTS is_us_eligible BOOLEAN DEFAULT TRUE,
                    ADD COLUMN IF NOT EXISTS location TEXT
            """)
            cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_source_external
                    ON charvak_jobs (source, external_job_id)
                    WHERE external_job_id IS NOT NULL
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_job_sources (
                    source_name TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    api_url TEXT,
                    attribution_text TEXT,
                    active BOOLEAN DEFAULT TRUE,
                    last_sync_at TIMESTAMP,
                    last_sync_status TEXT,
                    last_sync_error TEXT,
                    total_jobs_fetched INTEGER DEFAULT 0,
                    total_jobs_inserted INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                INSERT INTO charvak_job_sources (source_name, display_name, api_url, attribution_text, active)
                VALUES
                    ('remotive', 'Remotive', 'https://remotive.com/api/remote-jobs',
                     'Job data from Remotive (https://remotive.com)', TRUE),
                    ('arbeitnow', 'Arbeitnow', 'https://www.arbeitnow.com/api/job-board-api',
                     'Job data from Arbeitnow (https://www.arbeitnow.com)', TRUE)
                ON CONFLICT (source_name) DO NOTHING
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.warning(f"job_ingest_engine._ensure_tables warning: {e}")

    # ---------------------------------------------------------------
    # US eligibility filter
    # ---------------------------------------------------------------

    def _is_us_eligible(self, location_text):
        """Return True if a US H1B/OPT/H4 EAD candidate can apply."""
        if not location_text:
            return True  # benefit of the doubt

        loc = location_text.lower().strip()

        # Reject if it names a non-US region ONLY (unless US also mentioned)
        has_us = any(kw in loc for kw in US_LOCATION_KEYWORDS)
        has_eu = any(kw in loc for kw in EU_LOCATION_KEYWORDS)
        has_non_us = any(kw in loc for kw in NON_US_REGIONS)

        if has_us:
            return True  # US explicitly mentioned -> allow
        if has_eu or has_non_us:
            return False  # Region-restricted without US -> reject

        # No keyword hit -> default to allow (many jobs say "Remote" only)
        return True

    # ---------------------------------------------------------------
    # Dedupe + insert
    # ---------------------------------------------------------------

    def _insert_job(self, conn, cur, source, job_data):
        """
        Insert one job. Returns 'inserted' | 'skipped' | 'error'.

        Maps to actual charvak_jobs schema:
          job_id, title, company, job_type, location, salary, description,
          skills, posted_by, posted_date, status, applications_count,
          created_at, source, external_job_id, raw_json, is_us_eligible
        """
        external_id = job_data.get("external_job_id")
        if not external_id:
            return "error"

        try:
            cur.execute("""
                INSERT INTO charvak_jobs
                    (job_id, title, company, job_type, location, salary,
                     description, skills, posted_by, posted_date, status,
                     source, external_job_id, raw_json, is_us_eligible,
                     created_at)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                     %s, %s, %s, %s, NOW())
                ON CONFLICT (source, external_job_id) WHERE external_job_id IS NOT NULL DO NOTHING
            """, (
                f"JOB-{source[:3].upper()}-{external_id[:20]}",
                job_data.get("title", "")[:200],
                job_data.get("company", "")[:150],
                job_data.get("job_type", "Permanent")[:50],
                job_data.get("location", "Remote")[:200],
                job_data.get("salary", "")[:100],
                (job_data.get("description", "") or "")[:8000],
                job_data.get("skills", "")[:500],
                source,  # posted_by = source name
                datetime.now(timezone.utc).isoformat()[:19],
                "active",
                source,
                external_id,
                json.dumps(job_data.get("raw_json", {})),
                job_data.get("is_us_eligible", True),
            ))
            return "inserted" if cur.rowcount > 0 else "skipped"
        except Exception as e:
            logger.warning(f"_insert_job error ({source}/{external_id}): {e}")
            return "error"

    # ---------------------------------------------------------------
    # Remotive adapter
    # ---------------------------------------------------------------

    def ingest_remotive(self, limit=100):
        """
        Fetch jobs from Remotive API. Free, no auth.
        Docs: https://remotive.com/api/remote-jobs

        Returns: {status, fetched, inserted, skipped, errors}
        """
        result = {"status": "success", "fetched": 0, "inserted": 0, "skipped": 0, "errors": 0}
        try:
            resp = requests.get(
                "https://remotive.com/api/remote-jobs",
                params={"category": "software-dev", "limit": limit},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            jobs = data.get("jobs", [])
            result["fetched"] = len(jobs)

            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            for raw in jobs:
                location = raw.get("candidate_required_location", "")
                is_eligible = self._is_us_eligible(location)

                tags = raw.get("tags", [])
                skills_str = ", ".join(tags[:10]) if tags else ""
                job_data = {
                    "external_job_id": str(raw.get("slug", raw.get("url", "")))[:100],
                    "title": raw.get("title", ""),
                    "company": raw.get("company_name", ""),
                    "location": location,
                    "description": raw.get("description", ""),
                    "job_type": (raw.get("job_type", "") or "Contract")[:50],
                    "salary": (raw.get("salary", "") or "")[:100],
                    "skills": skills_str,
                    "is_us_eligible": is_eligible,
                    "raw_json": {
                        "url": raw.get("url", ""),
                        "salary": raw.get("salary", ""),
                        "job_type": raw.get("job_type", ""),
                        "category": raw.get("category", ""),
                        "publication_date": raw.get("publication_date", ""),
                        "tags": tags,
                    },
                }
                r = self._insert_job(conn, cur, "remotive", job_data)
                if r == "inserted":
                    result["inserted"] += 1
                elif r == "skipped":
                    result["skipped"] += 1
                else:
                    result["errors"] += 1

            conn.commit()
            cur.close()
            conn.close()

            self._update_source_status("remotive", "success", None,
                                       result["fetched"], result["inserted"])
        except Exception as e:
            logger.error(f"ingest_remotive failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)[:200]
            self._update_source_status("remotive", "error", str(e)[:200], 0, 0)

        return result

    # ---------------------------------------------------------------
    # Arbeitnow adapter
    # ---------------------------------------------------------------

    def ingest_arbeitnow(self, limit=100):
        """
        Fetch jobs from Arbeitnow API. Free, no auth.
        Docs: https://www.arbeitnow.com/api/job-board-api

        Returns: {status, fetched, inserted, skipped, errors}
        """
        result = {"status": "success", "fetched": 0, "inserted": 0, "skipped": 0, "errors": 0}
        try:
            resp = requests.get(
                "https://www.arbeitnow.com/api/job-board-api",
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            jobs = data.get("data", [])[:limit]
            result["fetched"] = len(jobs)

            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            for raw in jobs:
                location = raw.get("location", "")
                is_eligible = self._is_us_eligible(location)

                tags = raw.get("tags", [])
                skills_str = ", ".join(tags[:10]) if tags else ""
                job_data = {
                    "external_job_id": str(raw.get("slug", raw.get("url", "")))[:100],
                    "title": raw.get("title", ""),
                    "company": raw.get("company_name", ""),
                    "location": location,
                    "description": raw.get("description", ""),
                    "job_type": (raw.get("job_type", "") or "Contract")[:50],
                    "salary": (raw.get("salary", "") or "")[:100],
                    "skills": skills_str,
                    "is_us_eligible": is_eligible,
                    "raw_json": {
                        "url": raw.get("url", ""),
                        "salary": raw.get("salary", ""),
                        "job_type": raw.get("job_type", ""),
                        "category": raw.get("category", ""),
                        "publication_date": raw.get("publication_date", ""),
                        "tags": tags,
                    },
                }
                r = self._insert_job(conn, cur, "arbeitnow", job_data)
                if r == "inserted":
                    result["inserted"] += 1
                elif r == "skipped":
                    result["skipped"] += 1
                else:
                    result["errors"] += 1

            conn.commit()
            cur.close()
            conn.close()

            self._update_source_status("arbeitnow", "success", None,
                                       result["fetched"], result["inserted"])
        except Exception as e:
            logger.error(f"ingest_arbeitnow failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)[:200]
            self._update_source_status("arbeitnow", "error", str(e)[:200], 0, 0)

        return result

    # ---------------------------------------------------------------
    # Orchestration
    # ---------------------------------------------------------------

    def ingest_all(self):
        """Run all enabled sources."""
        return {
            "status": "success",
            "remotive": self.ingest_remotive(),
            "arbeitnow": self.ingest_arbeitnow(),
        }

    def sync_one(self, source_name):
        """Trigger a single source by name."""
        if source_name == "remotive":
            return self.ingest_remotive()
        elif source_name == "arbeitnow":
            return self.ingest_arbeitnow()
        return {"status": "error", "error": f"Unknown source: {source_name}"}

    # ---------------------------------------------------------------
    # Source registry
    # ---------------------------------------------------------------

    def list_sources(self):
        """Return all sources with their status + counts."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT source_name, display_name, api_url, attribution_text,
                       active, last_sync_at, last_sync_status, last_sync_error,
                       total_jobs_fetched, total_jobs_inserted
                FROM charvak_job_sources
                ORDER BY source_name
            """)
            rows = cur.fetchall()

            # Total actual rows per source from charvak_jobs
            cur.execute("""
                SELECT source, COUNT(*), COUNT(*) FILTER (WHERE is_us_eligible)
                FROM charvak_jobs
                WHERE source IS NOT NULL
                GROUP BY source
            """)
            counts = {r[0]: {"total": r[1], "us_eligible": r[2]} for r in cur.fetchall()}

            cur.close()
            conn.close()

            return {
                "status": "success",
                "sources": [
                    {
                        "source_name": r[0],
                        "display_name": r[1],
                        "api_url": r[2],
                        "attribution_text": r[3],
                        "active": r[4],
                        "last_sync_at": r[5].isoformat() if r[5] else None,
                        "last_sync_status": r[6],
                        "last_sync_error": r[7],
                        "total_jobs_fetched": r[8] or 0,
                        "total_jobs_inserted": r[9] or 0,
                        "actual_jobs_total": counts.get(r[0], {}).get("total", 0),
                        "actual_jobs_us_eligible": counts.get(r[0], {}).get("us_eligible", 0),
                    }
                    for r in rows
                ],
            }
        except Exception as e:
            logger.error(f"list_sources failed: {e}")
            return {"status": "error", "error": str(e)}

    def _update_source_status(self, source_name, status, error, fetched, inserted):
        """Update the source registry with the last sync result."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE charvak_job_sources
                SET last_sync_at = NOW(),
                    last_sync_status = %s,
                    last_sync_error = %s,
                    total_jobs_fetched = %s,
                    total_jobs_inserted = COALESCE(total_jobs_inserted, 0) + %s
                WHERE source_name = %s
            """, (status, error, fetched, inserted, source_name))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.warning(f"_update_source_status failed: {e}")


# Singleton
job_ingest_engine = JobIngestEngine()