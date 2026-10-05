"""
Charvak Client Staffing Engine (Session 22)
Manages client roles, screening questions, candidate applications, and
Client-ready submission package generation.
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
                    data.get("vendor", "Charvak"),
                    data.get("ip_address"),
                    data.get("user_agent"),
                ))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"apply_to_role failed: {e}")
            return {"status": "error", "message": f"Apply failed: {e}"}

        # Notification (non-fatal): email HR + admin about the new application
        try:
            self._notify_new_application(
                application_id=application_id,
                candidate_id=candidate_id,
                email=email,
                role_id=role_id,
                certificate_id=certificate_id,
                readiness_score=readiness_score,
                screening_answers=data.get("screening_answers") or [],
            )
        except Exception as _e:
            logger.warning(f"new application notification failed (non-fatal): {_e}")

        return {
            "status": "success",
            "application_id": application_id,
            "candidate_id": candidate_id,
        }

    def _notify_new_application(self, application_id, candidate_id, email,
                                 role_id, certificate_id, readiness_score,
                                 screening_answers):
        """Fetch candidate + role context, call enhanced_email. Non-fatal."""
        cand = (None, email, None, None, None)
        role = (None, None, "normal")
        qmap = {}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT name, email, phone, location, experience_years
                FROM charvak_candidates WHERE candidate_id = %s
            """, (candidate_id,))
            row = cur.fetchone()
            if row:
                cand = row

            cur.execute("""
                SELECT title, client_name, priority
                FROM charvak_client_roles WHERE role_id = %s
            """, (role_id,))
            row = cur.fetchone()
            if row:
                role = row

            cur.execute("""
                SELECT question_id, question_text FROM charvak_role_screening_questions
                WHERE role_id = %s
            """, (role_id,))
            qmap = {r[0]: r[1] for r in cur.fetchall()}
            cur.close(); conn.close()
        except Exception as e:
            logger.warning(f"_notify_new_application context fetch failed: {e}")

        enriched_answers = []
        for a in screening_answers:
            qid = a.get("question_id")
            enriched_answers.append({
                "question_text": qmap.get(qid, qid),
                "answer_text": a.get("answer_text", ""),
            })

        try:
            from enhanced_email import enhanced_email
            enhanced_email.send_new_application(
                candidate_name=cand[0],
                candidate_email=cand[1] or email,
                candidate_phone=cand[2],
                candidate_location=cand[3],
                candidate_experience=cand[4],
                role_title=role[0] or role_id,
                client_name=role[1],
                role_priority=role[2] or "normal",
                readiness_score=readiness_score,
                certificate_id=certificate_id,
                application_id=application_id,
                screening_answers=enriched_answers,
            )
        except Exception as e:
            logger.warning(f"enhanced_email.send_new_application failed: {e}")

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


    # ----------------------------------------------------------------
    # Submission package builder (Session 23)
    # ----------------------------------------------------------------

    def build_submission_package(self, application_id: str) -> Dict:
        """
        Build a client-ready submission package for an application.
        Returns a JSON structure grouped by submission form sections:
          personal, contact, employment, education, readiness,
          screening_answers, attachments_manifest, meta
        """
        application_id = (application_id or "").strip()
        if not application_id:
            return {"status": "error", "message": "application_id required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # 1. Application row + role + certificate
            cur.execute("""
                SELECT a.application_id, a.user_id, a.client_role_id,
                       a.certificate_id, a.readiness_score,
                       a.status, a.submission_status, a.created_at,
                       a.submitted_at, a.recruiter_notes,
                       r.title, r.client_name, r.location, r.skills_required,
                       r.experience_min_years, r.experience_max_years,
                       r.job_type, r.priority, r.jd_text
                FROM charvak_applications a
                LEFT JOIN charvak_client_roles r ON r.role_id = a.client_role_id
                WHERE a.application_id = %s
            """, (application_id,))
            app = cur.fetchone()
            if not app:
                cur.close(); conn.close()
                return {"status": "error", "message": "Application not found"}

            user_email = app[1]
            role_id = app[2]
            certificate_id = app[3]
            readiness_score = app[4]
            submitted_at = app[8]
            recruiter_notes = app[9]
            role_title = app[10]
            client_name = app[11]
            role_location = app[12]
            role_skills = app[13]
            role_exp_min = app[14]
            role_exp_max = app[15]
            role_job_type = app[16]
            role_priority = app[17]
            role_jd = app[18]

            # 2. Candidate row
            cur.execute("""
                SELECT candidate_id, name, email, phone, location,
                       job_title, current_company, experience_years,
                       relevant_experience_years, notice_period,
                       serving_notice_last_day, skills, education,
                       degree, university, graduation_year, gpa,
                       certifications, first_name, last_name,
                       additional_email, additional_phone,
                       current_salary_inr, current_salary_currency,
                       expected_hike_percent, variable_component,
                       other_benefits, candidate_summary, country,
                       linkedin_url, github_url, portfolio_url,
                       resume_text, visa_status, work_authorization,
                       willing_to_relocate, availability,
                       salary_expectation, preferred_roles,
                       languages_spoken, remote_preference
                FROM charvak_candidates
                WHERE email = %s
                LIMIT 1
            """, (user_email,))
            c = cur.fetchone()

            # 3. Readiness certificate (if present)
            cert = None
            if certificate_id:
                cur.execute("""
                    SELECT certificate_id, display_name, role, industry, level,
                           readiness_score, percentile, benchmark_score,
                           verdict, certificate_hash, created_at
                    FROM charvak_readiness_certificates
                    WHERE certificate_id = %s
                """, (certificate_id,))
                cert = cur.fetchone()

            # 4. Consent
            consent = None
            cur.execute("""
                SELECT consent_id, consent_method, consented_at,
                       ip_address, user_agent, consent_proof_doc_id
                FROM charvak_candidate_consents
                WHERE email = %s AND role_id = %s
                ORDER BY consented_at DESC LIMIT 1
            """, (user_email, role_id))
            consent = cur.fetchone()

            # 5. Documents manifest
            docs = []
            if c:
                cur.execute("""
                    SELECT document_id, document_type, filename, content_type,
                           size_bytes, uploaded_at
                    FROM charvak_candidate_documents
                    WHERE candidate_id = %s
                    ORDER BY uploaded_at DESC
                """, (c[0],))
                docs = cur.fetchall()

            # 6. Screening answers with question text
            cur.execute("""
                SELECT q.question_num, q.question_text, q.answer_type,
                       q.fill_source, a.answer_text, a.answered_by, a.answered_at
                FROM charvak_role_screening_questions q
                LEFT JOIN charvak_role_screening_answers a
                    ON a.question_id = q.question_id
                   AND a.role_id = q.role_id
                WHERE q.role_id = %s
                ORDER BY q.question_num, q.sort_order
            """, (role_id,))
            questions = cur.fetchall()

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"build_cbrex_package failed: {e}")
            return {"status": "error", "message": f"Build failed: {e}"}

        def s(v):
            """Stringify null-safe."""
            return "" if v is None else (str(v) if not isinstance(v, str) else v)

        def jsonlist(v):
            if v is None:
                return []
            if isinstance(v, list):
                return v
            try:
                import json as _j
                return _j.loads(v) if isinstance(v, str) else list(v)
            except Exception:
                return []

        # Personal section
        first_name = s(c[18]) if c else ""
        last_name = s(c[19]) if c else ""
        if not first_name and not last_name and c:
            parts = s(c[1]).split(" ", 1)
            first_name = parts[0] if parts else ""
            last_name = parts[1] if len(parts) > 1 else ""

        personal = {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": s(c[1]) if c else "",
            "country": s(c[28]) if c and len(c) > 28 else "India",
            "current_location": s(c[4]) if c else "",
        }

        # Contact section
        contact = {
            "primary_email": s(user_email),
            "additional_email": s(c[20]) if c else "",
            "primary_phone": s(c[3]) if c else "",
            "additional_phone": s(c[21]) if c else "",
            "linkedin_url": s(c[29]) if c else "",
            "github_url": s(c[30]) if c else "",
            "portfolio_url": s(c[31]) if c else "",
        }

        # Employment section
        employment = {
            "current_company": s(c[6]) if c else "",
            "current_designation": s(c[5]) if c else "",
            "total_experience_years": c[7] if c else None,
            "relevant_experience_years": c[8] if c else None,
            "current_salary": float(c[22]) if c and c[22] is not None else None,
            "current_salary_currency": s(c[23]) if c else "INR",
            "expected_hike_percent": c[24] if c else None,
            "variable_component": s(c[25]) if c else "",
            "other_benefits": s(c[26]) if c else "",
            "notice_period": s(c[9]) if c else "",
            "serving_notice_last_day": c[10].isoformat() if c and c[10] else None,
            "availability": s(c[36]) if c else "",
            "salary_expectation": s(c[37]) if c else "",
            "visa_status": s(c[33]) if c else "",
            "work_authorization": s(c[34]) if c else "",
            "willing_to_relocate": bool(c[35]) if c else False,
            "remote_preference": s(c[40]) if c else "",
        }

        # Education section
        education = {
            "qualification": s(c[12]) if c else "",
            "degree": s(c[13]) if c else "",
            "university": s(c[14]) if c else "",
            "graduation_year": c[15] if c else None,
            "gpa": float(c[16]) if c and c[16] is not None else None,
        }

        # Skills
        skills = jsonlist(c[11]) if c else []

        # Readiness section
        readiness = {
            "readiness_score": readiness_score,
            "certificate_id": certificate_id,
            "certificate_url": f"/readiness/{certificate_id}" if certificate_id else None,
            "verdict": s(cert[8]) if cert else None,
            "percentile": cert[6] if cert else None,
            "benchmark_score": cert[7] if cert else None,
            "certificate_hash": s(cert[9]) if cert else None,
        }

        # Screening answers
        screening = []
        for q in questions:
            screening.append({
                "question_num": q[0],
                "question_text": s(q[1]),
                "answer_type": s(q[2]),
                "fill_source": s(q[3]),
                "answer": s(q[4]),
                "answered_by": s(q[5]),
                "answered_at": q[6].isoformat() if q[6] else None,
            })

        # Attachments manifest
        attachments = {
            "resume_available": bool(c and c[31]),
            "resume_url": s(c[31]) if c and len(c) > 31 else "",
            "certificate_pdf_url": f"/api/readiness/{certificate_id}/download" if certificate_id else None,
            "consent_recorded": bool(consent),
            "consent_id": s(consent[0]) if consent else None,
            "consent_proof_doc_id": s(consent[5]) if consent else None,
            "uploaded_documents": [
                {
                    "document_id": d[0],
                    "document_type": d[1],
                    "filename": d[2],
                    "content_type": d[3],
                    "size_bytes": d[4],
                    "uploaded_at": d[5].isoformat() if d[5] else None,
                } for d in docs
            ],
        }

        # Candidate summary
        candidate_summary = s(c[27]) if c else ""

        # Meta
        meta = {
            "application_id": application_id,
            "role_id": role_id,
            "role_title": role_title,
            "client_name": client_name,
            "role_location": role_location,
            "role_skills": role_skills,
            "role_experience_min": role_exp_min,
            "role_experience_max": role_exp_max,
            "role_job_type": role_job_type,
            "role_priority": role_priority,
            "candidate_id": c[0] if c else None,
            "applied_at": app[7].isoformat() if app[7] else None,
            "submitted_at": submitted_at.isoformat() if submitted_at else None,
            "submission_status": app[6],
            "recruiter_notes": s(recruiter_notes),
            "generated_at": __import__("datetime").datetime.now().isoformat(),
        }

        return {
            "status": "success",
            "package": {
                "meta": meta,
                "personal": personal,
                "contact": contact,
                "employment": employment,
                "education": education,
                "skills": skills,
                "readiness": readiness,
                "candidate_summary": candidate_summary,
                "screening_answers": screening,
                "attachments": attachments,
            },
        }


    # Batch download (Session 25 Patch 5c.2) - delegates to helper module
    def build_batch_zip(self, role_id):
        from client_staffing_batch import build_role_batch_zip
        return build_role_batch_zip(self, role_id)


client_staffing_engine = ClientStaffingEngine()
