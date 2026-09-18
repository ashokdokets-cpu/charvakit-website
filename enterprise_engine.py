"""
Charvak Enterprise Engine
Complete enterprise career services: benchmarking, pathways, approvals,
appointments, compliance, tiering, resume books, kiosk, surveys
(DB-backed - Session B/2)
"""
import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.enterprise")


class EnterpriseEngine:
    """Complete enterprise career services platform (DB-backed)."""

    def __init__(self):
        self._ensure_tables()
        logger.info("Enterprise Engine ready (DB-backed) - 8 modules loaded")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_enterprise_salary_data (
                    salary_id        TEXT PRIMARY KEY,
                    university       TEXT,
                    major            TEXT DEFAULT '',
                    industry         TEXT DEFAULT '',
                    base_salary      NUMERIC(12,2) DEFAULT 0,
                    signing_bonus    NUMERIC(12,2) DEFAULT 0,
                    location         TEXT DEFAULT '',
                    graduation_year  INTEGER DEFAULT 2026,
                    recorded_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_salary_univ ON charvak_enterprise_salary_data(university)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_salary_inds ON charvak_enterprise_salary_data(industry)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_salary_loc  ON charvak_enterprise_salary_data(location)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_enterprise_pathways (
                    pathway_id   TEXT PRIMARY KEY,
                    name         TEXT,
                    description  TEXT DEFAULT '',
                    steps        JSONB DEFAULT '[]'::jsonb,
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_pathways_name ON charvak_enterprise_pathways(name)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_enterprise_resume_approvals (
                    review_id          TEXT PRIMARY KEY,
                    student_id         TEXT,
                    student_name       TEXT,
                    resume_text        TEXT DEFAULT '',
                    status             TEXT DEFAULT 'pending',
                    reviewer_comments  TEXT DEFAULT '',
                    submitted_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at        TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_resume_student ON charvak_enterprise_resume_approvals(student_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_resume_status  ON charvak_enterprise_resume_approvals(status)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_enterprise_appointments (
                    appointment_id     TEXT PRIMARY KEY,
                    student_id         TEXT,
                    student_name       TEXT,
                    advisor_id         TEXT,
                    date               TEXT,
                    duration_minutes   INTEGER DEFAULT 30,
                    reason             TEXT DEFAULT 'Career Counseling',
                    status             TEXT DEFAULT 'booked',
                    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_appt_advisor ON charvak_enterprise_appointments(advisor_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_appt_student ON charvak_enterprise_appointments(student_id)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_enterprise_employer_tiers (
                    tier_id       TEXT PRIMARY KEY,
                    company_name  TEXT,
                    tier          TEXT DEFAULT 'tier2',
                    notes         TEXT DEFAULT '',
                    set_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_tiers_tier    ON charvak_enterprise_employer_tiers(tier)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_tiers_company ON charvak_enterprise_employer_tiers(company_name)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_enterprise_resume_books (
                    book_id      TEXT PRIMARY KEY,
                    name         TEXT,
                    description  TEXT DEFAULT '',
                    student_ids  JSONB DEFAULT '[]'::jsonb,
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_books_name ON charvak_enterprise_resume_books(name)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_enterprise_surveys (
                    survey_id   TEXT PRIMARY KEY,
                    title       TEXT,
                    questions   JSONB DEFAULT '[]'::jsonb,
                    responses   INTEGER DEFAULT 0,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_surveys_title ON charvak_enterprise_surveys(title)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_enterprise_kiosk_sessions (
                    kiosk_id     TEXT PRIMARY KEY,
                    event_id     TEXT,
                    location     TEXT DEFAULT 'Main Entrance',
                    status       TEXT DEFAULT 'active',
                    check_ins    INTEGER DEFAULT 0,
                    started_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_kiosks_event  ON charvak_enterprise_kiosk_sessions(event_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ent_kiosks_status ON charvak_enterprise_kiosk_sessions(status)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_enterprise_kiosk_events (
                    event_id        TEXT PRIMARY KEY,
                    kiosk_id        TEXT NOT NULL,
                    student_id      TEXT NOT NULL,
                    checked_in_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_kiosk_events_kiosk   ON charvak_enterprise_kiosk_events(kiosk_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_kiosk_events_student ON charvak_enterprise_kiosk_events(student_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_kiosk_events_time    ON charvak_enterprise_kiosk_events(checked_in_at)''')

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"enterprise tables init failed: {e}")

    # ============================================================
    # 1. SALARY BENCHMARKING
    # ============================================================

    def record_salary(self, data: Dict) -> Dict:
        """Record anonymized salary data."""
        salary_id = f"SAL-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_enterprise_salary_data
                    (salary_id, university, major, industry, base_salary,
                     signing_bonus, location, graduation_year)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                salary_id,
                data.get("university", "Unknown"),
                data.get("major", ""),
                data.get("industry", ""),
                float(data.get("base_salary", 0)),
                float(data.get("signing_bonus", 0)),
                data.get("location", ""),
                int(data.get("graduation_year", 2026)),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"record_salary failed: {e}")
            return {"status": "error", "message": "Could not record salary"}

        return {"status": "success", "salary_id": salary_id, "message": "Salary recorded anonymously"}

    def get_salary_benchmarks(self, filters: Dict = None) -> Dict:
        """Get anonymized salary benchmarks."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            where_parts = []
            params = []
            if filters:
                if filters.get("university"):
                    where_parts.append("university = %s")
                    params.append(filters["university"])
                if filters.get("major"):
                    where_parts.append("LOWER(major) LIKE %s")
                    params.append(f"%{filters['major'].lower()}%")
                if filters.get("industry"):
                    where_parts.append("LOWER(industry) LIKE %s")
                    params.append(f"%{filters['industry'].lower()}%")
                if filters.get("location"):
                    where_parts.append("LOWER(location) LIKE %s")
                    params.append(f"%{filters['location'].lower()}%")

            sql = '''
                SELECT salary_id, university, major, industry, base_salary,
                       signing_bonus, location, graduation_year
                FROM charvak_enterprise_salary_data
            '''
            if where_parts:
                sql += " WHERE " + " AND ".join(where_parts)
            cur.execute(sql, params)
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_salary_benchmarks failed: {e}")
            return {"status": "success", "count": 0, "message": "No data available"}

        if not rows:
            return {"status": "success", "count": 0, "message": "No data available"}

        data = [{
            "salary_id": r[0],
            "university": r[1],
            "major": r[2] or "",
            "industry": r[3] or "",
            "base_salary": float(r[4]) if r[4] is not None else 0,
            "signing_bonus": float(r[5]) if r[5] is not None else 0,
            "location": r[6] or "",
            "graduation_year": r[7],
        } for r in rows]

        salaries = [d["base_salary"] for d in data if d["base_salary"] > 0]
        bonuses = [d["signing_bonus"] for d in data if d["signing_bonus"] > 0]

        def _median(vals):
            if not vals:
                return 0
            s = sorted(vals)
            n = len(s)
            return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2

        return {
            "status": "success",
            "count": len(data),
            "benchmarks": {
                "average_base_salary": round(sum(salaries) / len(salaries), 2) if salaries else 0,
                "median_base_salary": round(_median(salaries), 2),
                "average_signing_bonus": round(sum(bonuses) / len(bonuses), 2) if bonuses else 0,
                "median_signing_bonus": round(_median(bonuses), 2),
                "top_industries": self._get_top_industries(data),
                "top_locations": self._get_top_locations(data),
            },
        }

    # ============================================================
    # 2. STUDENT PATHWAYS
    # ============================================================

    def create_pathway(self, data: Dict) -> Dict:
        """Create a career pathway."""
        pathway_id = f"PATH-{secrets.token_hex(4).upper()}"

        steps = data.get("steps", [
            {"name": "Upload Resume", "required": True},
            {"name": "Take Skill Check", "required": True},
            {"name": "Complete Micro-Internship", "required": False},
            {"name": "Earn Verified Badge", "required": True},
            {"name": "Apply to Jobs", "required": True},
        ])

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_enterprise_pathways (pathway_id, name, description, steps)
                VALUES (%s, %s, %s, %s::jsonb)
            ''', (
                pathway_id,
                data.get("name", "Career Readiness Track"),
                data.get("description", ""),
                json.dumps(steps),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_pathway failed: {e}")
            return {"status": "error", "message": "Could not create pathway"}

        return {"status": "success", "pathway_id": pathway_id, "message": "Pathway created"}

    def assign_pathway(self, student_id: str, pathway_id: str) -> Dict:
        """Assign a pathway to a student (stateless - no write in original)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT pathway_id, name, description, steps, created_at
                FROM charvak_enterprise_pathways WHERE pathway_id = %s
            ''', (pathway_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"assign_pathway failed: {e}")
            return {"status": "error", "message": "Pathway not found"}

        if not row:
            return {"status": "error", "message": "Pathway not found"}

        steps = row[3] if isinstance(row[3], list) else json.loads(row[3] or "[]")
        pathway = {
            "pathway_id": row[0],
            "name": row[1],
            "description": row[2] or "",
            "steps": steps,
            "created_at": row[4].isoformat() if hasattr(row[4], "isoformat") else str(row[4]),
        }

        return {
            "status": "success",
            "student_id": student_id,
            "pathway": pathway,
            "progress": [{"step": s["name"], "completed": False} for s in steps],
        }

    # ============================================================
    # 3. RESUME APPROVAL WORKFLOW
    # ============================================================

    def submit_resume_for_review(self, data: Dict) -> Dict:
        """Submit resume for approval."""
        review_id = f"REV-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_enterprise_resume_approvals
                    (review_id, student_id, student_name, resume_text, status)
                VALUES (%s, %s, %s, %s, 'pending')
            ''', (
                review_id,
                data.get("student_id"),
                data.get("student_name"),
                data.get("resume_text", ""),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"submit_resume_for_review failed: {e}")
            return {"status": "error", "message": "Could not submit resume"}

        return {"status": "success", "review_id": review_id, "message": "Resume submitted for review"}

    def review_resume(self, review_id: str, decision: str, comments: str = "") -> Dict:
        """Review a resume."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_enterprise_resume_approvals
                SET status = %s, reviewer_comments = %s, reviewed_at = CURRENT_TIMESTAMP
                WHERE review_id = %s
            ''', (decision, comments, review_id))
            affected = cur.rowcount
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"review_resume failed: {e}")
            return {"status": "error", "message": "Review not found"}

        if affected == 0:
            return {"status": "error", "message": "Review not found"}
        verb = {"approve": "approved", "reject": "rejected"}.get(decision, decision)
        return {"status": "success", "message": f"Resume {verb}"}

    def get_pending_reviews(self) -> Dict:
        """Get all pending resume reviews."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT review_id, student_id, student_name, resume_text,
                       status, reviewer_comments, submitted_at, reviewed_at
                FROM charvak_enterprise_resume_approvals
                WHERE status = 'pending'
                ORDER BY submitted_at ASC
            ''')
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_pending_reviews failed: {e}")
            return {"status": "success", "pending": [], "count": 0}

        pending = [{
            "review_id": r[0],
            "student_id": r[1],
            "student_name": r[2],
            "resume_text": r[3] or "",
            "status": r[4],
            "reviewer_comments": r[5] or "",
            "submitted_at": r[6].isoformat() if hasattr(r[6], "isoformat") else str(r[6]),
            "reviewed_at": r[7].isoformat() if r[7] and hasattr(r[7], "isoformat") else None,
        } for r in rows]

        return {"status": "success", "pending": pending, "count": len(pending)}

    # ============================================================
    # 4. APPOINTMENT BOOKING
    # ============================================================

    def create_appointment(self, data: Dict) -> Dict:
        """Book an appointment."""
        appointment_id = f"APT-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_enterprise_appointments
                    (appointment_id, student_id, student_name, advisor_id, date,
                     duration_minutes, reason, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'booked')
            ''', (
                appointment_id,
                data.get("student_id"),
                data.get("student_name"),
                data.get("advisor_id", "ADVISOR-001"),
                data.get("date"),
                int(data.get("duration_minutes", 30)),
                data.get("reason", "Career Counseling"),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_appointment failed: {e}")
            return {"status": "error", "message": "Could not book appointment"}

        return {"status": "success", "appointment_id": appointment_id, "message": "Appointment booked"}

    def get_appointments(self, advisor_id: str = None) -> Dict:
        """Get appointments."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            if advisor_id:
                cur.execute('''
                    SELECT appointment_id, student_id, student_name, advisor_id,
                           date, duration_minutes, reason, status, created_at
                    FROM charvak_enterprise_appointments
                    WHERE advisor_id = %s
                    ORDER BY created_at ASC
                ''', (advisor_id,))
            else:
                cur.execute('''
                    SELECT appointment_id, student_id, student_name, advisor_id,
                           date, duration_minutes, reason, status, created_at
                    FROM charvak_enterprise_appointments
                    ORDER BY created_at ASC
                ''')
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_appointments failed: {e}")
            return {"status": "error", "message": "Could not load appointments"}

        appointments = [{
            "appointment_id": r[0],
            "student_id": r[1],
            "student_name": r[2],
            "advisor_id": r[3],
            "date": r[4],
            "duration_minutes": r[5],
            "reason": r[6],
            "status": r[7],
            "created_at": r[8].isoformat() if hasattr(r[8], "isoformat") else str(r[8]),
        } for r in rows]

        return {"status": "success", "appointments": appointments, "count": len(appointments)}

    # ============================================================
    # 5. EMPLOYER TIERING
    # ============================================================

    def set_employer_tier(self, data: Dict) -> Dict:
        """Set employer tier."""
        tier_id = f"TIER-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_enterprise_employer_tiers
                    (tier_id, company_name, tier, notes)
                VALUES (%s, %s, %s, %s)
            ''', (
                tier_id,
                data.get("company_name"),
                data.get("tier", "tier2"),
                data.get("notes", ""),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"set_employer_tier failed: {e}")
            return {"status": "error", "message": "Could not set employer tier"}

        return {
            "status": "success",
            "tier_id": tier_id,
            "message": f"{data.get('company_name')} set as {data.get('tier')}",
        }

    def get_employers_by_tier(self, tier: str = None) -> Dict:
        """Get employers by tier."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            if tier:
                cur.execute('''
                    SELECT tier_id, company_name, tier, notes, set_at
                    FROM charvak_enterprise_employer_tiers
                    WHERE tier = %s
                    ORDER BY set_at ASC
                ''', (tier,))
            else:
                cur.execute('''
                    SELECT tier_id, company_name, tier, notes, set_at
                    FROM charvak_enterprise_employer_tiers
                    ORDER BY set_at ASC
                ''')
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_employers_by_tier failed: {e}")
            return {"status": "error", "message": "Could not load employers"}

        employers = [{
            "tier_id": r[0],
            "company_name": r[1],
            "tier": r[2],
            "notes": r[3] or "",
            "set_at": r[4].isoformat() if hasattr(r[4], "isoformat") else str(r[4]),
        } for r in rows]

        return {"status": "success", "employers": employers, "count": len(employers)}

    # ============================================================
    # 6. RESUME BOOKS
    # ============================================================

    def create_resume_book(self, data: Dict) -> Dict:
        """Create a resume book."""
        book_id = f"BOOK-{secrets.token_hex(4).upper()}"
        student_ids = data.get("student_ids", [])

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_enterprise_resume_books
                    (book_id, name, description, student_ids)
                VALUES (%s, %s, %s, %s::jsonb)
            ''', (
                book_id,
                data.get("name", "Resume Book"),
                data.get("description", ""),
                json.dumps(student_ids),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_resume_book failed: {e}")
            return {"status": "error", "message": "Could not create resume book"}

        return {
            "status": "success",
            "book_id": book_id,
            "message": f"Resume book created with {len(student_ids)} students",
            "download_url": f"https://charvakit.com/api/resume-books/{book_id}/pdf",
        }

    # ============================================================
    # 7. SURVEY-ON-LOGIN
    # ============================================================

    def create_survey(self, data: Dict) -> Dict:
        """Create a survey."""
        survey_id = f"SURVEY-{secrets.token_hex(4).upper()}"

        questions = data.get("questions", [
            "Are you currently employed?",
            "What is your current salary?",
            "Who is your employer?",
            "What is your job title?",
        ])

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_enterprise_surveys
                    (survey_id, title, questions, responses)
                VALUES (%s, %s, %s::jsonb, 0)
            ''', (
                survey_id,
                data.get("title", "Outcome Survey"),
                json.dumps(questions),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_survey failed: {e}")
            return {"status": "error", "message": "Could not create survey"}

        return {"status": "success", "survey_id": survey_id, "message": "Survey created"}

    def record_survey_response(self, survey_id: str, data: Dict) -> Dict:
        """Record survey response (increments counter only - matches original)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_enterprise_surveys
                SET responses = responses + 1
                WHERE survey_id = %s
            ''', (survey_id,))
            affected = cur.rowcount
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"record_survey_response failed: {e}")
            return {"status": "error", "message": "Survey not found"}

        if affected == 0:
            return {"status": "error", "message": "Survey not found"}
        return {"status": "success", "message": "Response recorded"}

    # ============================================================
    # 8. KIOSK MODE
    # ============================================================

    def start_kiosk(self, data: Dict) -> Dict:
        """Start kiosk mode for event check-in."""
        kiosk_id = f"KIOSK-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_enterprise_kiosk_sessions
                    (kiosk_id, event_id, location, status, check_ins)
                VALUES (%s, %s, %s, 'active', 0)
            ''', (
                kiosk_id,
                data.get("event_id"),
                data.get("location", "Main Entrance"),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"start_kiosk failed: {e}")
            return {"status": "error", "message": "Could not start kiosk"}

        return {
            "status": "success",
            "kiosk_id": kiosk_id,
            "message": "Kiosk mode started!",
            "check_in_url": f"https://charvakit.com/kiosk/{kiosk_id}",
        }

    def kiosk_check_in(self, kiosk_id: str, student_id: str) -> Dict:
        """Check in student via kiosk (increments counter AND logs event)."""
        event_id = f"KEVT-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT 1 FROM charvak_enterprise_kiosk_sessions WHERE kiosk_id = %s', (kiosk_id,))
            if cur.fetchone() is None:
                cur.close(); conn.close()
                return {"status": "error", "message": "Kiosk not found"}

            # #37b fix: log the check-in event (who + when)
            cur.execute("""
                INSERT INTO charvak_enterprise_kiosk_events
                    (event_id, kiosk_id, student_id)
                VALUES (%s, %s, %s)
            """, (event_id, kiosk_id, student_id))

            cur.execute("""
                UPDATE charvak_enterprise_kiosk_sessions
                SET check_ins = check_ins + 1
                WHERE kiosk_id = %s
            """, (kiosk_id,))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"kiosk_check_in failed: {e}")
            return {"status": "error", "message": "Could not check in"}

        return {
            "status": "success",
            "event_id": event_id,
            "message": f"Student {student_id} checked in!",
        }

    # ============================================================
    # HELPERS
    # ============================================================

    def _get_top_industries(self, data: List[Dict], limit: int = 5) -> List[Dict]:
        industry_counts = {}
        for d in data:
            if d["industry"]:
                industry_counts[d["industry"]] = industry_counts.get(d["industry"], 0) + 1
        sorted_ind = sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"industry": i, "count": c} for i, c in sorted_ind[:limit]]

    def _get_top_locations(self, data: List[Dict], limit: int = 5) -> List[Dict]:
        loc_counts = {}
        for d in data:
            if d["location"]:
                loc_counts[d["location"]] = loc_counts.get(d["location"], 0) + 1
        sorted_loc = sorted(loc_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"location": l, "count": c} for l, c in sorted_loc[:limit]]

    # ============================================================
    # STATS
    # ============================================================

    def get_stats(self) -> Dict:
        """Get enterprise engine statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT COUNT(*) FROM charvak_enterprise_salary_data')
            salary_records = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_enterprise_pathways')
            pathways = int(cur.fetchone()[0] or 0)

            cur.execute("SELECT COUNT(*) FROM charvak_enterprise_resume_approvals WHERE status = 'pending'")
            pending_resume_reviews = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_enterprise_appointments')
            appointments = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_enterprise_employer_tiers')
            employer_tiers = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_enterprise_resume_books')
            resume_books = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_enterprise_surveys')
            surveys = int(cur.fetchone()[0] or 0)

            cur.execute("SELECT COUNT(*) FROM charvak_enterprise_kiosk_sessions WHERE status = 'active'")
            active_kiosks = int(cur.fetchone()[0] or 0)

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "salary_records": salary_records,
                "pathways": pathways,
                "pending_resume_reviews": pending_resume_reviews,
                "appointments": appointments,
                "employer_tiers": employer_tiers,
                "resume_books": resume_books,
                "surveys": surveys,
                "active_kiosks": active_kiosks,
            },
        }


enterprise_engine = EnterpriseEngine()
