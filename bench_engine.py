"""
Bench Candidate Profile Engine
Session 2 — Bench-Placement Agent

Manages H1B/OPT bench candidates with US staffing fields.
"""

import os
import json
import logging
import csv
import io
import uuid
from typing import Dict, List
import psycopg2
from dotenv import load_dotenv

# Match database.py's env-loading order:
# 1. .env.local first (dev override), with override=True
# 2. .env fallback (prod values)
load_dotenv(".env.local", override=True)
load_dotenv()

logger = logging.getLogger(__name__)


class BenchEngine:
    VALID_WORK_AUTH = ['H1B', 'OPT', 'GC', 'USC', 'TN', 'H4-EAD', 'L2-EAD']
    VALID_AVAILABILITY = ['immediate', '2 weeks', '1 month', 'on project']

    def __init__(self):
        self._ensure_columns()

    def _ensure_columns(self):
        """Self-healing DDL — adds missing columns on first use.
        Split into individual ALTERs because Postgres does not reliably
        support multi-column ADD COLUMN IF NOT EXISTS.
        Note: 'availability' already exists as a legacy column, skip it.
        """
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()
            statements = [
                "ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS work_auth_status TEXT",
                "ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS rate_min NUMERIC",
                "ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS rate_max NUMERIC",
                "ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS visa_expiry DATE",
                "ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS has_verified_cert BOOLEAN DEFAULT FALSE",
                "ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS bench_since TIMESTAMP",
                "ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS employer_email TEXT",
                "ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS employer_phone TEXT",
            ]
            for stmt in statements:
                cur.execute(stmt)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"_ensure_columns failed: {e}")

    def _safe_str(self, data, key, default=""):
        """Return stripped string, treating None and '' the same."""
        v = data.get(key)
        if v is None:
            return default
        return str(v).strip()

    def _safe_num(self, data, key):
        """Return float or None."""
        v = data.get(key)
        if v is None or v == "":
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    def _safe_int(self, data, key):
        """Return int or None."""
        v = data.get(key)
        if v is None or v == "":
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

    def add_to_bench(self, candidate_data: Dict) -> Dict:
        """
        Add (or update) a candidate as bench.
        Requires at minimum: name, work_auth_status.

        email is the UNIQUE identifier per candidate. If blank or same as
        employer_email, a unique internal email is auto-generated so multiple
        bench candidates can coexist with the same employer email.

        employer_email and employer_phone default to env vars.
        """
        name = self._safe_str(candidate_data, "name")
        work_auth = self._safe_str(candidate_data, "work_auth_status")

        # Employer contact info
        employer_email = (
            self._safe_str(candidate_data, "employer_email")
            or os.getenv("EMPLOYER_EMAIL", "ashokcquent@gmail.com")
        ).lower()
        employer_phone = (
            self._safe_str(candidate_data, "employer_phone")
            or os.getenv("EMPLOYER_PHONE", "847-262-4000")
        )

        # Candidate's unique email (auto-generate if blank or same as employer)
        email = self._safe_str(candidate_data, "email").lower()
        if not email or email == employer_email:
            email = f"bench-{uuid.uuid4().hex[:12]}@charvak.internal"

        if not name:
            return {"status": "error", "message": "name is required"}
        if not work_auth:
            return {"status": "error", "message": "work_auth_status is required"}
        if work_auth not in self.VALID_WORK_AUTH:
            return {
                "status": "error",
                "message": f"work_auth_status must be one of: {', '.join(self.VALID_WORK_AUTH)}"
            }

        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()

            # Check if candidate exists
            cur.execute(
                "SELECT candidate_id FROM charvak_candidates WHERE email = %s",
                (email,)
            )
            existing = cur.fetchone()

            skills = candidate_data.get("skills") or []
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(",") if s.strip()]

            candidate_phone = self._safe_str(candidate_data, "phone") or None
            location = self._safe_str(candidate_data, "location") or None
            availability = self._safe_str(candidate_data, "availability") or None
            visa_expiry = self._safe_str(candidate_data, "visa_expiry") or None
            rate_min = self._safe_num(candidate_data, "rate_min")
            rate_max = self._safe_num(candidate_data, "rate_max")
            experience_years = self._safe_int(candidate_data, "experience_years")

            if existing:
                cur.execute("""
                    UPDATE charvak_candidates SET
                        name = %s,
                        work_auth_status = %s,
                        availability = %s,
                        rate_min = %s,
                        rate_max = %s,
                        visa_expiry = %s,
                        skills = %s,
                        experience_years = COALESCE(%s, experience_years),
                        phone = COALESCE(%s, phone),
                        location = COALESCE(%s, location),
                        employer_email = %s,
                        employer_phone = %s,
                        bench_since = COALESCE(bench_since, NOW()),
                        updated_at = NOW()
                    WHERE email = %s
                """, (
                    name, work_auth, availability,
                    rate_min, rate_max, visa_expiry,
                    json.dumps(skills),
                    experience_years,
                    candidate_phone, location,
                    employer_email, employer_phone,
                    email
                ))
                action = "updated"
            else:
                candidate_id = f"CAND-{uuid.uuid4().hex[:12].upper()}"
                cur.execute("""
                    INSERT INTO charvak_candidates (
                        candidate_id, name, email, phone, location, skills,
                        experience_years, work_auth_status, availability,
                        rate_min, rate_max, visa_expiry, bench_since,
                        employer_email, employer_phone, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, 'registered')
                """, (
                    candidate_id, name, email,
                    candidate_phone, location,
                    json.dumps(skills),
                    experience_years,
                    work_auth, availability,
                    rate_min, rate_max, visa_expiry,
                    employer_email, employer_phone
                ))
                action = "created"

            conn.commit()
            cur.close()
            conn.close()
            return {"status": "success", "action": action, "email": email}

        except Exception as e:
            logger.error(f"add_to_bench failed: {e}")
            return {"status": "error", "message": str(e)}

    def list_bench(self, work_auth: str = None, availability: str = None,
                   skills: str = None, rate_max: float = None,
                   search: str = None, limit: int = 100, offset: int = 0) -> Dict:
        """List bench candidates with filters."""
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()

            where = ["bench_since IS NOT NULL"]
            params = []

            if work_auth and work_auth != "Any":
                where.append("work_auth_status = %s")
                params.append(work_auth)

            if availability and availability != "Any":
                where.append("availability = %s")
                params.append(availability)

            if skills:
                where.append("skills::text ILIKE %s")
                params.append(f"%{skills}%")

            if rate_max is not None:
                where.append("rate_max <= %s")
                params.append(rate_max)

            if search:
                where.append("(name ILIKE %s OR email ILIKE %s OR skills::text ILIKE %s)")
                params.extend([f"%{search}%"] * 3)

            where_clause = " AND ".join(where)

            cur.execute(f"SELECT COUNT(*) FROM charvak_candidates WHERE {where_clause}", params)
            total = cur.fetchone()[0]

            cur.execute(f"""
                SELECT candidate_id, name, email, phone, location, skills,
                       experience_years, work_auth_status, availability,
                       rate_min, rate_max, visa_expiry, bench_since, has_verified_cert,
                       employer_email, employer_phone
                FROM charvak_candidates
                WHERE {where_clause}
                ORDER BY bench_since DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])

            rows = cur.fetchall()
            cur.close()
            conn.close()

            candidates = []
            for r in rows:
                skills_val = r[5] if isinstance(r[5], list) else (json.loads(r[5]) if r[5] else [])
                candidates.append({
                    "candidate_id": r[0],
                    "name": r[1],
                    "email": r[2],
                    "phone": r[3],
                    "location": r[4],
                    "skills": skills_val,
                    "experience_years": r[6],
                    "work_auth_status": r[7],
                    "availability": r[8],
                    "rate_min": float(r[9]) if r[9] else None,
                    "rate_max": float(r[10]) if r[10] else None,
                    "visa_expiry": r[11].isoformat() if r[11] else None,
                    "bench_since": r[12].isoformat() if r[12] else None,
                    "has_verified_cert": r[13],
                    "employer_email": r[14],
                    "employer_phone": r[15]
                })

            return {"status": "success", "candidates": candidates, "total": total}

        except Exception as e:
            logger.error(f"list_bench failed: {e}")
            return {"status": "error", "message": str(e)}

    def update_bench_candidate(self, email: str, updates: Dict) -> Dict:
        """Update specific fields."""
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()

            allowed = ['name', 'phone', 'location', 'availability', 'rate_min',
                       'rate_max', 'visa_expiry', 'work_auth_status', 'experience_years',
                       'skills', 'employer_email', 'employer_phone']
            sets = []
            params = []
            for k in allowed:
                if k in updates:
                    sets.append(f"{k} = %s")
                    val = updates[k]
                    # Convert Python list to JSON string for JSONB columns
                    if k == 'skills' and isinstance(val, list):
                        val = json.dumps(val)
                    params.append(val)

            if not sets:
                return {"status": "error", "message": "no valid fields to update"}

            params.append(email)
            cur.execute(
                f"UPDATE charvak_candidates SET {', '.join(sets)}, updated_at = NOW() WHERE email = %s",
                params
            )
            conn.commit()
            rows_affected = cur.rowcount
            cur.close()
            conn.close()

            if rows_affected == 0:
                return {"status": "error", "message": "candidate not found"}
            return {"status": "success"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def remove_from_bench(self, email: str) -> Dict:
        """Remove candidate from bench (keeps candidate record)."""
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()
            cur.execute("""
                UPDATE charvak_candidates
                SET bench_since = NULL, work_auth_status = NULL, availability = NULL
                WHERE email = %s
            """, (email,))
            conn.commit()
            rows = cur.rowcount
            cur.close()
            conn.close()
            return {"status": "success", "removed": rows}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def import_from_csv(self, csv_content: str) -> Dict:
        """Bulk import from CSV string."""
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            results = {"created": 0, "updated": 0, "errors": []}

            for row in reader:
                skills = row.get("skills", "").strip()
                if skills:
                    row["skills"] = [s.strip() for s in skills.split(",") if s.strip()]

                for field in ["rate_min", "rate_max"]:
                    if row.get(field):
                        try:
                            row[field] = float(row[field])
                        except (ValueError, TypeError):
                            row[field] = None

                if row.get("experience_years"):
                    try:
                        row["experience_years"] = int(row["experience_years"])
                    except (ValueError, TypeError):
                        row["experience_years"] = None

                result = self.add_to_bench(row)
                if result.get("status") == "success":
                    if result.get("action") == "created":
                        results["created"] += 1
                    else:
                        results["updated"] += 1
                else:
                    results["errors"].append({
                        "email": row.get("email"),
                        "error": result.get("message")
                    })

            return {"status": "success", "results": results}

        except Exception as e:
            logger.error(f"import_from_csv failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_bench_stats(self) -> Dict:
        """Aggregate stats."""
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM charvak_candidates WHERE bench_since IS NOT NULL")
            total = cur.fetchone()[0]

            cur.execute("""
                SELECT work_auth_status, COUNT(*)
                FROM charvak_candidates
                WHERE bench_since IS NOT NULL
                GROUP BY work_auth_status
            """)
            by_auth = {row[0] or "Unknown": row[1] for row in cur.fetchall()}

            cur.execute("""
                SELECT availability, COUNT(*)
                FROM charvak_candidates
                WHERE bench_since IS NOT NULL
                GROUP BY availability
            """)
            by_avail = {row[0] or "Unknown": row[1] for row in cur.fetchall()}

            cur.close()
            conn.close()

            return {
                "status": "success",
                "total": total,
                "by_work_auth": by_auth,
                "by_availability": by_avail
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}


bench_engine = BenchEngine()
