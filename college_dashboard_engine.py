"""
college_dashboard_engine.py - TPO Placement Readiness Dashboard
Session 109
"""

import uuid
import logging
from datetime import datetime, timezone
from database import db

logger = logging.getLogger(__name__)

class CollegeDashboardEngine:
    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self):
        try:
            conn = db.get_pooled_connection()
            if not conn: return
            cur = conn.cursor()
            # Fallback DDL
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_college_invites (
                    invite_id TEXT PRIMARY KEY,
                    institution_name TEXT NOT NULL,
                    student_email TEXT NOT NULL,
                    student_name TEXT,
                    target_role TEXT,
                    status TEXT DEFAULT 'pending',
                    invited_at TIMESTAMPTZ DEFAULT NOW(),
                    completed_at TIMESTAMPTZ,
                    UNIQUE(institution_name, student_email)
                )
            """)
            conn.commit()
            cur.close()
            db.release_pooled_connection(conn)
        except Exception as e:
            logger.warning(f"[college_dashboard] init failed: {e}")

    def get_batch_stats(self, institution_name):
        """Get aggregated stats for a college."""
        conn = db.get_pooled_connection()
        if not conn: return {"status": "error", "message": "DB unavailable"}
        try:
            cur = conn.cursor()
            
            # 1. Invited count
            cur.execute("SELECT COUNT(*) FROM charvak_college_invites WHERE institution_name = %s", (institution_name,))
            invited = cur.fetchone()[0]

            # 2. Assessed count & average score (join candidates to certs)
            # We assume candidates are linked via email
            query = """
                SELECT 
                    COUNT(DISTINCT c.candidate_id) as assessed_count,
                    COALESCE(AVG(cc.score), 0) as avg_score,
                    COUNT(DISTINCT cc.cert_id) FILTER (WHERE cc.score >= 80) as ready_count,
                    COUNT(DISTINCT cc.cert_id) FILTER (WHERE cc.score >= 60 AND cc.score < 80) as upskill_count,
                    COUNT(DISTINCT cc.cert_id) FILTER (WHERE cc.score < 60) as not_ready_count
                FROM charvak_candidates c
                LEFT JOIN charvak_career_certifications cc ON c.email = cc.email
                WHERE c.institution_name = %s OR c.email IN (
                    SELECT student_email FROM charvak_college_invites WHERE institution_name = %s
                )
            """
            cur.execute(query, (institution_name, institution_name))
            row = cur.fetchone()
            
            stats = {
                "invited": invited,
                "assessed": row[0] or 0,
                "avg_score": round(float(row[1]), 1) if row[1] else 0,
                "ready": row[2] or 0,
                "upskill": row[3] or 0,
                "not_ready": row[4] or 0
            }
            cur.close()
            db.release_pooled_connection(conn)
            return {"status": "success", "stats": stats}
        except Exception as e:
            logger.error(f"[college_dashboard] get_batch_stats failed: {e}")
            db.release_pooled_connection(conn)
            return {"status": "error", "message": str(e)}

    def get_student_rankings(self, institution_name, limit=100):
        """Get ranked list of students."""
        conn = db.get_pooled_connection()
        if not conn: return {"status": "error"}
        try:
            cur = conn.cursor()
            query = """
                SELECT 
                    COALESCE(ci.student_name, c.name) as name,
                    ci.student_email as email,
                    cc.score,
                    COALESCE(cc.role_title, ci.target_role) as role,
                    cc.cert_id,
                    ci.status
                FROM charvak_college_invites ci
                LEFT JOIN charvak_candidates c ON ci.student_email = c.email
                LEFT JOIN charvak_career_certifications cc ON ci.student_email = cc.email
                WHERE ci.institution_name = %s
                ORDER BY cc.score DESC NULLS LAST, ci.student_name ASC
                LIMIT %s
            """
            cur.execute(query, (institution_name, limit))
            rows = cur.fetchall()
            
            students = []
            for r in rows:
                score = float(r[2]) if r[2] else None
                status = "Ready" if score and score >= 80 else "Upskill" if score and score >= 60 else "Not Ready" if score else "Pending"
                students.append({
                    "name": r[0],
                    "email": r[1],
                    "score": round(score, 1) if score else None,
                    "role": r[3],
                    "cert_id": r[4],
                    "invite_status": r[5],
                    "readiness": status
                })
            
            cur.close()
            db.release_pooled_connection(conn)
            return {"status": "success", "students": students}
        except Exception as e:
            logger.error(f"[college_dashboard] get_student_rankings failed: {e}")
            db.release_pooled_connection(conn)
            return {"status": "error", "message": str(e)}

    def bulk_invite(self, institution_name, students):
        """Insert bulk invites. Students is a list of dicts: {name, email, role}"""
        conn = db.get_pooled_connection()
        if not conn: return {"status": "error"}
        inserted = 0
        skipped = 0
        try:
            cur = conn.cursor()
            for s in students:
                email = s.get("email", "").strip().lower()
                if not email or "@" not in email:
                    skipped += 1
                    continue
                
                invite_id = f"INV-{uuid.uuid4().hex[:12].upper()}"
                try:
                    cur.execute("""
                        INSERT INTO charvak_college_invites 
                        (invite_id, institution_name, student_email, student_name, target_role, status)
                        VALUES (%s, %s, %s, %s, %s, 'pending')
                        ON CONFLICT (institution_name, student_email) DO NOTHING
                    """, (invite_id, institution_name, email, s.get("name", ""), s.get("role", "")))
                    if cur.rowcount > 0:
                        inserted += 1
                    else:
                        skipped += 1
                except Exception as row_err:
                    logger.warning(f"[college_dashboard] insert failed for {email}: {row_err}")
                    skipped += 1
            
            conn.commit()
            cur.close()
            db.release_pooled_connection(conn)
            return {"status": "success", "inserted": inserted, "skipped": skipped}
        except Exception as e:
            logger.error(f"[college_dashboard] bulk_invite failed: {e}")
            conn.rollback()
            db.release_pooled_connection(conn)
            return {"status": "error", "message": str(e)}

college_dashboard_engine = CollegeDashboardEngine()