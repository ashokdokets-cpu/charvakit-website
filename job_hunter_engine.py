"""
Job Hunter Engine - Session 119
Ranks real India + Global jobs for college students.
"""
import os
import json
import logging
from database import db

logger = logging.getLogger("charvakit.job_hunter")

class JobHunterEngine:
    def get_ranked_jobs(self, student_id: str, india_only: bool = True, category: str = "all") -> list:
        """Fetch active jobs and rank them by match score. Optionally filter by role category."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            # 1. Get student's certs
            cur.execute("""
                SELECT role, score FROM charvak_career_certifications
                WHERE student_id = %s
                  AND passed = TRUE
                  AND revoked_at IS NULL
                  AND (expires_at IS NULL OR expires_at > NOW())
            """, (student_id,))
            certs = cur.fetchall()
            
            # 2. Get practice stats
            cur.execute("""
                SELECT COALESCE(SUM(questions_correct), 0), COALESCE(SUM(questions_total), 0)
                FROM charvak_practice_attempts WHERE student_id = %s
            """, (student_id,))
            correct, total = cur.fetchone()
            practice_acc = (correct / total * 100) if total > 0 else 0

            # 3. Get jobs — STRICT India filter
            if india_only:
                cur.execute("""
                    SELECT job_id, title, company, location, salary, source, posted_date, description
                    FROM charvak_jobs
                    WHERE status = 'active'
                      AND (
                        source IN ('techmap', 'naukri', 'adzuna')
                        OR LOWER(location) LIKE '%%india%%'
                        OR LOWER(location) LIKE '%%bangalore%%'
                        OR LOWER(location) LIKE '%%bengaluru%%'
                        OR LOWER(location) LIKE '%%mumbai%%'
                        OR LOWER(location) LIKE '%%delhi%%'
                        OR LOWER(location) LIKE '%%hyderabad%%'
                        OR LOWER(location) LIKE '%%chennai%%'
                        OR LOWER(location) LIKE '%%pune%%'
                        OR LOWER(location) LIKE '%%kolkata%%'
                        OR LOWER(location) LIKE '%%ahmedabad%%'
                        OR LOWER(location) LIKE '%%jaipur%%'
                        OR LOWER(location) LIKE '%%gurgaon%%'
                        OR LOWER(location) LIKE '%%noida%%'
                        OR LOWER(location) LIKE '%%guntur%%'
                        OR LOWER(location) LIKE '%%vijayawada%%'
                        OR LOWER(location) LIKE '%%visakhapatnam%%'
                      )
                      AND (%s = 'all' OR role_category = %s)
                    ORDER BY created_at DESC
                    LIMIT 100
                """, (category, category))
            else:
                cur.execute("""
                    SELECT job_id, title, company, location, salary, source, posted_date, description
                    FROM charvak_jobs
                    WHERE status = 'active'
                    ORDER BY created_at DESC
                    LIMIT 50
                """)
            jobs = cur.fetchall()

            ranked = []
            for j in jobs:
                job_id, title, company, location, salary, source, posted_date, desc = j
                
                # Match algorithm
                match_score = 50  # Base
                
                title_lower = (title or "").lower()
                desc_lower = (desc or "").lower()
                
                for c_role, c_score in certs:
                    if c_role:
                        c_role_lower = c_role.lower()
                        if c_role_lower in title_lower or c_role_lower in desc_lower:
                            match_score += (c_score * 0.3)
                            break
                
                match_score += (practice_acc * 0.2)
                match_score = min(100, int(match_score))

                # Only show if match score is decent
                if match_score >= 40:
                    ranked.append({
                        "job_id": job_id,
                        "title": title,
                        "company": company,
                        "location": location or "India",
                        "salary": salary or "Not disclosed",
                        "source": source,
                        "posted_date": posted_date[:10] if posted_date else "Recent",
                        "match_score": match_score,
                    })

            ranked.sort(key=lambda x: x["match_score"], reverse=True)
            return ranked
        finally:
            cur.close()
            conn.close()

    def save_job(self, student_id: str, job_id: str) -> dict:
        """Save a job for a student. Returns status dict."""
        import secrets
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            save_id = f"SAVE-{secrets.token_hex(4).upper()}"
            cur.execute("""
                INSERT INTO charvak_saved_jobs (save_id, student_id, job_id, status)
                VALUES (%s, %s, %s, 'saved')
                ON CONFLICT (student_id, job_id) DO NOTHING
            """, (save_id, student_id, job_id))
            conn.commit()
            return {"status": "success", "action": "saved", "job_id": job_id}
        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def unsave_job(self, student_id: str, job_id: str) -> dict:
        """Remove a saved job."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                DELETE FROM charvak_saved_jobs
                WHERE student_id = %s AND job_id = %s
            """, (student_id, job_id))
            conn.commit()
            return {"status": "success", "action": "unsaved", "job_id": job_id}
        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def update_application_status(self, student_id: str, job_id: str, new_status: str, notes: str = None) -> dict:
        """Update application status: applied | interviewing | offer | rejected."""
        valid = ["saved", "applied", "interviewing", "offer", "rejected"]
        if new_status not in valid:
            return {"status": "error", "message": f"Invalid status. Use: {valid}"}

        conn = db.get_connection()
        cur = conn.cursor()
        try:
            # Build update dynamically
            if new_status == "applied":
                cur.execute("""
                    UPDATE charvak_saved_jobs
                    SET status = %s,
                        applied_at = NOW(),
                        followup_3day_at = NOW() + INTERVAL '3 days',
                        followup_7day_at = NOW() + INTERVAL '7 days',
                        followup_14day_at = NOW() + INTERVAL '14 days',
                        notes = COALESCE(%s, notes),
                        updated_at = NOW()
                    WHERE student_id = %s AND job_id = %s
                """, (new_status, notes, student_id, job_id))
            else:
                cur.execute("""
                    UPDATE charvak_saved_jobs
                    SET status = %s,
                        notes = COALESCE(%s, notes),
                        updated_at = NOW()
                    WHERE student_id = %s AND job_id = %s
                """, (new_status, notes, student_id, job_id))
            conn.commit()
            return {"status": "success", "new_status": new_status, "rowcount": cur.rowcount}
        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def get_saved_jobs(self, student_id: str) -> list:
        """Get all saved jobs with full job details."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT sj.save_id, sj.job_id, sj.status, sj.applied_at, sj.notes,
                       sj.created_at, sj.updated_at,
                       j.title, j.company, j.location, j.salary, j.source
                FROM charvak_saved_jobs sj
                JOIN charvak_jobs j ON j.job_id = sj.job_id
                WHERE sj.student_id = %s
                ORDER BY sj.updated_at DESC
            """, (student_id,))
            rows = cur.fetchall()
            results = []
            for r in rows:
                results.append({
                    "save_id": r[0], "job_id": r[1], "status": r[2],
                    "applied_at": r[3], "notes": r[4],
                    "created_at": r[5], "updated_at": r[6],
                    "title": r[7], "company": r[8], "location": r[9],
                    "salary": r[10], "source": r[11],
                })
            return results
        finally:
            cur.close()
            conn.close()

    def get_saved_job_ids(self, student_id: str) -> set:
        """Return a set of job_ids the student has saved (for quick lookup in templates)."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT job_id FROM charvak_saved_jobs WHERE student_id = %s", (student_id,))
            return {r[0] for r in cur.fetchall()}
        finally:
            cur.close()
            conn.close()

    def get_application_stats(self, student_id: str) -> dict:
        """Summary counts for the tracker dashboard."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT status, COUNT(*) FROM charvak_saved_jobs
                WHERE student_id = %s GROUP BY status
            """, (student_id,))
            counts = {r[0]: r[1] for r in cur.fetchall()}
            return {
                "saved": counts.get("saved", 0),
                "applied": counts.get("applied", 0),
                "interviewing": counts.get("interviewing", 0),
                "offer": counts.get("offer", 0),
                "rejected": counts.get("rejected", 0),
                "total": sum(counts.values()),
            }
        finally:
            cur.close()
            conn.close()


    def save_job(self, student_id: str, job_id: str) -> dict:
        import secrets
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            save_id = f"SAVE-{secrets.token_hex(4).upper()}"
            cur.execute("""
                INSERT INTO charvak_saved_jobs (save_id, student_id, job_id, status)
                VALUES (%s, %s, %s, 'saved')
                ON CONFLICT (student_id, job_id) DO NOTHING
            """, (save_id, student_id, job_id))
            conn.commit()
            return {"status": "success", "action": "saved"}
        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def unsave_job(self, student_id: str, job_id: str) -> dict:
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM charvak_saved_jobs WHERE student_id = %s AND job_id = %s", (student_id, job_id))
            conn.commit()
            return {"status": "success", "action": "unsaved"}
        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def update_application_status(self, student_id: str, job_id: str, new_status: str, notes: str = None) -> dict:
        valid = ["saved", "applied", "interviewing", "offer", "rejected"]
        if new_status not in valid:
            return {"status": "error", "message": f"Invalid status. Use: {valid}"}
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            if new_status == "applied":
                cur.execute("""
                    UPDATE charvak_saved_jobs
                    SET status = %s, applied_at = NOW(),
                        followup_3day_at = NOW() + INTERVAL '3 days',
                        followup_7day_at = NOW() + INTERVAL '7 days',
                        followup_14day_at = NOW() + INTERVAL '14 days',
                        notes = COALESCE(%s, notes), updated_at = NOW()
                    WHERE student_id = %s AND job_id = %s
                """, (new_status, notes, student_id, job_id))
            else:
                cur.execute("""
                    UPDATE charvak_saved_jobs
                    SET status = %s, notes = COALESCE(%s, notes), updated_at = NOW()
                    WHERE student_id = %s AND job_id = %s
                """, (new_status, notes, student_id, job_id))
            conn.commit()
            return {"status": "success", "new_status": new_status, "rowcount": cur.rowcount}
        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            conn.close()

    def get_saved_jobs(self, student_id: str) -> list:
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT sj.save_id, sj.job_id, sj.status, sj.applied_at, sj.notes,
                       sj.created_at, sj.updated_at,
                       j.title, j.company, j.location, j.salary, j.source
                FROM charvak_saved_jobs sj
                JOIN charvak_jobs j ON j.job_id = sj.job_id
                WHERE sj.student_id = %s
                ORDER BY sj.updated_at DESC
            """, (student_id,))
            results = []
            for r in cur.fetchall():
                results.append({
                    "save_id": r[0], "job_id": r[1], "status": r[2],
                    "applied_at": r[3], "notes": r[4],
                    "created_at": r[5], "updated_at": r[6],
                    "title": r[7], "company": r[8], "location": r[9],
                    "salary": r[10], "source": r[11],
                })
            return results
        finally:
            cur.close()
            conn.close()

    def get_saved_job_ids(self, student_id: str) -> set:
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT job_id FROM charvak_saved_jobs WHERE student_id = %s", (student_id,))
            return {r[0] for r in cur.fetchall()}
        finally:
            cur.close()
            conn.close()

    def get_application_stats(self, student_id: str) -> dict:
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT status, COUNT(*) FROM charvak_saved_jobs WHERE student_id = %s GROUP BY status", (student_id,))
            counts = {r[0]: r[1] for r in cur.fetchall()}
            return {
                "saved": counts.get("saved", 0),
                "applied": counts.get("applied", 0),
                "interviewing": counts.get("interviewing", 0),
                "offer": counts.get("offer", 0),
                "rejected": counts.get("rejected", 0),
                "total": sum(counts.values()),
            }
        finally:
            cur.close()
            conn.close()


    def get_student_cert_summary(self, student_id: str) -> dict:
        """Return summary of student's certs for display."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT role, score FROM charvak_career_certifications
                WHERE student_id = %s AND passed = TRUE AND revoked_at IS NULL
                AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY score DESC
            """, (student_id,))
            certs = [{"role": r[0], "score": r[1]} for r in cur.fetchall()]
            return {
                "count": len(certs),
                "top_role": certs[0]["role"] if certs else None,
                "top_score": certs[0]["score"] if certs else 0,
                "certs": certs,
            }
        finally:
            cur.close()
            conn.close()


job_hunter_engine = JobHunterEngine()