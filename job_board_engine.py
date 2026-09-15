"""
Charvak Job Board Engine
Database-backed job posting and applications
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.jobboard")


class JobBoardEngine:
    """Database-backed job board."""

    def __init__(self):
        self._ensure_tables()
        logger.info("Job Board Engine ready (database-backed)")

    def _ensure_tables(self):
        """Idempotent table creation."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_jobs (
                    job_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    job_type TEXT DEFAULT 'Permanent',
                    location TEXT DEFAULT 'Remote',
                    salary TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    skills TEXT DEFAULT '',
                    posted_by TEXT DEFAULT 'api',
                    posted_date TEXT DEFAULT '',
                    status TEXT DEFAULT 'active',
                    applications_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_applications (
                    application_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    user_id TEXT DEFAULT 'anonymous',
                    resume_url TEXT DEFAULT '',
                    applied_at TEXT DEFAULT '',
                    status TEXT DEFAULT 'applied',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Job board tables init failed: {e}")

    def _row_to_job(self, row) -> Dict:
        """Convert DB row to dict shape matching the old in-memory format."""
        if not row:
            return None
        return {
            "job_id": row[0],
            "title": row[1],
            "company": row[2],
            "job_type": row[3],
            "location": row[4],
            "salary": row[5],
            "description": row[6],
            "skills": [s.strip() for s in (row[7] or "").split(",") if s.strip()],
            "posted_by": row[8],
            "posted_date": row[9],
            "status": row[10],
            "applications_count": row[11] or 0,
        }

    def post_job(self, data: Dict) -> Dict:
        """Post a new job. Persists to DB."""
        job_id = f"JOB-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        skills = data.get("skills", [])
        skills_str = ",".join(skills) if isinstance(skills, list) else str(skills or "")

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_jobs
                    (job_id, title, company, job_type, location, salary, description, skills, posted_by, posted_date, status, applications_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active', 0)
            """, (
                job_id,
                data.get("title"),
                data.get("company"),
                data.get("job_type", "Permanent"),
                data.get("location", "Remote"),
                data.get("salary", ""),
                data.get("description", ""),
                skills_str,
                data.get("posted_by", "api"),
                datetime.now().strftime("%Y-%m-%d")
            ))
            conn.commit()
            cur.close()
            conn.close()

            logger.info(f"Job posted: {job_id} - {data.get('title')} at {data.get('company')}")
            return {
                "status": "success",
                "job_id": job_id,
                "message": "Job posted successfully"
            }
        except Exception as e:
            logger.error(f"post_job failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_jobs(self, filters: Dict = None) -> List[Dict]:
        """Get active jobs with optional filters."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            query = "SELECT job_id, title, company, job_type, location, salary, description, skills, posted_by, posted_date, status, applications_count FROM charvak_jobs WHERE status = 'active'"
            params = []

            if filters:
                if filters.get("type"):
                    query += " AND job_type = %s"
                    params.append(filters["type"])
                if filters.get("location"):
                    query += " AND LOWER(location) LIKE %s"
                    params.append(f"%{filters['location'].lower()}%")
                if filters.get("keyword"):
                    kw = f"%{filters['keyword'].lower()}%"
                    query += " AND (LOWER(title) LIKE %s OR LOWER(skills) LIKE %s)"
                    params.extend([kw, kw])

            query += " ORDER BY created_at DESC LIMIT 200"

            cur.execute(query, params)
            rows = cur.fetchall()
            cur.close()
            conn.close()

            return [self._row_to_job(r) for r in rows]
        except Exception as e:
            logger.error(f"get_jobs failed: {e}")
            return []

    def apply_to_job(self, data: Dict) -> Dict:
        """Apply to a job. Persists to DB. Increments applications_count."""
        job_id = data.get("job_id")
        if not job_id:
            return {"status": "error", "message": "job_id required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Verify job exists
            cur.execute("SELECT job_id FROM charvak_jobs WHERE job_id = %s", (job_id,))
            if not cur.fetchone():
                cur.close()
                conn.close()
                return {"status": "error", "message": "Job not found"}

            application_id = f"APP-{secrets.token_hex(4).upper()}"
            cur.execute("""
                INSERT INTO charvak_applications
                    (application_id, job_id, user_id, resume_url, applied_at, status)
                VALUES (%s, %s, %s, %s, %s, 'applied')
            """, (
                application_id,
                job_id,
                data.get("user_id", "anonymous"),
                data.get("resume_url", ""),
                datetime.now().isoformat()
            ))
            cur.execute("""
                UPDATE charvak_jobs
                SET applications_count = applications_count + 1
                WHERE job_id = %s
            """, (job_id,))
            conn.commit()
            cur.close()
            conn.close()

            logger.info(f"Application: {application_id} for {job_id}")
            return {
                "status": "success",
                "application_id": application_id,
                "message": "Application submitted"
            }
        except Exception as e:
            logger.error(f"apply_to_job failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_applications(self, job_id: str = None) -> List[Dict]:
        """Get applications, optionally filtered by job."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            if job_id:
                cur.execute("""
                    SELECT application_id, job_id, user_id, resume_url, applied_at, status
                    FROM charvak_applications WHERE job_id = %s
                    ORDER BY created_at DESC LIMIT 500
                """, (job_id,))
            else:
                cur.execute("""
                    SELECT application_id, job_id, user_id, resume_url, applied_at, status
                    FROM charvak_applications
                    ORDER BY created_at DESC LIMIT 500
                """)

            rows = cur.fetchall()
            cur.close()
            conn.close()

            return [
                {
                    "application_id": r[0],
                    "job_id": r[1],
                    "user_id": r[2],
                    "resume_url": r[3],
                    "applied_at": r[4],
                    "status": r[5],
                }
                for r in rows
            ]
        except Exception as e:
            logger.error(f"get_applications failed: {e}")
            return []

    def get_stats(self) -> Dict:
        """Get job board statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM charvak_jobs WHERE status = 'active'")
            active_jobs = cur.fetchone()[0] or 0

            cur.execute("SELECT COUNT(*) FROM charvak_applications")
            total_applications = cur.fetchone()[0] or 0

            cur.execute("SELECT COUNT(DISTINCT company) FROM charvak_jobs")
            companies = cur.fetchone()[0] or 0

            cur.execute("SELECT COUNT(DISTINCT location) FROM charvak_jobs")
            locations = cur.fetchone()[0] or 0

            cur.close()
            conn.close()

            return {
                "active_jobs": active_jobs,
                "total_applications": total_applications,
                "companies": companies,
                "locations": locations
            }
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"active_jobs": 0, "total_applications": 0, "companies": 0, "locations": 0}

    def _find_job(self, job_id: str) -> Optional[Dict]:
        """Internal helper — find a job by ID."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT job_id, title, company, job_type, location, salary, description, skills, posted_by, posted_date, status, applications_count
                FROM charvak_jobs WHERE job_id = %s
            """, (job_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            return self._row_to_job(row)
        except Exception as e:
            logger.error(f"_find_job failed: {e}")
            return None


job_board_engine = JobBoardEngine()