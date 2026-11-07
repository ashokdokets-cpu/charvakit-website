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
import hashlib
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

    def _is_tech_role(self, title, skills):
        """
        Return True if this job looks like a tech role.
        Drops nurses, accountants, wedding coordinators, etc. before
        they hit the expensive 108G bench-relevance filter.

        Matches on title keywords first (primary signal), then falls back
        to skill tags if title is ambiguous.
        """
        t = (title or "").lower()

        # Primary: title keywords
        TITLE_KEYWORDS = [
            "engineer", "developer", "programmer", "architect",
            "devops", "sre", "site reliability", "platform",
            "data scien", "data engineer", "data analyst",
            "machine learning", "ml engineer", "ai engineer",
            "artificial intelligence",
            "backend", "frontend", "full-stack", "fullstack", "full stack",
            "software", "web dev", "mobile dev",
            "ios engineer", "android engineer",
            "python", "java engineer", "javascript",
            "golang", "go engineer", "rust engineer",
            "react engineer", "node engineer",
            "qa engineer", "test engineer", "sdet",
            "systems engineer", "security engineer",
            "cloud engineer", "infrastructure engineer",
            "tech lead", "technical lead", "engineering manager",
            "cto", "vp engineering", "head of engineering",
            "computer vision", "nlp engineer", "llm",
            "blockchain engineer", "smart contract",
            "site reliability engineer",
        ]
        if any(kw in t for kw in TITLE_KEYWORDS):
            return True

        # Secondary: check skills if we got an array of tags
        if skills:
            if isinstance(skills, str):
                skill_list = [s.strip().lower() for s in skills.split(",")]
            else:
                skill_list = [str(s).strip().lower() for s in skills]

            TECH_SKILLS = {
                "python", "java", "javascript", "typescript", "golang", "go",
                "rust", "ruby", "php", "c++", "c#", "kotlin", "swift", "scala",
                "react", "vue", "angular", "node", "django", "flask", "fastapi",
                "rails", "spring", "express",
                "aws", "gcp", "azure", "kubernetes", "docker", "terraform",
                "ansible", "jenkins", "ci/cd",
                "sql", "postgres", "postgresql", "mysql", "mongodb", "redis",
                "elasticsearch", "kafka",
                "machine learning", "ml", "ai", "deep learning",
                "tensorflow", "pytorch", "pandas", "numpy",
                "devops", "sre", "microservices",
                "graphql", "rest api", "api",
            }
            # Need at least 2 tech-skill hits to count as tech (avoid false positives)
            hits = sum(1 for s in skill_list if s in TECH_SKILLS)
            if hits >= 2:
                return True

        return False
    def _is_us_eligible(self, location_text):
        """
        US/Canada-only filter. Returns True only if location is US, Canada,
        remote/worldwide, or unmarked. All other regions rejected.
        """
        if not location_text:
            return True

        loc = location_text.lower().strip()

        # 1. Reject explicit non-US/CA signals (unless worldwide/remote)
        GLOBAL = ["worldwide", "anywhere", "global", "remote"]
        has_global = any(kw in loc for kw in GLOBAL)

        NON_US_CA = [
            "germany", "deutschland", "berlin", "munich", "münchen", "hamburg",
            "frankfurt", "cologne", "köln", "düsseldorf", "stuttgart", "leipzig",
            "uk", "united kingdom", "london", "manchester", "edinburgh",
            "france", "paris", "lyon", "netherlands", "amsterdam", "rotterdam",
            "spain", "madrid", "barcelona", "italy", "milan", "rome",
            "poland", "warsaw", "krakow", "portugal", "lisbon", "porto",
            "ireland", "dublin", "sweden", "stockholm", "norway", "oslo",
            "denmark", "copenhagen", "finland", "helsinki", "austria", "vienna",
            "belgium", "brussels", "switzerland", "zurich", "zürich",
            "czech", "prague", "greece", "athens", "hungary", "budapest",
            "europe", "eu only", "emea",
            "india", "bangalore", "bengaluru", "mumbai", "delhi", "pune",
            "japan", "tokyo", "china", "shanghai", "beijing",
            "singapore", "hong kong", "uae", "dubai", "abu dhabi",
            "israel", "tel aviv", "asia", "apac",
            "australia", "sydney", "melbourne", "new zealand",
            "brazil", "são paulo", "south america", "latin america", "latam",
            "south africa", "johannesburg", "africa",
            "mexico", "mexico city", "argentina", "buenos aires",
            "russia", "moscow", "ukraine", "kyiv", "middle east",
        ]
        has_non_us_ca = any(kw in loc for kw in NON_US_CA)

        # 2. If clearly non-US/CA and no "worldwide/remote" escape → reject
        if has_non_us_ca and not has_global:
            return False

        # 3. Otherwise allow (US, Canada, remote, worldwide, or ambiguous)
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


        # ---- Session 108G: Bench-relevance filter ----
        from bench_jd_filter import bench_jd_filter
        raw_skills = job_data.get("skills", "")
        if isinstance(raw_skills, str):
            jd_skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
        else:
            jd_skills = raw_skills or []
        jd_for_filter = {
            "role_title": job_data.get("title", ""),
            "title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "location": job_data.get("location", ""),
            "skills_required": jd_skills,
            "work_auth_required": job_data.get("work_auth_required", "Any"),
            "rate_min": None,
            "rate_max": None,
            "raw_text": job_data.get("description", ""),
            "source": source,
        }
        is_relevant, reason, best_cand, _, overlap = bench_jd_filter.is_relevant(jd_for_filter)
        if not is_relevant:
            return "skipped_relevance"
        # ---- End filter ----

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
                f"JOB-{source[:3].upper()}-{hashlib.md5(str(external_id).encode()).hexdigest()[:12]}",
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
        result = {"status": "success", "fetched": 0, "inserted": 0, "skipped": 0, "skipped_relevance": 0, "errors": 0}
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
                elif r == "skipped_relevance":
                    result["skipped_relevance"] += 1
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
        result = {"status": "success", "fetched": 0, "inserted": 0, "skipped": 0, "skipped_relevance": 0, "errors": 0}
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
                elif r == "skipped_relevance":
                    result["skipped_relevance"] += 1
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
        """Run all enabled sources (Session 108B: 8 total)."""
        return {
            "status": "success",
            "remotive": self.ingest_remotive(),
            "arbeitnow": self.ingest_arbeitnow(),
            "remoteok": self.ingest_remoteok(),
            "weworkremotely": self.ingest_weworkremotely(),
            "jobicy": self.ingest_jobicy(),
            "himalayas": self.ingest_himalayas(),
            "themuse": self.ingest_themuse(),
            "hn_hiring": self.ingest_hn_hiring(),
        }

    def sync_one(self, source_name):
        """Trigger a single source by name (Session 108B: 8 total)."""
        dispatch = {
            "remotive": self.ingest_remotive,
            "arbeitnow": self.ingest_arbeitnow,
            "remoteok": self.ingest_remoteok,
            "weworkremotely": self.ingest_weworkremotely,
            "jobicy": self.ingest_jobicy,
            "himalayas": self.ingest_himalayas,
            "themuse": self.ingest_themuse,
            "hn_hiring": self.ingest_hn_hiring,
        }
        fn = dispatch.get(source_name)
        if not fn:
            return {"status": "error", "error": f"Unknown source: {source_name}"}
        return fn()

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


    # ---------------------------------------------------------------
    # RemoteOK adapter (Session 108B)
    # ---------------------------------------------------------------
    # API: https://remoteok.com/api
    # Returns JSON array; first element is legal metadata, skip it.
    # Rate limit: be polite, 1 sync/day is plenty.

    def ingest_remoteok(self, limit=100):
        """Fetch jobs from RemoteOK. Free, no auth. Attribution required."""
        result = {"status": "success", "fetched": 0, "inserted": 0, "skipped": 0, "skipped_relevance": 0, "errors": 0}
        try:
            resp = requests.get(
                "https://remoteok.com/api",
                headers={"User-Agent": "Charvak/1.0 (job aggregation; +https://charvakit.com)"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            # First element is metadata: {legal: "...", last_updated: "..."}
            jobs = data[1:] if isinstance(data, list) and len(data) > 0 else []
            jobs = jobs[:limit]
            result["fetched"] = len(jobs)

            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            for raw in jobs:
                location = raw.get("location", "") or "Remote"
                is_eligible = self._is_us_eligible(location)

                tags = raw.get("tags", []) or []
                skills_str = ", ".join(tags[:15]) if tags else ""

                # RemoteOK salary: salary_min/salary_max (sometimes strings)
                salary_min = raw.get("salary_min")
                salary_max = raw.get("salary_max")
                salary_str = ""
                if salary_min and salary_max:
                    try:
                        salary_str = f"${int(float(salary_min)):,} - ${int(float(salary_max)):,}"
                    except (ValueError, TypeError):
                        salary_str = f"{salary_min} - {salary_max}"
                elif salary_min:
                    salary_str = f"${salary_min}+"

                job_data = {
                    "external_job_id": str(raw.get("id", raw.get("slug", "")))[:100],
                    "title": raw.get("position", raw.get("role", "")),
                    "company": raw.get("company", ""),
                    "location": location,
                    "description": raw.get("description", ""),
                    "job_type": "Contract",
                    "salary": salary_str[:100],
                    "skills": skills_str[:500],
                    "is_us_eligible": is_eligible,
                    "raw_json": {
                        "url": raw.get("url", ""),
                        "apply_url": raw.get("apply_url", ""),
                        "date": raw.get("date", ""),
                        "tags": tags,
                        "logo": raw.get("company_logo", ""),
                    },
                }
                # Pre-filter: skip non-tech roles before 108G runs
                if not self._is_tech_role(raw.get("position", raw.get("role", "")), tags):
                    result.setdefault("skipped_non_tech", 0)
                    result["skipped_non_tech"] += 1
                    result["fetched"] -= 1  # don't count as fetched
                    continue
                r = self._insert_job(conn, cur, "remoteok", job_data)
                if r == "inserted":
                    result["inserted"] += 1
                elif r == "skipped":
                    result["skipped"] += 1
                elif r == "skipped_relevance":
                    result["skipped_relevance"] += 1
                else:
                    result["errors"] += 1

            conn.commit()
            cur.close()
            conn.close()
            self._update_source_status("remoteok", "success", None,
                                       result["fetched"], result["inserted"])
        except Exception as e:
            logger.error(f"ingest_remoteok failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)[:200]
            self._update_source_status("remoteok", "error", str(e)[:200], 0, 0)

        return result

    # ---------------------------------------------------------------
    # We Work Remotely adapter (Session 108B)
    # ---------------------------------------------------------------
    # RSS feeds per category. XML parsing via xml.etree.
    # Attribution required.

    def ingest_weworkremotely(self, limit=100):
        """Fetch jobs from WWR RSS feeds. Free, no auth. Attribution required."""
        result = {"status": "success", "fetched": 0, "inserted": 0, "skipped": 0, "skipped_relevance": 0, "errors": 0}
        try:
            import xml.etree.ElementTree as ET

            FEEDS = [
                "https://weworkremotely.com/categories/remote-programming-jobs.rss",
                "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
                "https://weworkremotely.com/categories/remote-design-jobs.rss",
            ]

            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            seen_ids = set()

            for feed_url in FEEDS:
                if result["fetched"] >= limit:
                    break
                try:
                    resp = requests.get(
                        feed_url,
                        headers={"User-Agent": "Charvak/1.0 (job aggregation; +https://charvakit.com)"},
                        timeout=30,
                    )
                    resp.raise_for_status()
                    root = ET.fromstring(resp.content)
                    items = root.findall(".//item")

                    for item in items:
                        if result["fetched"] >= limit:
                            break
                        title_raw = (item.findtext("title") or "").strip()
                        link = (item.findtext("link") or "").strip()
                        desc = (item.findtext("description") or "").strip()
                        region = (item.findtext("{http://www.weworkremotely.com}region") or "").strip()

                        if not title_raw or not link:
                            continue

                        # WWR title format: "Company: Job Title"
                        if ":" in title_raw:
                            company, title = title_raw.split(":", 1)
                            company = company.strip()
                            title = title.strip()
                        else:
                            company = ""
                            title = title_raw

                        # Use link slug as stable external id
                        ext_id = link.rstrip("/").split("/")[-1][:100]
                        if ext_id in seen_ids:
                            continue
                        seen_ids.add(ext_id)

                        # Region hint for US filter
                        location = "Remote"
                        if region:
                            location = f"Remote - {region}"

                        is_eligible = self._is_us_eligible(location)
                        result["fetched"] += 1

                        # Strip HTML from description
                        import re as _re
                        desc_clean = _re.sub(r"<[^>]+>", " ", desc)[:8000]

                        job_data = {
                            "external_job_id": ext_id,
                            "title": title[:200],
                            "company": company[:150],
                            "location": location[:200],
                            "description": desc_clean,
                            "job_type": "Contract",
                            "salary": "",
                            "skills": "",
                            "is_us_eligible": is_eligible,
                            "raw_json": {
                                "url": link,
                                "feed": feed_url,
                                "region": region,
                            },
                        }
                        # Pre-filter: skip non-tech roles
                        if not self._is_tech_role(title, None):
                            result.setdefault("skipped_non_tech", 0)
                            result["skipped_non_tech"] += 1
                            result["fetched"] -= 1
                            continue
                        r = self._insert_job(conn, cur, "weworkremotely", job_data)
                        if r == "inserted":
                            result["inserted"] += 1
                        elif r == "skipped":
                            result["skipped"] += 1
                        elif r == "skipped_relevance":
                            result["skipped_relevance"] += 1
                        else:
                            result["errors"] += 1
                except Exception as feed_err:
                    logger.warning(f"WWR feed failed ({feed_url}): {feed_err}")
                    continue

            conn.commit()
            cur.close()
            conn.close()
            self._update_source_status("weworkremotely", "success", None,
                                       result["fetched"], result["inserted"])
        except Exception as e:
            logger.error(f"ingest_weworkremotely failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)[:200]
            self._update_source_status("weworkremotely", "error", str(e)[:200], 0, 0)

        return result

    # ---------------------------------------------------------------
    # Jobicy adapter (Session 108B)
    # ---------------------------------------------------------------
    # API: https://jobicy.com/api/v2/remote-jobs
    # JSON: {jobs: [...]}, paginated via count + page. Attribution required.

    def ingest_jobicy(self, limit=100):
        """Fetch jobs from Jobicy. Free, no auth. Attribution required."""
        result = {"status": "success", "fetched": 0, "inserted": 0, "skipped": 0, "skipped_relevance": 0, "errors": 0}
        try:
            # Jobicy: /api/v2/remote-jobs?count=X&geo=usa
            resp = requests.get(
                "https://jobicy.com/api/v2/remote-jobs",
                params={"count": min(limit, 50), "geo": "usa"},
                headers={"User-Agent": "Charvak/1.0 (job aggregation; +https://charvakit.com)"},
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
                location = raw.get("jobGeo", "") or "Remote"
                is_eligible = self._is_us_eligible(location)

                # Jobicy returns jobIndustry and jobType as arrays
                industries = raw.get("jobIndustry", []) or []
                types = raw.get("jobType", []) or []
                skills_str = ", ".join(industries[:10]) if industries else ""

                salary_min = raw.get("annualSalaryMin")
                salary_max = raw.get("annualSalaryMax")
                currency = raw.get("salaryCurrency", "USD")
                salary_str = ""
                if salary_min and salary_max:
                    salary_str = f"{currency} {salary_min} - {salary_max}"

                job_data = {
                    "external_job_id": str(raw.get("id", ""))[:100],
                    "title": raw.get("jobTitle", ""),
                    "company": raw.get("companyName", ""),
                    "location": location,
                    "description": raw.get("jobDescription", ""),
                    "job_type": (types[0] if types else "Contract")[:50],
                    "salary": salary_str[:100],
                    "skills": skills_str[:500],
                    "is_us_eligible": is_eligible,
                    "raw_json": {
                        "url": raw.get("url", ""),
                        "jobLevel": raw.get("jobLevel", ""),
                        "jobExcerpt": raw.get("jobExcerpt", ""),
                        "pubDate": raw.get("pubDate", ""),
                        "companyLogo": raw.get("companyLogo", ""),
                    },
                }
                # Pre-filter: skip non-tech roles
                if not self._is_tech_role(raw.get("jobTitle", ""), industries):
                    result.setdefault("skipped_non_tech", 0)
                    result["skipped_non_tech"] += 1
                    result["fetched"] -= 1
                    continue
                r = self._insert_job(conn, cur, "jobicy", job_data)
                if r == "inserted":
                    result["inserted"] += 1
                elif r == "skipped":
                    result["skipped"] += 1
                elif r == "skipped_relevance":
                    result["skipped_relevance"] += 1
                else:
                    result["errors"] += 1

            conn.commit()
            cur.close()
            conn.close()
            self._update_source_status("jobicy", "success", None,
                                       result["fetched"], result["inserted"])
        except Exception as e:
            logger.error(f"ingest_jobicy failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)[:200]
            self._update_source_status("jobicy", "error", str(e)[:200], 0, 0)

        return result

    # ---------------------------------------------------------------
    # Himalayas adapter (Session 108B)
    # ---------------------------------------------------------------
    # API: https://himalayas.app/jobs/api
    # JSON: {jobs: [...]}. Free, no auth. Attribution required.

    def ingest_himalayas(self, limit=100):
        """Fetch jobs from Himalayas. Free, no auth. Attribution required."""
        result = {"status": "success", "fetched": 0, "inserted": 0, "skipped": 0, "skipped_relevance": 0, "errors": 0}
        try:
            resp = requests.get(
                "https://himalayas.app/jobs/api",
                params={"limit": min(limit, 100)},
                headers={"User-Agent": "Charvak/1.0 (job aggregation; +https://charvakit.com)"},
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
                location = raw.get("locationRestrictions", [{}])
                if isinstance(location, list) and location:
                    loc_str = ", ".join(str(x) for x in location if x)
                else:
                    loc_str = "Remote"
                is_eligible = self._is_us_eligible(loc_str)

                categories = raw.get("categories", []) or []
                skills_str = ", ".join(categories[:10]) if categories else ""

                min_sal = raw.get("minSalary")
                max_sal = raw.get("maxSalary")
                salary_str = ""
                if min_sal and max_sal:
                    salary_str = f"${min_sal:,} - ${max_sal:,}"

                job_data = {
                    "external_job_id": str(raw.get("guid", raw.get("id", "")))[:100],
                    "title": raw.get("title", ""),
                    "company": raw.get("companyName", ""),
                    "location": loc_str[:200],
                    "description": raw.get("description", ""),
                    "job_type": raw.get("employmentType", "Contract")[:50],
                    "salary": salary_str[:100],
                    "skills": skills_str[:500],
                    "is_us_eligible": is_eligible,
                    "raw_json": {
                        "url": raw.get("applicationLink", raw.get("guid", "")),
                        "companyLogo": raw.get("companyLogo", ""),
                        "pubDate": raw.get("pubDate", ""),
                        "categories": categories,
                    },
                }
                # Pre-filter: skip non-tech roles
                if not self._is_tech_role(raw.get("title", ""), categories):
                    result.setdefault("skipped_non_tech", 0)
                    result["skipped_non_tech"] += 1
                    result["fetched"] -= 1
                    continue
                r = self._insert_job(conn, cur, "himalayas", job_data)
                if r == "inserted":
                    result["inserted"] += 1
                elif r == "skipped":
                    result["skipped"] += 1
                elif r == "skipped_relevance":
                    result["skipped_relevance"] += 1
                else:
                    result["errors"] += 1

            conn.commit()
            cur.close()
            conn.close()
            self._update_source_status("himalayas", "success", None,
                                       result["fetched"], result["inserted"])
        except Exception as e:
            logger.error(f"ingest_himalayas failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)[:200]
            self._update_source_status("himalayas", "error", str(e)[:200], 0, 0)

        return result

    # ---------------------------------------------------------------
    # The Muse adapter (Session 108B)
    # ---------------------------------------------------------------
    # API: https://www.themuse.com/api/public/jobs
    # JSON: {results: [...], page_count: N}. Free, no auth needed for
    # public search. Attribution required.

    def ingest_themuse(self, limit=100):
        """Fetch jobs from The Muse. Free, no auth. Attribution required."""
        result = {"status": "success", "fetched": 0, "inserted": 0, "skipped": 0, "skipped_relevance": 0, "errors": 0}
        try:
            resp = requests.get(
                "https://www.themuse.com/api/public/jobs",
                params={"page": 1, "category": "Software Engineering", "level": "Mid Level"},
                headers={"User-Agent": "Charvak/1.0 (job aggregation; +https://charvakit.com)"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            jobs = data.get("results", [])
            result["fetched"] = len(jobs)

            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            for raw in jobs:
                locations = raw.get("locations", [])
                # The Muse locations: [{name: "Remote"}, {name: "New York, NY"}]
                loc_names = [l.get("name", "") for l in locations if l.get("name")] if locations else []
                loc_str = ", ".join(loc_names) if loc_names else "Remote"
                is_eligible = self._is_us_eligible(loc_str)

                categories = raw.get("categories", []) or []
                skills_str = ", ".join(c.get("name", "") for c in categories[:10] if c.get("name"))

                company = (raw.get("company") or {}).get("name", "")
                levels = raw.get("levels", []) or []
                job_type = "Contract"
                if levels:
                    job_type = (levels[0].get("name") or "Contract")[:50]

                # Description is HTML; strip tags
                import re as _re
                desc_html = raw.get("contents", "")
                desc_clean = _re.sub(r"<[^>]+>", " ", desc_html)[:8000]

                job_data = {
                    "external_job_id": str(raw.get("id", ""))[:100],
                    "title": raw.get("name", ""),
                    "company": company,
                    "location": loc_str[:200],
                    "description": desc_clean,
                    "job_type": job_type,
                    "salary": "",
                    "skills": skills_str[:500],
                    "is_us_eligible": is_eligible,
                    "raw_json": {
                        "url": (raw.get("refs") or {}).get("landing_page", ""),
                        "publication_date": raw.get("publication_date", ""),
                        "company_logo": (raw.get("company") or {}).get("logo", ""),
                        "categories": [c.get("name", "") for c in categories],
                        "levels": [l.get("name", "") for l in levels],
                    },
                }
                # Pre-filter: skip non-tech roles
                if not self._is_tech_role(raw.get("name", ""), [c.get("name", "") for c in categories]):
                    result.setdefault("skipped_non_tech", 0)
                    result["skipped_non_tech"] += 1
                    result["fetched"] -= 1
                    continue
                r = self._insert_job(conn, cur, "themuse", job_data)
                if r == "inserted":
                    result["inserted"] += 1
                elif r == "skipped":
                    result["skipped"] += 1
                elif r == "skipped_relevance":
                    result["skipped_relevance"] += 1
                else:
                    result["errors"] += 1

            conn.commit()
            cur.close()
            conn.close()
            self._update_source_status("themuse", "success", None,
                                       result["fetched"], result["inserted"])
        except Exception as e:
            logger.error(f"ingest_themuse failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)[:200]
            self._update_source_status("themuse", "error", str(e)[:200], 0, 0)

        return result

    # ---------------------------------------------------------------
    # HN Who is Hiring adapter (Session 108B)
    # ---------------------------------------------------------------
    # Uses Algolia HN API to fetch the latest "Ask HN: Who is hiring?"
    # thread, then parses top-level comments as JDs.
    # No auth. Attribution required (link back to HN comment).

    def ingest_hn_hiring(self, limit=100):
        """Fetch comments from the latest 'Ask HN: Who is hiring?' thread."""
        result = {"status": "success", "fetched": 0, "inserted": 0, "skipped": 0, "skipped_relevance": 0, "errors": 0}
        try:
            import re as _re

            # Step 1: Find the latest "Ask HN: Who is hiring?" story by author whoishiring
            search_resp = requests.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={"query": "Ask HN: Who is hiring?", "tags": "story", "hitsPerPage": 5},
                timeout=30,
            )
            search_resp.raise_for_status()
            search_data = search_resp.json()
            hits = search_data.get("hits", [])
            # Filter to entries actually authored by "whoishiring" and titled correctly
            candidates = [h for h in hits if h.get("author") == "whoishiring"]
            if not candidates:
                raise ValueError("No 'whoishiring' thread found in recent stories")
            latest = candidates[0]
            story_id = latest.get("objectID")

            # Step 2: Fetch the story's top-level comments
            story_resp = requests.get(
                f"https://hn.algolia.com/api/v1/items/{story_id}",
                timeout=30,
            )
            story_resp.raise_for_status()
            story_data = story_resp.json()
            comments = story_data.get("children", [])

            # Limit and filter deleted/dead
            comments = [c for c in comments if c.get("text") and not c.get("deleted")][:limit]
            result["fetched"] = len(comments)

            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            for idx, comment in enumerate(comments):
                text_html = comment.get("text", "")
                # Strip HTML tags
                text_clean = _re.sub(r"<[^>]+>", " ", text_html)
                text_clean = _re.sub(r"\s+", " ", text_clean).strip()

                if not text_clean:
                    continue

                # HN whoishiring posts have a common format:
                # "Company | Role | Location | ..."  or a paragraph.
                # Heuristic: parse the first line for company/title/location
                first_line = text_clean.split("\n")[0][:300]
                parts = [p.strip() for p in first_line.split("|")]

                company = ""
                title = ""
                location = ""

                if len(parts) >= 2:
                    company = parts[0][:150]
                    title = parts[1][:200]
                    # Find a location-like part
                    for p in parts[2:5]:
                        p_lower = p.lower()
                        if any(k in p_lower for k in ["remote", "usa", "us", "united states", "new york", "san francisco", "seattle", "austin", "boston", "anywhere", "worldwide", "global"]):
                            location = p[:200]
                            break
                    if not location:
                        location = "Remote"

                # If we couldn't parse company/title, skip — no useful JD
                if not title or len(title) < 3:
                    # Try to salvage first 100 chars as title
                    if len(text_clean) > 20:
                        title = text_clean[:200]
                        company = "HN Who is Hiring"
                        location = "Remote"
                    else:
                        result["errors"] += 1
                        continue

                is_eligible = self._is_us_eligible(location)

                # Extract skills heuristically: common tech keywords in the text
                tech_keywords = [
                    "python", "java", "javascript", "typescript", "go", "rust",
                    "ruby", "php", "c++", "c#", "kotlin", "swift", "scala",
                    "react", "vue", "angular", "node", "django", "flask",
                    "aws", "gcp", "azure", "kubernetes", "docker", "terraform",
                    "sql", "postgres", "mysql", "mongodb", "redis",
                    "machine learning", "ml", "ai", "data science",
                ]
                found_skills = []
                lower_text = text_clean.lower()
                for kw in tech_keywords:
                    if kw in lower_text:
                        found_skills.append(kw)
                skills_str = ", ".join(found_skills[:15])

                ext_id = f"hn-{comment.get('id', idx)}"

                job_data = {
                    "external_job_id": ext_id[:100],
                    "title": title[:200],
                    "company": company[:150],
                    "location": location[:200],
                    "description": text_clean[:8000],
                    "job_type": "Contract",
                    "salary": "",
                    "skills": skills_str[:500],
                    "is_us_eligible": is_eligible,
                    "raw_json": {
                        "hn_comment_id": comment.get("id"),
                        "hn_url": f"https://news.ycombinator.com/item?id={comment.get('id')}",
                        "author": comment.get("author", ""),
                        "created_at": comment.get("created_at", ""),
                        "thread_id": story_id,
                    },
                }
                # Pre-filter: skip non-tech roles
                if not self._is_tech_role(title, found_skills):
                    result.setdefault("skipped_non_tech", 0)
                    result["skipped_non_tech"] += 1
                    result["fetched"] -= 1
                    continue
                r = self._insert_job(conn, cur, "hn_hiring", job_data)
                if r == "inserted":
                    result["inserted"] += 1
                elif r == "skipped":
                    result["skipped"] += 1
                elif r == "skipped_relevance":
                    result["skipped_relevance"] += 1
                else:
                    result["errors"] += 1

            conn.commit()
            cur.close()
            conn.close()
            self._update_source_status("hn_hiring", "success", None,
                                       result["fetched"], result["inserted"])
        except Exception as e:
            logger.error(f"ingest_hn_hiring failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)[:200]
            self._update_source_status("hn_hiring", "error", str(e)[:200], 0, 0)

        return result
# Singleton
job_ingest_engine = JobIngestEngine()
