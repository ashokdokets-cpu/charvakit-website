"""
college_dashboard_engine.py - TPO Placement Readiness Dashboard
Session 109
"""

import uuid
import logging
import secrets
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
        """Get aggregated stats by reusing the rankings logic to avoid SQL bugs."""
        try:
            # We fetch the rankings first (which we know works perfectly)
            rankings = self.get_student_rankings(institution_name, limit=5000)
            if rankings.get("status") != "success":
                return {"status": "error", "message": "Failed to fetch rankings"}

            students = rankings.get("students", [])
            
            invited = len(students)
            assessed = 0
            total_score = 0
            ready = 0
            upskill = 0
            not_ready = 0

            for s in students:
                if s.get("score") is not None:
                    assessed += 1
                    total_score += s["score"]
                    if s["readiness"] == "Ready": ready += 1
                    elif s["readiness"] == "Upskill": upskill += 1
                    elif s["readiness"] == "Not Ready": not_ready += 1

            avg_score = round(total_score / assessed, 1) if assessed > 0 else 0

            return {
                "status": "success",
                "stats": {
                    "invited": invited,
                    "assessed": assessed,
                    "avg_score": avg_score,
                    "ready": ready,
                    "upskill": upskill,
                    "not_ready": not_ready
                }
            }
        except Exception as e:
            logger.error(f"[college_dashboard] get_batch_stats failed: {e}")
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


    def send_bulk_invites(self, institution_name, base_url="https://www.charvakit.com"):
        """Generate magic links and send emails via SendGrid."""
        conn = db.get_pooled_connection()
        if not conn: return {"status": "error", "message": "DB unavailable"}
        
        sent_count = 0
        failed_count = 0
        try:
            cur = conn.cursor()
            # Find students who haven't been sent an invite yet
            cur.execute("""
                SELECT student_email, student_name, target_role 
                FROM charvak_college_invites 
                WHERE institution_name = %s AND last_email_sent_at IS NULL
            """, (institution_name,))
            students = cur.fetchall()
            
            from enhanced_email import enhanced_email
            
            for s in students:
                email = s[0]
                name = s[1] or "Student"
                role = s[2] or "Target Role"
                
                # Generate a secure magic token
                token = secrets.token_urlsafe(32)
                magic_link = f"{base_url}/student/magic-login?token={token}"
                
                # Update DB first so we don't double-send
                cur.execute("""
                    UPDATE charvak_college_invites 
                    SET last_email_sent_at = NOW(), magic_token = %s 
                    WHERE institution_name = %s AND student_email = %s
                """, (token, institution_name, email))
                conn.commit()
                
                # Send the email
                subject = f"Action Required: Verify your skills for {institution_name}"
                html_content = f"""
                <h3>Hi {name},</h3>
                <p>Your college ({institution_name}) has partnered with Charvak to help you get placed.</p>
                <p>Click the link below to take your 20-minute technical assessment for the role of <b>{role}</b>. 
                Once you pass, you get a cryptographically verified certificate to share with recruiters.</p>
                <p><a href="{magic_link}" style="padding: 10px 20px; background: #0d9488; color: white; text-decoration: none; border-radius: 5px;">Start My Assessment</a></p>
                <p>This link logs you in automatically. No password needed.</p>
                """
                
                try:
                    # Assuming enhanced_email.send_email(to, subject, body) is your method
                    enhanced_email.send_email(email, subject, html_content)
                    sent_count += 1
                except Exception as email_err:
                    logger.error(f"[bulk_invite] Email failed for {email}: {email_err}")
                    failed_count += 1
                    # Rollback the timestamp so we can retry later
                    cur.execute("""
                        UPDATE charvak_college_invites 
                        SET last_email_sent_at = NULL, magic_token = NULL 
                        WHERE institution_name = %s AND student_email = %s
                    """, (institution_name, email))
                    conn.commit()
            
            cur.close()
            db.release_pooled_connection(conn)
            return {"status": "success", "sent": sent_count, "failed": failed_count}
        except Exception as e:
            logger.error(f"[college_dashboard] send_bulk_invites failed: {e}")
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