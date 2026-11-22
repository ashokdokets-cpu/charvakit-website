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
    def get_ranked_jobs(self, student_id: str, india_only: bool = True) -> list:
        """Fetch active jobs and rank them by match score."""
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
                    ORDER BY created_at DESC
                    LIMIT 100
                """)
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

job_hunter_engine = JobHunterEngine()