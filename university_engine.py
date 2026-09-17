"""
Charvak University Engine
University admin portal + first-destination outcome reporting
(DB-backed - Session D/3)
"""
import json
import logging
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.university")


class UniversityEngine:
    """Handles university partnerships and outcome reporting (DB-backed)."""

    def __init__(self):
        self._ensure_tables()
        logger.info("University Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_universities (
                    university_id   TEXT PRIMARY KEY,
                    name            TEXT,
                    admin_email     TEXT,
                    location        TEXT DEFAULT '',
                    type            TEXT DEFAULT 'University',
                    student_count   INTEGER DEFAULT 0,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_universities_admin ON charvak_universities(admin_email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_universities_name  ON charvak_universities(name)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_university_students (
                    student_id        TEXT PRIMARY KEY,
                    university_id     TEXT NOT NULL,
                    name              TEXT,
                    email             TEXT,
                    graduation_year   INTEGER DEFAULT 2026,
                    status            TEXT DEFAULT 'enrolled',
                    placement_status  TEXT DEFAULT 'not_placed',
                    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_unistudents_university ON charvak_university_students(university_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_unistudents_email      ON charvak_university_students(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_unistudents_placement  ON charvak_university_students(placement_status)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_university_outcomes (
                    outcome_id     TEXT PRIMARY KEY,
                    student_id     TEXT NOT NULL,
                    outcome_type   TEXT DEFAULT 'employed',
                    company_name   TEXT DEFAULT '',
                    salary         NUMERIC(12,2) DEFAULT 0,
                    job_title      TEXT DEFAULT '',
                    location       TEXT DEFAULT '',
                    recorded_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_unioutcomes_student ON charvak_university_outcomes(student_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_unioutcomes_type    ON charvak_university_outcomes(outcome_type)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"university tables init failed: {e}")

    # ============================================================
    # SERIALIZERS
    # ============================================================

    @staticmethod
    def _row_to_university(row) -> Dict:
        if not row:
            return {}
        return {
            "university_id": row[0],
            "name": row[1],
            "admin_email": row[2],
            "location": row[3] or "",
            "type": row[4],
            "student_count": row[5],
            "created_at": row[6].isoformat() if hasattr(row[6], "isoformat") else str(row[6]),
        }

    @staticmethod
    def _row_to_student(row) -> Dict:
        if not row:
            return {}
        return {
            "student_id": row[0],
            "university_id": row[1],
            "name": row[2],
            "email": row[3],
            "graduation_year": row[4],
            "status": row[5],
            "placement_status": row[6],
            "created_at": row[7].isoformat() if hasattr(row[7], "isoformat") else str(row[7]),
        }

    # ============================================================
    # REGISTER + ADD
    # ============================================================

    def register_university(self, data: Dict) -> Dict:
        """Register a university."""
        university_id = f"UNI-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_universities
                    (university_id, name, admin_email, location, type, student_count)
                VALUES (%s, %s, %s, %s, %s, 0)
            ''', (
                university_id,
                data.get("name"),
                data.get("admin_email"),
                data.get("location", ""),
                data.get("type", "University"),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"register_university failed: {e}")
            return {"status": "error", "message": "Could not register university"}

        return {
            "status": "success",
            "university_id": university_id,
            "message": "University registered!",
            "admin_portal": f"https://charvakit.com/university/{university_id}",
        }

    def add_student(self, data: Dict) -> Dict:
        """Add student under a university."""
        student_id = f"STU-{secrets.token_hex(4).upper()}"
        university_id = data.get("university_id")

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_university_students
                    (student_id, university_id, name, email, graduation_year, status, placement_status)
                VALUES (%s, %s, %s, %s, %s, 'enrolled', 'not_placed')
            ''', (
                student_id,
                university_id,
                data.get("name"),
                data.get("email"),
                int(data.get("graduation_year", 2026)),
            ))
            cur.execute('''
                UPDATE charvak_universities
                SET student_count = student_count + 1
                WHERE university_id = %s
            ''', (university_id,))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"add_student failed: {e}")
            return {"status": "error", "message": "Could not add student"}

        return {"status": "success", "student_id": student_id, "message": "Student added"}

    def record_outcome(self, data: Dict) -> Dict:
        """Record first-destination outcome."""
        outcome_id = f"OUT-{secrets.token_hex(4).upper()}"
        student_id = data.get("student_id")
        outcome_type = data.get("outcome_type", "employed")

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_university_outcomes
                    (outcome_id, student_id, outcome_type, company_name, salary, job_title, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                outcome_id,
                student_id,
                outcome_type,
                data.get("company_name", ""),
                float(data.get("salary", 0)),
                data.get("job_title", ""),
                data.get("location", ""),
            ))
            # Update student placement status
            new_status = "placed" if outcome_type == "employed" else outcome_type
            cur.execute('''
                UPDATE charvak_university_students
                SET placement_status = %s
                WHERE student_id = %s
            ''', (new_status, student_id))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"record_outcome failed: {e}")
            return {"status": "error", "message": "Could not record outcome"}

        return {"status": "success", "outcome_id": outcome_id, "message": "Outcome recorded"}

    # ============================================================
    # REPORTS
    # ============================================================

    def get_first_destination_report(self, university_id: str) -> Dict:
        """Generate first-destination outcome report."""
        uni = self._find_university(university_id)
        if not uni:
            return {"status": "error", "message": "University not found"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT COUNT(*) FROM charvak_university_students WHERE university_id = %s', (university_id,))
            total_students = int(cur.fetchone()[0] or 0)

            # Outcomes for this university's students
            cur.execute('''
                SELECT COUNT(*) FROM charvak_university_outcomes o
                WHERE o.student_id IN (
                    SELECT student_id FROM charvak_university_students WHERE university_id = %s
                )
            ''', (university_id,))
            outcomes_recorded = int(cur.fetchone()[0] or 0)

            # Employed count
            cur.execute('''
                SELECT COUNT(*) FROM charvak_university_outcomes o
                WHERE o.outcome_type = 'employed' AND o.student_id IN (
                    SELECT student_id FROM charvak_university_students WHERE university_id = %s
                )
            ''', (university_id,))
            employed_count = int(cur.fetchone()[0] or 0)

            # Average salary of employed (excluding 0 salary)
            cur.execute('''
                SELECT COALESCE(AVG(salary), 0) FROM charvak_university_outcomes o
                WHERE o.outcome_type = 'employed' AND o.salary > 0 AND o.student_id IN (
                    SELECT student_id FROM charvak_university_students WHERE university_id = %s
                )
            ''', (university_id,))
            avg_salary = float(cur.fetchone()[0] or 0)

            # Top companies
            cur.execute('''
                SELECT company_name, COUNT(*) FROM charvak_university_outcomes o
                WHERE o.outcome_type = 'employed' AND o.company_name != ''
                  AND o.student_id IN (
                    SELECT student_id FROM charvak_university_students WHERE university_id = %s
                  )
                GROUP BY company_name
                ORDER BY COUNT(*) DESC, company_name ASC
                LIMIT 5
            ''', (university_id,))
            top_companies = [{"company": r[0], "hires": r[1]} for r in cur.fetchall()]

            # Top locations
            cur.execute('''
                SELECT location, COUNT(*) FROM charvak_university_outcomes o
                WHERE o.outcome_type = 'employed' AND o.location != ''
                  AND o.student_id IN (
                    SELECT student_id FROM charvak_university_students WHERE university_id = %s
                  )
                GROUP BY location
                ORDER BY COUNT(*) DESC, location ASC
                LIMIT 5
            ''', (university_id,))
            top_locations = [{"location": r[0], "count": r[1]} for r in cur.fetchall()]

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_first_destination_report failed: {e}")
            return {"status": "error", "message": "Could not generate report"}

        employment_rate = round(employed_count / total_students * 100, 1) if total_students else 0

        return {
            "status": "success",
            "university": uni["name"],
            "report": {
                "total_students": total_students,
                "outcomes_recorded": outcomes_recorded,
                "employment_rate": employment_rate,
                "average_salary": round(avg_salary, 2) if avg_salary else 0,
                "top_companies": top_companies,
                "top_locations": top_locations,
            },
        }

    def get_university_dashboard(self, university_id: str) -> Dict:
        """Get university admin dashboard."""
        uni = self._find_university(university_id)
        if not uni:
            return {"status": "error", "message": "University not found"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT student_id, university_id, name, email, graduation_year,
                       status, placement_status, created_at
                FROM charvak_university_students
                WHERE university_id = %s
                ORDER BY created_at DESC
            ''', (university_id,))
            student_rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_university_dashboard failed: {e}")
            return {"status": "error", "message": "Could not load dashboard"}

        students = [self._row_to_student(r) for r in student_rows]

        report = None
        if students:
            report_response = self.get_first_destination_report(university_id)
            report = report_response.get("report")

        return {
            "status": "success",
            "university": uni,
            "students": students,
            "report": report,
        }

    def get_stats(self) -> Dict:
        """Get university engine statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM charvak_universities')
            total_universities = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_university_students')
            total_students = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_university_outcomes')
            total_outcomes = int(cur.fetchone()[0] or 0)

            cur.execute("SELECT COUNT(*) FROM charvak_university_outcomes WHERE outcome_type = 'employed'")
            employed = int(cur.fetchone()[0] or 0)
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        employment_rate = round(employed / total_outcomes * 100, 1) if total_outcomes else 0

        return {
            "status": "success",
            "stats": {
                "total_universities": total_universities,
                "total_students": total_students,
                "total_outcomes": total_outcomes,
                "employment_rate": employment_rate,
            },
        }

    # ============================================================
    # HELPERS
    # ============================================================

    def _get_top_companies(self, outcomes: List[Dict], limit: int = 5) -> List[Dict]:
        """(Preserved for API compatibility - used by legacy callers.)"""
        company_counts = {}
        for o in outcomes:
            if o["company_name"]:
                company_counts[o["company_name"]] = company_counts.get(o["company_name"], 0) + 1
        sorted_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"company": c, "hires": n} for c, n in sorted_companies[:limit]]

    def _get_top_locations(self, outcomes: List[Dict], limit: int = 5) -> List[Dict]:
        """(Preserved for API compatibility - used by legacy callers.)"""
        location_counts = {}
        for o in outcomes:
            if o["location"]:
                location_counts[o["location"]] = location_counts.get(o["location"], 0) + 1
        sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"location": l, "count": n} for l, n in sorted_locations[:limit]]

    def _find_university(self, university_id: str) -> Optional[Dict]:
        if not university_id:
            return None
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT university_id, name, admin_email, location, type,
                       student_count, created_at
                FROM charvak_universities WHERE university_id = %s
            ''', (university_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
            return self._row_to_university(row) if row else None
        except Exception as e:
            logger.error(f"_find_university failed: {e}")
            return None


university_engine = UniversityEngine()