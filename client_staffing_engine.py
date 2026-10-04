"""
Charvak Client Staffing Engine (Session 22)
Manages client roles, screening questions, candidate applications, and
CBREX-ready submission package generation.
"""
import os
import json
import logging
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.client_staffing")


ROLE_STATUSES = ["sourcing", "shortlisting", "submitted", "closed", "on_hold"]
SUBMISSION_STATUSES = ["pending", "shortlisted", "submitted", "interviewing",
                       "offer", "hired", "rejected", "withdrawn"]
ANSWER_TYPES = ["text", "multiline", "yes_no", "choice_single",
                "choice_multi", "number"]


class ClientStaffingEngine:
    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Self-healing DDL. Matches migrations/20261005_client_staffing_pipeline.sql."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_client_roles (
                    role_id              TEXT PRIMARY KEY,
                    client_name          TEXT NOT NULL,
                    client_type          TEXT DEFAULT 'direct',
                    vendor_portal        TEXT,
                    vendor_role_ref      TEXT,
                    title                TEXT NOT NULL,
                    location             TEXT,
                    experience_min_years INTEGER,
                    experience_max_years INTEGER,
                    skills_required      TEXT,
                    budget_min_inr       INTEGER,
                    budget_max_inr       INTEGER,
                    job_type             TEXT DEFAULT 'Permanent',
                    submission_deadline  DATE,
                    priority             TEXT DEFAULT 'normal',
                    status               TEXT DEFAULT 'sourcing',
                    source               TEXT DEFAULT 'email',
                    source_email_ref     TEXT,
                    jd_text              TEXT,
                    posted_by            TEXT DEFAULT 'charvak-staffing',
                    created_by           TEXT,
                    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_role_screening_questions (
                    question_id    TEXT PRIMARY KEY,
                    role_id        TEXT NOT NULL,
                    question_num   INTEGER NOT NULL,
                    question_text  TEXT NOT NULL,
                    answer_type    TEXT NOT NULL,
                    choices_json   JSONB,
                    fill_source    TEXT NOT NULL DEFAULT 'candidate',
                    required       BOOLEAN DEFAULT TRUE,
                    sort_order     INTEGER,
                    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_role_screening_answers (
                    answer_id    TEXT PRIMARY KEY,
                    role_id      TEXT NOT NULL,
                    candidate_id TEXT NOT NULL,
                    question_id  TEXT NOT NULL,
                    answer_text  TEXT,
                    answered_by  TEXT,
                    answered_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(candidate_id, question_id)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_candidate_documents (
                    document_id    TEXT PRIMARY KEY,
                    candidate_id   TEXT NOT NULL,
                    email          TEXT,
                    document_type  TEXT NOT NULL,
                    filename       TEXT NOT NULL,
                    content_type   TEXT,
                    size_bytes     INTEGER,
                    storage_path   TEXT,
                    content_base64 TEXT,
                    uploaded_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_candidate_consents (
                    consent_id     TEXT PRIMARY KEY,
                    candidate_id   TEXT NOT NULL,
                    email          TEXT NOT NULL,
                    role_id        TEXT NOT NULL,
                    vendor         TEXT,
                    consent_method TEXT,
                    consented_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address     TEXT,
                    user_agent     TEXT,
                    consent_proof_doc_id TEXT,
                    UNIQUE(candidate_id, role_id)
                )
            """)

            # Extended columns
            for col, typ in [
                ("first_name", "TEXT"),
                ("last_name", "TEXT"),
                ("additional_email", "TEXT"),
                ("additional_phone", "TEXT"),
                ("current_company", "TEXT"),
                ("current_salary_inr", "NUMERIC"),
                ("current_salary_currency", "TEXT DEFAULT 'INR'"),
                ("relevant_experience_years", "INTEGER"),
                ("expected_hike_percent", "INTEGER"),
                ("variable_component", "TEXT"),
                ("other_benefits", "TEXT"),
                ("serving_notice_last_day", "DATE"),
                ("notice_period", "TEXT"),
                ("candidate_summary", "TEXT"),
                ("country", "TEXT DEFAULT 'India'"),
            ]:
                try:
                    cur.execute(f"ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS {col} {typ}")
                except Exception as _e:
                    logger.warning(f"candidates.{col} alter failed: {_e}")

            for col, typ in [
                ("client_role_id", "TEXT"),
                ("certificate_id", "TEXT"),
                ("readiness_score", "INTEGER"),
                ("submission_status", "TEXT DEFAULT 'pending'"),
                ("submitted_at", "TIMESTAMP"),
                ("submission_notes", "TEXT"),
                ("recruiter_notes", "TEXT"),
            ]:
                try:
                    cur.execute(f"ALTER TABLE charvak_applications ADD COLUMN IF NOT EXISTS {col} {typ}")
                except Exception as _e:
                    logger.warning(f"applications.{col} alter failed: {_e}")

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"client_staffing table init failed: {e}")

    # ----------------------------------------------------------------
    # Role CRUD
    # ----------------------------------------------------------------

    def create_role(self, data: Dict) -> Dict:
        """Create a client role. data = {client_name, title, ...}"""
        client_name = (data.get("client_name") or "").strip()
        title = (data.get("title") or "").strip()
        if not client_name or not title:
            return {"status": "error", "message": "client_name and title required"}

        role_id = "ROLE-" + secrets.token_hex(4).upper()

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_client_roles
                    (role_id, client_name, client_type, vendor_portal,
                     vendor_role_ref, title, location, experience_min_years,
                     experience_max_years, skills_required, budget_min_inr,
                     budget_max_inr, job_type, submission_deadline, priority,
                     status, source, source_email_ref, jd_text,
                     posted_by, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s)
            """, (
                role_id,
                client_name,
                data.get("client_type", "direct"),
                data.get("vendor_portal"),
                data.get("vendor_role_ref"),
                title,
                data.get("location"),
                data.get("experience_min_years"),
                data.get("experience_max_years"),
                data.get("skills_required"),
                data.get("budget_min_inr"),
                data.get("budget_max_inr"),
                data.get("job_type", "Permanent"),
                data.get("submission_deadline"),
                data.get("priority", "normal"),
                data.get("status", "sourcing"),
                data.get("source", "email"),
                data.get("source_email_ref"),
                data.get("jd_text"),
                "charvak-staffing",
                data.get("created_by"),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_role failed: {e}")
            return {"status": "error", "message": f"Could not create role: {e}"}

        return {"status": "success", "role_id": role_id}

    def list_roles(self, status: Optional[str] = None,
                   client_name: Optional[str] = None) -> Dict:
        """List roles with applicant counts."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            sql = """
                SELECT r.role_id, r.client_name, r.client_type, r.vendor_portal,
                       r.title, r.location, r.experience_min_years,
                       r.experience_max_years, r.skills_required,
                       r.budget_min_inr, r.budget_max_inr, r.job_type,
                       r.submission_deadline, r.priority, r.status,
                       r.created_at,
                       (SELECT COUNT(*) FROM charvak_applications a
                        WHERE a.client_role_id = r.role_id) AS applicant_count
                FROM charvak_client_roles r
                WHERE 1=1
            """
            params = []
            if status:
                sql += " AND r.status = %s"
                params.append(status)
            if client_name:
                sql += " AND r.client_name = %s"
                params.append(client_name)
            sql += " ORDER BY r.created_at DESC LIMIT 200"

            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"list_roles failed: {e}")
            return {"status": "error", "message": f"List failed: {e}"}

        roles = [{
            "role_id": r[0],
            "client_name": r[1],
            "client_type": r[2],
            "vendor_portal": r[3],
            "title": r[4],
            "location": r[5],
            "experience_min_years": r[6],
            "experience_max_years": r[7],
            "skills_required": r[8],
            "budget_min_inr": r[9],
            "budget_max_inr": r[10],
            "job_type": r[11],
            "submission_deadline": r[12].isoformat() if r[12] else None,
            "priority": r[13],
            "status": r[14],
            "created_at": r[15].isoformat() if r[15] else None,
            "applicant_count": r[16],
        } for r in rows]
        return {"status": "success", "roles": roles, "count": len(roles)}

    def get_role(self, role_id: str) -> Dict:
        """Get role details + screening questions."""
        role_id = (role_id or "").strip()
        if not role_id:
            return {"status": "error", "message": "role_id required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT role_id, client_name, client_type, vendor_portal,
                       vendor_role_ref, title, location, experience_min_years,
                       experience_max_years, skills_required, budget_min_inr,
                       budget_max_inr, job_type, submission_deadline, priority,
                       status, source, source_email_ref, jd_text,
                       posted_by, created_by, created_at, updated_at
                FROM charvak_client_roles WHERE role_id = %s
            """, (role_id,))
            r = cur.fetchone()
            if not r:
                cur.close(); conn.close()
                return {"status": "error", "message": "Role not found"}

            role = {
                "role_id": r[0], "client_name": r[1], "client_type": r[2],
                "vendor_portal": r[3], "vendor_role_ref": r[4], "title": r[5],
                "location": r[6], "experience_min_years": r[7],
                "experience_max_years": r[8], "skills_required": r[9],
                "budget_min_inr": r[10], "budget_max_inr": r[11],
                "job_type": r[12],
                "submission_deadline": r[13].isoformat() if r[13] else None,
                "priority": r[14], "status": r[15], "source": r[16],
                "source_email_ref": r[17], "jd_text": r[18],
                "posted_by": r[19], "created_by": r[20],
                "created_at": r[21].isoformat() if r[21] else None,
                "updated_at": r[22].isoformat() if r[22] else None,
                "screening_questions": [],
            }

            cur.execute("""
                SELECT question_id, question_num, question_text, answer_type,
                       choices_json, fill_source, required, sort_order
                FROM charvak_role_screening_questions
                WHERE role_id = %s
                ORDER BY COALESCE(sort_order, question_num)
            """, (role_id,))
            for q in cur.fetchall():
                role["screening_questions"].append({
                    "question_id": q[0],
                    "question_num": q[1],
                    "question_text": q[2],
                    "answer_type": q[3],
                    "choices": q[4] if isinstance(q[4], list) else (json.loads(q[4]) if q[4] else None),
                    "fill_source": q[5],
                    "required": bool(q[6]),
                    "sort_order": q[7],
                })

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_role failed: {e}")
            return {"status": "error", "message": f"Fetch failed: {e}"}

        return {"status": "success", "role": role}

    def set_screening_questions(self, role_id: str, questions: List[Dict]) -> Dict:
        """Replace all screening questions for a role."""
        role_id = (role_id or "").strip()
        if not role_id:
            return {"status": "error", "message": "role_id required"}
        if not isinstance(questions, list):
            return {"status": "error", "message": "questions must be a list"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Delete existing
            cur.execute("DELETE FROM charvak_role_screening_questions WHERE role_id = %s", (role_id,))

            for i, q in enumerate(questions, 1):
                qid = "QST-" + secrets.token_hex(4).upper()
                answer_type = q.get("answer_type", "text")
                if answer_type not in ANSWER_TYPES:
                    answer_type = "text"
                cur.execute("""
                    INSERT INTO charvak_role_screening_questions
                        (question_id, role_id, question_num, question_text,
                         answer_type, choices_json, fill_source, required, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s)
                """, (
                    qid, role_id, q.get("question_num", i),
                    q.get("question_text", ""),
                    answer_type,
                    json.dumps(q.get("choices")) if q.get("choices") else None,
                    q.get("fill_source", "candidate"),
                    bool(q.get("required", True)),
                    q.get("sort_order", i),
                ))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"set_screening_questions failed: {e}")
            return {"status": "error", "message": f"Save failed: {e}"}

        return {"status": "success", "count": len(questions)}

    # ----------------------------------------------------------------
    # Candidate application
    # ----------------------------------------------------------------

    def apply_to_role(self, data: Dict) -> Dict:
        """
        Candidate applies to a client role.
        data = {email, role_id, certificate_id (optional),
                screening_answers: [{question_id, answer_text}],
                consent: bool}
        """
        email = (data.get("email") or "").strip().lower()
        role_id = (data.get("role_id") or "").strip()
        if not email or not role_id:
            return {"status": "error", "message": "email and role_id required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Look up candidate
            cur.execute("SELECT candidate_id, skill_score FROM charvak_candidates WHERE email = %s", (email,))
            cand_row = cur.fetchone()
            if not cand_row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Candidate profile not found. Complete your profile first."}
            candidate_id = cand_row[0]

            # Resolve readiness certificate (if provided, else latest for this role/level)
            certificate_id = data.get("certificate_id")
            readiness_score = None
            if certificate_id:
                cur.execute("""
                    SELECT certificate_id, readiness_score
                    FROM charvak_readiness_certificates
                    WHERE certificate_id = %s AND email = %s
                """, (certificate_id, email))
                cr = cur.fetchone()
                if cr:
                    certificate_id = cr[0]
                    readiness_score = cr[1]

            # Idempotency: one application per (email, role_id)
            cur.execute("""
                SELECT application_id FROM charvak_applications
                WHERE user_id = %s AND client_role_id = %s
            """, (email, role_id))
            existing = cur.fetchone()
            if existing:
                application_id = existing[0]
            else:
                application_id = "APP-" + secrets.token_hex(4).upper()
                cur.execute("""
                    INSERT INTO charvak_applications
                        (application_id, job_id, user_id, status,
                         client_role_id, certificate_id, readiness_score,
                         submission_status)
                    VALUES (%s, %s, %s, 'applied', %s, %s, %s, 'pending')
                """, (
                    application_id, role_id, email, role_id,
                    certificate_id, readiness_score,
                ))

            # Save screening answers
            answers = data.get("screening_answers") or []
            for a in answers:
                qid = (a.get("question_id") or "").strip()
                if not qid:
                    continue
                cur.execute("""
                    INSERT INTO charvak_role_screening_answers
                        (answer_id, role_id, candidate_id, question_id,
                         answer_text, answered_by)
                    VALUES (%s, %s, %s, %s, %s, 'candidate')
                    ON CONFLICT (candidate_id, question_id) DO UPDATE
                    SET answer_text = EXCLUDED.answer_text,
                        answered_by = EXCLUDED.answered_by,
                        answered_at = CURRENT_TIMESTAMP
                """, (
                    "ANS-" + secrets.token_hex(4).upper(),
                    role_id, candidate_id, qid,
                    str(a.get("answer_text") or ""),
                ))

            # Record consent (if granted)
            if data.get("consent"):
                cur.execute("""
                    INSERT INTO charvak_candidate_consents
                        (consent_id, candidate_id, email, role_id, vendor,
                         consent_method, ip_address, user_agent)
                    VALUES (%s, %s, %s, %s, %s, 'in_app', %s, %s)
                    ON CONFLICT (candidate_id, role_id) DO UPDATE
                    SET consent_method = 'in_app',
                        consented_at = CURRENT_TIMESTAMP
                """, (
                    "CNS-" + secrets.token_hex(4).upper(),
                    candidate_id, email, role_id,
                    data.get("vendor", "CBREX"),
                    data.get("ip_address"),
                    data.get("user_agent"),
                ))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"apply_to_role failed: {e}")
            return {"status": "error", "message": f"Apply failed: {e}"}

        return {
            "status": "success",
            "application_id": application_id,
            "candidate_id": candidate_id,
        }

    def list_applications_for_role(self, role_id: str) -> Dict:
        """Admin: applications for a role, ranked by readiness score."""
        role_id = (role_id or "").strip()
        if not role_id:
            return {"status": "error", "message": "role_id required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT a.application_id, a.user_id, a.status,
                       a.certificate_id, a.readiness_score,
                       a.submission_status, a.submitted_at,
                       a.recruiter_notes,
                       c.name, c.job_title, c.experience_years,
                       c.location, c.skills
                FROM charvak_applications a
                LEFT JOIN charvak_candidates c ON c.email = a.user_id
                WHERE a.client_role_id = %s
                ORDER BY COALESCE(a.readiness_score, 0) DESC, a.created_at DESC
            """, (role_id,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"list_applications_for_role failed: {e}")
            return {"status": "error", "message": f"List failed: {e}"}

        apps = [{
            "application_id": r[0],
            "email": r[1],
            "status": r[2],
            "certificate_id": r[3],
            "readiness_score": r[4],
            "submission_status": r[5],
            "submitted_at": r[6].isoformat() if r[6] else None,
            "recruiter_notes": r[7],
            "candidate_name": r[8],
            "current_job_title": r[9],
            "experience_years": r[10],
            "location": r[11],
            "skills": r[12],
        } for r in rows]
        return {"status": "success", "applications": apps, "count": len(apps)}

    def update_submission_status(self, application_id: str, status: str,
                                  recruiter_notes: Optional[str] = None) -> Dict:
        """Admin: move an application through the submission pipeline."""
        application_id = (application_id or "").strip()
        status = (status or "").strip()
        if not application_id:
            return {"status": "error", "message": "application_id required"}
        if status not in SUBMISSION_STATUSES:
            return {"status": "error", "message": f"Invalid status. Allowed: {SUBMISSION_STATUSES}"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            submitted_at = None
            if status in ("submitted", "interviewing", "offer", "hired"):
                submitted_at = datetime.now()

            cur.execute("""
                UPDATE charvak_applications
                SET submission_status = %s,
                    submitted_at = COALESCE(%s, submitted_at),
                    recruiter_notes = COALESCE(%s, recruiter_notes)
                WHERE application_id = %s
                RETURNING application_id, submission_status
            """, (status, submitted_at, recruiter_notes, application_id))
            row = cur.fetchone()
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"update_submission_status failed: {e}")
            return {"status": "error", "message": f"Update failed: {e}"}

        if not row:
            return {"status": "error", "message": "Application not found"}
        return {"status": "success", "application_id": row[0], "submission_status": row[1]}


client_staffing_engine = ClientStaffingEngine()
