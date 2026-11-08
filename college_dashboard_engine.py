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
        """Get ranked list of students. Safely pulls from multiple assessment tables."""
        conn = db.get_pooled_connection()
        if not conn: return {"status": "error"}
        try:
            cur = conn.cursor()
            
            # Step 1: Get all invites for this institution
            cur.execute("""
                SELECT student_name, student_email, target_role, status
                FROM charvak_college_invites
                WHERE institution_name = %s
                ORDER BY student_name ASC
                LIMIT %s
            """, (institution_name, limit))
            invites = cur.fetchall()
            
            students = []
            for inv in invites:
                name = inv[0]
                email = inv[1]
                role = inv[2]
                status = inv[3]
                
                score = None
                cert_id = None
                
                # Step 2: Try to find a CERTIFICATE
                try:
                    cur.execute("""
                        SELECT score, cert_id FROM charvak_career_certifications
                        WHERE email = %s LIMIT 1
                    """, (email,))
                    cert = cur.fetchone()
                    if cert:
                        score = float(cert[0]) if cert[0] is not None else None
                        cert_id = cert[1]
                except Exception:
                    pass
                
                # Step 3: Fallback to raw career assessment
                if score is None:
                    try:
                        cur.execute("""
                            SELECT score FROM charvak_career_assessments
                            WHERE email = %s AND status = 'completed'
                            ORDER BY started_at DESC LIMIT 1
                        """, (email,))
                        res = cur.fetchone()
                        if res and res[0] is not None:
                            score = float(res[0])
                    except Exception:
                        pass
                
                # Step 4: Fallback to generic assessment_results
                if score is None:
                    try:
                        cur.execute("""
                            SELECT score FROM charvak_assessment_results
                            WHERE email = %s ORDER BY id DESC LIMIT 1
                        """, (email,))
                        res = cur.fetchone()
                        if res and res[0] is not None:
                            score = float(res[0])
                    except Exception:
                        pass
                
                readiness = "Pending"
                if score is not None:
                    if score >= 80: readiness = "Ready"
                    elif score >= 60: readiness = "Upskill"
                    else: readiness = "Not Ready"
                
                students.append({
                    "name": name,
                    "email": email,
                    "score": round(score, 1) if score is not None else None,
                    "role": role,
                    "cert_id": cert_id,
                    "invite_status": status,
                    "readiness": readiness
                })
            
            # Sort: highest scores first, then pending
            students.sort(key=lambda x: (x["score"] is None, -(x["score"] or 0)))
            
            cur.close()
            db.release_pooled_connection(conn)
            return {"status": "success", "students": students}
        except Exception as e:
            logger.error(f"[college_dashboard] get_student_rankings failed: {e}")
            try: db.release_pooled_connection(conn)
            except: pass
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