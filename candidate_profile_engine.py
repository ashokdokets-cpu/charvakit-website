"""
Candidate Profile Engine (Session 30).

Read-only aggregation layer that presents a candidate's full activity
across all Charvak subsystems as one unified view. No writes, no schema
changes — pure reads across existing tables.

Design principles:
- One call = one screen. Everything `/career-center` needs, in one fetch.
- Section-isolated. A failure in one section never breaks the response.
- Aggregate large tables (integrity events, credit history).
- Enumerate small tables (certificates, applications, enrollments).
- Self-view only. This engine returns the caller's own data.
- Stable shape. Empty tables still return their section with empty lists,
  so the frontend can render consistent UI whether or not data exists.

Public API:
- get_unified_profile(email, include=None) -> dict
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Sections that can be selectively included via `include=[...]`
ALL_SECTIONS = [
    "identity",
    "profile",
    "assessments",
    "certificates",
    "applications",
    "training",
    "career_engine",
    "integrity",
    "credits",
    "doketsrb",
]


class CandidateProfileEngine:
    def __init__(self):
        pass

    # ---------------------------------------------------------------- public

    def get_unified_profile(self, email: str, include: Optional[List[str]] = None) -> Dict:
        """
        Return a unified view of a candidate's activity across all subsystems.

        email is required. include is an optional whitelist of sections.
        If include is None, all sections are returned.
        """
        email = (email or "").strip().lower()
        if not email:
            return {"status": "error", "message": "email required"}

        wanted = set(include) if include else set(ALL_SECTIONS)
        # Identity always included — cheap, and callers need it for rendering.
        wanted.add("identity")

        result = {
            "status": "success",
            "email": email,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "sections_included": sorted(wanted),
        }

        if "identity" in wanted:
            result["identity"] = self._safe_section(self._identity, email)
        if "profile" in wanted:
            result["profile"] = self._safe_section(self._profile, email)
        if "assessments" in wanted:
            result["assessments"] = self._safe_section(self._assessments, email)
        if "certificates" in wanted:
            result["certificates"] = self._safe_section(self._certificates, email)
        if "applications" in wanted:
            result["applications"] = self._safe_section(self._applications, email)
        if "training" in wanted:
            result["training"] = self._safe_section(self._training, email)
        if "career_engine" in wanted:
            result["career_engine"] = self._safe_section(self._career_engine, email)
        if "integrity" in wanted:
            result["integrity"] = self._safe_section(self._integrity, email)
        if "credits" in wanted:
            result["credits"] = self._safe_section(self._credits, email)
        if "doketsrb" in wanted:
            result["doketsrb"] = self._safe_section(self._doketsrb, email)

        return result

    # ----------------------------------------------------------- orchestrator

    def _safe_section(self, fn, email: str) -> Dict:
        """Wrap a section fetch so it can never crash the whole response."""
        try:
            out = fn(email)
            if not isinstance(out, dict):
                return {"status": "error", "message": "section returned non-dict"}
            return out
        except Exception as e:
            logger.warning(f"[candidate_profile] section {fn.__name__} failed: {e}")
            return {"status": "error", "message": str(e)[:200]}

    def _conn(self):
        from database import db
        return db.get_connection()

    # ------------------------------------------------------------ 1. identity

    def _identity(self, email: str) -> Dict:
        """Users table + candidate_id link."""
        conn = self._conn(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT user_id, email, name, phone, role, created_at
                FROM users WHERE LOWER(email) = %s
            """, (email,))
            user_row = cur.fetchone()

            cur.execute("""
                SELECT candidate_id FROM charvak_candidates WHERE LOWER(email) = %s
            """, (email,))
            cand_row = cur.fetchone()

            return {
                "status": "success",
                "user": {
                    "user_id": user_row[0] if user_row else None,
                    "email": user_row[1] if user_row else email,
                    "name": user_row[2] if user_row else None,
                    "phone": user_row[3] if user_row else None,
                    "role": user_row[4] if user_row else None,
                    "created_at": user_row[5].isoformat() if user_row and user_row[5] else None,
                } if user_row else None,
                "candidate_id": cand_row[0] if cand_row else None,
                "registered": bool(user_row),
            }
        finally:
            cur.close(); conn.close()

    # ------------------------------------------------------------- 2. profile

    def _profile(self, email: str) -> Dict:
        """Full profile from charvak_candidates + master_profiles."""
        conn = self._conn(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT candidate_id, name, first_name, last_name, phone,
                       additional_email, additional_phone,
                       skills, experience_years, relevant_experience_years,
                       job_title, current_company, preferred_roles,
                       location, country, visa_status, work_authorization,
                       portfolio_url, github_url, linkedin_url,
                       education, degree, major, university, gpa, graduation_year,
                       certifications, languages_spoken,
                       willing_to_relocate, remote_preference,
                       salary_expectation, current_salary_inr, current_salary_currency,
                       expected_hike_percent, variable_component, other_benefits,
                       notice_period, serving_notice_last_day,
                       availability, candidate_summary, status,
                       skill_score, badge_id, resume_text,
                       registered_at, updated_at
                FROM charvak_candidates WHERE LOWER(email) = %s
            """, (email,))
            r = cur.fetchone()
            if not r:
                return {"status": "success", "present": False, "profile": None}

            keys = [
                "candidate_id", "name", "first_name", "last_name", "phone",
                "additional_email", "additional_phone",
                "skills", "experience_years", "relevant_experience_years",
                "job_title", "current_company", "preferred_roles",
                "location", "country", "visa_status", "work_authorization",
                "portfolio_url", "github_url", "linkedin_url",
                "education", "degree", "major", "university", "gpa", "graduation_year",
                "certifications", "languages_spoken",
                "willing_to_relocate", "remote_preference",
                "salary_expectation", "current_salary_inr", "current_salary_currency",
                "expected_hike_percent", "variable_component", "other_benefits",
                "notice_period", "serving_notice_last_day",
                "availability", "candidate_summary", "status",
                "skill_score", "badge_id", "resume_text",
                "registered_at", "updated_at",
            ]
            profile = dict(zip(keys, r))
            # Coerce JSONB dicts already handled by psycopg2. Convert dates to iso.
            for k in ("registered_at", "updated_at", "serving_notice_last_day"):
                v = profile.get(k)
                if v is not None and hasattr(v, "isoformat"):
                    profile[k] = v.isoformat()
            # Trim resume_text (could be huge)
            if profile.get("resume_text"):
                profile["resume_text_preview"] = profile["resume_text"][:500]
                del profile["resume_text"]

            # Extended profile (master_profiles JSONB, may be empty)
            cur.execute("""
                SELECT data, created_at, updated_at
                FROM charvak_master_profiles WHERE LOWER(email) = %s
            """, (email,))
            mp = cur.fetchone()
            master = None
            if mp:
                master = {
                    "data": mp[0] if isinstance(mp[0], dict) else json.loads(mp[0] or "{}"),
                    "created_at": mp[1].isoformat() if mp[1] else None,
                    "updated_at": mp[2].isoformat() if mp[2] else None,
                }

            return {
                "status": "success",
                "present": True,
                "profile": profile,
                "master_profile": master,
            }
        finally:
            cur.close(); conn.close()

    # -------------------------------------------------------- 3. assessments

    def _assessments(self, email: str) -> Dict:
        """Career assessments + generic assessment results. Aggregated counts + recent."""
        conn = self._conn(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT COUNT(*), MAX(completed_at)
                FROM charvak_career_assessments
                WHERE LOWER(email) = %s AND status = 'completed'
            """, (email,))
            n_career, last_career = cur.fetchone()

            cur.execute("""
                SELECT assessment_id, role, industry, level, format, size,
                       score, passed, correct_count, num_questions,
                       started_at, completed_at
                FROM charvak_career_assessments
                WHERE LOWER(email) = %s AND status = 'completed'
                ORDER BY completed_at DESC NULLS LAST LIMIT 5
            """, (email,))
            recent_career = []
            for r in cur.fetchall():
                recent_career.append({
                    "assessment_id": r[0], "role": r[1], "industry": r[2],
                    "level": r[3], "format": r[4], "size": r[5],
                    "score": r[6], "passed": r[7], "correct_count": r[8],
                    "num_questions": r[9],
                    "started_at": r[10].isoformat() if r[10] else None,
                    "completed_at": r[11].isoformat() if r[11] else None,
                })

            cur.execute("""
                SELECT COUNT(*) FROM charvak_assessment_results WHERE LOWER(email) = %s
            """, (email,))
            n_results = cur.fetchone()[0]

            cur.execute("""
                SELECT result_id, assessment_type, assessment_name, score, percentage,
                       passed, completed_at
                FROM charvak_assessment_results WHERE LOWER(email) = %s
                ORDER BY completed_at DESC LIMIT 5
            """, (email,))
            recent_results = []
            for r in cur.fetchall():
                recent_results.append({
                    "result_id": r[0], "assessment_type": r[1], "assessment_name": r[2],
                    "score": float(r[3]) if r[3] is not None else None,
                    "percentage": float(r[4]) if r[4] is not None else None,
                    "passed": r[5],
                    "completed_at": r[6].isoformat() if r[6] else None,
                })

            # Per-skill ability
            cur.execute("""
                SELECT skill, ability_score, attempts, last_updated
                FROM charvak_user_ability WHERE LOWER(email) = %s
                ORDER BY last_updated DESC
            """, (email,))
            ability = []
            for r in cur.fetchall():
                ability.append({
                    "skill": r[0],
                    "ability_score": float(r[1]) if r[1] is not None else None,
                    "attempts": r[2],
                    "last_updated": r[3].isoformat() if r[3] else None,
                })

            return {
                "status": "success",
                "career_assessments_completed": n_career or 0,
                "career_last_completed_at": last_career.isoformat() if last_career else None,
                "recent_career_assessments": recent_career,
                "total_assessment_results": n_results or 0,
                "recent_results": recent_results,
                "ability": ability,
            }
        finally:
            cur.close(); conn.close()

    # ------------------------------------------------------- 4. certificates

    def _certificates(self, email: str) -> Dict:
        """Readiness certs + course completion certs."""
        conn = self._conn(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT certificate_id, role, industry, level,
                       readiness_score, percentile, benchmark_score, verdict,
                       source, certificate_hash, created_at, superseded_by
                FROM charvak_readiness_certificates
                WHERE LOWER(email) = %s
                ORDER BY created_at DESC
            """, (email,))
            readiness = []
            for r in cur.fetchall():
                readiness.append({
                    "certificate_id": r[0], "role": r[1], "industry": r[2], "level": r[3],
                    "readiness_score": r[4], "percentile": r[5], "benchmark_score": r[6],
                    "verdict": r[7], "source": r[8], "hash": r[9],
                    "created_at": r[10].isoformat() if r[10] else None,
                    "superseded_by": r[11],
                    "url": f"/readiness/{r[0]}",
                })

            cur.execute("""
                SELECT certificate_id, enrollment_id, course_name, duration_weeks,
                       recipient_name, issued_at
                FROM charvak_certificates
                WHERE LOWER(email) = %s
                ORDER BY issued_at DESC
            """, (email,))
            courses = []
            for r in cur.fetchall():
                courses.append({
                    "certificate_id": r[0], "enrollment_id": r[1],
                    "course_name": r[2], "duration_weeks": r[3],
                    "recipient_name": r[4],
                    "issued_at": r[5].isoformat() if r[5] else None,
                    "url": f"/certificate/{r[0]}",
                })

            return {
                "status": "success",
                "readiness_certificates": readiness,
                "course_certificates": courses,
                "total": len(readiness) + len(courses),
            }
        finally:
            cur.close(); conn.close()

    # ------------------------------------------------------- 5. applications

    def _applications(self, email: str) -> Dict:
        """Staffing (via charvak_applications), micro-project, and generic."""
        conn = self._conn(); cur = conn.cursor()
        try:
            # charvak_applications: user_id may be candidate_id OR email.
            # Try candidate_id join first; fall back to direct user_id match.
            cur.execute("""
                SELECT a.application_id, a.job_id, a.client_role_id, a.user_id,
                       a.status, a.submission_status, a.certificate_id,
                       a.readiness_score, a.applied_at, a.created_at
                FROM charvak_applications a
                LEFT JOIN charvak_candidates c
                    ON a.user_id = c.candidate_id OR LOWER(a.user_id) = c.email
                WHERE LOWER(COALESCE(c.email, a.user_id)) = %s
                ORDER BY a.created_at DESC NULLS LAST
            """, (email,))
            staffing = []
            for r in cur.fetchall():
                staffing.append({
                    "application_id": r[0], "job_id": r[1], "client_role_id": r[2],
                    "user_id": r[3], "status": r[4], "submission_status": r[5],
                    "certificate_id": r[6], "readiness_score": r[7],
                    "applied_at": r[8], "created_at": r[9].isoformat() if r[9] else None,
                })

            # micro applications
            cur.execute("""
                SELECT application_id, project_id, status, ai_score, applied_at,
                       assigned_at, submitted_at, approved_at
                FROM charvak_micro_applications WHERE LOWER(candidate_email) = %s
                ORDER BY applied_at DESC NULLS LAST
            """, (email,))
            micro = []
            for r in cur.fetchall():
                micro.append({
                    "application_id": r[0], "project_id": r[1], "status": r[2],
                    "ai_score": r[3],
                    "applied_at": r[4].isoformat() if r[4] else None,
                    "assigned_at": r[5].isoformat() if r[5] else None,
                    "submitted_at": r[6].isoformat() if r[6] else None,
                    "approved_at": r[7].isoformat() if r[7] else None,
                })

            # consents (candidate gave for staffing roles)
            cur.execute("""
                SELECT consent_id, role_id, vendor, consent_method,
                       consented_at, ip_address
                FROM charvak_candidate_consents
                WHERE LOWER(email) = %s ORDER BY consented_at DESC
            """, (email,))
            consents = []
            for r in cur.fetchall():
                consents.append({
                    "consent_id": r[0], "role_id": r[1], "vendor": r[2],
                    "consent_method": r[3],
                    "consented_at": r[4].isoformat() if r[4] else None,
                    "ip_address": r[5],
                })

            return {
                "status": "success",
                "staffing_applications": staffing,
                "micro_applications": micro,
                "consents": consents,
                "totals": {
                    "staffing": len(staffing),
                    "micro": len(micro),
                    "consents": len(consents),
                },
            }
        finally:
            cur.close(); conn.close()

    # ---------------------------------------------------------- 6. training

    def _training(self, email: str) -> Dict:
        """AI course enrollments + internships + generic training."""
        conn = self._conn(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT enrollment_id, course_name, duration_weeks, user_level,
                       progress, total_weeks, status, started_at, completed_at
                FROM charvak_enrollments WHERE LOWER(email) = %s
                ORDER BY started_at DESC
            """, (email,))
            courses = []
            for r in cur.fetchall():
                courses.append({
                    "enrollment_id": r[0], "course_name": r[1], "duration_weeks": r[2],
                    "user_level": r[3], "progress": r[4], "total_weeks": r[5],
                    "status": r[6],
                    "started_at": r[7].isoformat() if r[7] else None,
                    "completed_at": r[8].isoformat() if r[8] else None,
                })

            cur.execute("""
                SELECT enrollment_id, program_id, duration, total_days, current_day,
                       status, tier_key, start_date, completed_at, amount_paid_inr
                FROM charvak_ai_internship_enrollments WHERE LOWER(email) = %s
                ORDER BY start_date DESC
            """, (email,))
            internships = []
            for r in cur.fetchall():
                internships.append({
                    "enrollment_id": r[0], "program_id": r[1], "duration": r[2],
                    "total_days": r[3], "current_day": r[4], "status": r[5],
                    "tier_key": r[6],
                    "start_date": r[7].isoformat() if r[7] else None,
                    "completed_at": r[8].isoformat() if r[8] else None,
                    "amount_paid_inr": r[9],
                })

            return {
                "status": "success",
                "courses": courses,
                "internships": internships,
                "totals": {"courses": len(courses), "internships": len(internships)},
            }
        finally:
            cur.close(); conn.close()

    # ----------------------------------------------------- 7. career engine

    def _career_engine(self, email: str) -> Dict:
        """Saved jobs, alerts, interviews, offers, company follows."""
        conn = self._conn(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT save_id, job_id, saved_at
                FROM charvak_career_saved_jobs WHERE LOWER(email) = %s
                ORDER BY saved_at DESC LIMIT 20
            """, (email,))
            saved = [{"save_id": r[0], "job_id": r[1],
                      "saved_at": r[2].isoformat() if r[2] else None} for r in cur.fetchall()]

            cur.execute("""
                SELECT alert_id, keywords, location, frequency, created_at
                FROM charvak_career_job_alerts WHERE LOWER(email) = %s
                ORDER BY created_at DESC
            """, (email,))
            alerts = [{"alert_id": r[0],
                       "keywords": r[1] if isinstance(r[1], list) else json.loads(r[1] or "[]"),
                       "location": r[2], "frequency": r[3],
                       "created_at": r[4].isoformat() if r[4] else None} for r in cur.fetchall()]

            cur.execute("""
                SELECT interview_id, employer, role, date, platform, status, created_at
                FROM charvak_career_interviews WHERE LOWER(candidate_email) = %s
                ORDER BY created_at DESC LIMIT 20
            """, (email,))
            interviews = [{"interview_id": r[0], "employer": r[1], "role": r[2],
                           "date": r[3], "platform": r[4], "status": r[5],
                           "created_at": r[6].isoformat() if r[6] else None} for r in cur.fetchall()]

            cur.execute("""
                SELECT offer_id, company, role, salary, status, created_at
                FROM charvak_career_offers WHERE LOWER(candidate_email) = %s
                ORDER BY created_at DESC LIMIT 20
            """, (email,))
            offers = [{"offer_id": r[0], "company": r[1], "role": r[2],
                       "salary": float(r[3]) if r[3] is not None else None,
                       "status": r[4],
                       "created_at": r[5].isoformat() if r[5] else None} for r in cur.fetchall()]

            cur.execute("""
                SELECT follow_id, company, followed_at
                FROM charvak_career_company_follows WHERE LOWER(email) = %s
                ORDER BY followed_at DESC LIMIT 20
            """, (email,))
            follows = [{"follow_id": r[0], "company": r[1],
                        "followed_at": r[2].isoformat() if r[2] else None} for r in cur.fetchall()]

            return {
                "status": "success",
                "saved_jobs": saved,
                "job_alerts": alerts,
                "interviews": interviews,
                "offers": offers,
                "company_follows": follows,
                "totals": {
                    "saved_jobs": len(saved), "job_alerts": len(alerts),
                    "interviews": len(interviews), "offers": len(offers),
                    "company_follows": len(follows),
                },
            }
        finally:
            cur.close(); conn.close()

    # ------------------------------------------------------------- 8. integrity

    def _integrity(self, email: str) -> Dict:
        """AGGREGATED integrity summary. Not a list — could be thousands of rows."""
        conn = self._conn(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT event_type, COUNT(*)
                FROM charvak_assessment_integrity_events
                WHERE LOWER(email) = %s
                GROUP BY event_type
            """, (email,))
            counts = {}
            total = 0
            for r in cur.fetchall():
                counts[r[0]] = int(r[1])
                total += int(r[1])

            cur.execute("""
                SELECT COUNT(DISTINCT assessment_id), MAX(occurred_at)
                FROM charvak_assessment_integrity_events
                WHERE LOWER(email) = %s
            """, (email,))
            n_assessments, last_event = cur.fetchone()

            # Pull summary JSONB from charvak_career_assessments (pre-computed per assessment)
            cur.execute("""
                SELECT assessment_id, integrity_summary
                FROM charvak_career_assessments
                WHERE LOWER(email) = %s AND integrity_summary IS NOT NULL
                      AND integrity_summary != '{}'::jsonb
                ORDER BY completed_at DESC NULLS LAST LIMIT 10
            """, (email,))
            per_assessment = []
            for r in cur.fetchall():
                per_assessment.append({
                    "assessment_id": r[0],
                    "summary": r[1] if isinstance(r[1], dict) else json.loads(r[1] or "{}"),
                })

            # Risk classification mirroring integrity_engine.compute_risk_level
            pastes = counts.get("paste", 0)
            tabs = counts.get("tab_switch", 0)
            if total == 0:
                risk = "clean"
            elif total > 15 or (tabs >= 3 and pastes >= 2):
                risk = "elevated"
            elif total >= 6:
                risk = "moderate"
            elif total >= 1:
                risk = "minor"
            else:
                risk = "clean"

            return {
                "status": "success",
                "total_events": total,
                "counts": counts,
                "assessments_with_events": n_assessments or 0,
                "last_event_at": last_event.isoformat() if last_event else None,
                "overall_risk_level": risk,
                "per_assessment": per_assessment,
            }
        finally:
            cur.close(); conn.close()

    # --------------------------------------------------------------- 9. credits

    def _credits(self, email: str) -> Dict:
        """Credit balance + usage aggregated by feature."""
        conn = self._conn(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT plan, credits_remaining, total_credits_used, total_ai_calls, expires_at
                FROM charvak_user_credits WHERE LOWER(email) = %s
            """, (email,))
            r = cur.fetchone()
            balance = {
                "plan": r[0], "credits_remaining": r[1],
                "total_credits_used": r[2], "total_ai_calls": r[3],
                "expires_at": r[4].isoformat() if r[4] else None,
            } if r else None

            cur.execute("""
                SELECT feature, COUNT(*), SUM(credits_used)
                FROM charvak_credit_usage_history WHERE LOWER(email) = %s
                GROUP BY feature ORDER BY SUM(credits_used) DESC
            """, (email,))
            by_feature = [{"feature": r[0], "calls": int(r[1]),
                           "credits_used": int(r[2] or 0)} for r in cur.fetchall()]

            return {
                "status": "success",
                "balance": balance,
                "usage_by_feature": by_feature,
            }
        finally:
            cur.close(); conn.close()

    # ------------------------------------------------------------- 10. doketsrb

    def _doketsrb(self, email: str) -> Dict:
        """DoketsRB ATS scores. Empty until a candidate runs /ats."""
        conn = self._conn(); cur = conn.cursor()
        try:
            # Match via candidate_id (linked from charvak_candidates)
            cur.execute("""
                SELECT e.event_id, e.candidate_id, e.score, e.source,
                       e.target_role, e.metadata, e.created_at
                FROM charvak_doketsrb_score_events e
                JOIN charvak_candidates c ON e.candidate_id = c.candidate_id
                WHERE LOWER(c.email) = %s
                ORDER BY e.created_at DESC LIMIT 20
            """, (email,))
            events = []
            for r in cur.fetchall():
                events.append({
                    "event_id": r[0], "candidate_id": r[1], "score": r[2],
                    "source": r[3], "target_role": r[4],
                    "metadata": r[5] if isinstance(r[5], dict) else json.loads(r[5] or "{}"),
                    "created_at": r[6].isoformat() if r[6] else None,
                })
            return {"status": "success", "score_events": events, "total": len(events)}
        finally:
            cur.close(); conn.close()


# Singleton, matching the codebase convention.
candidate_profile_engine = CandidateProfileEngine()