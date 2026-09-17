"""
Charvak Career Engine V2
Global job board features: alerts, saved jobs, salary insights,
interview scheduling, recommendations, company follow, offers, withdrawal
(DB-backed - Session C/2)
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.careerv2")


class CareerV2Engine:
    """Advanced career features (Postgres-backed)."""

    def __init__(self):
        self._ensure_tables()
        logger.info("Career V2 Engine ready (DB-backed) - 6 modules")

    def _ensure_tables(self):
        """Idempotent table creation for Career V2 tables."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_career_job_alerts (
                    alert_id     TEXT PRIMARY KEY,
                    email        TEXT NOT NULL,
                    keywords     JSONB DEFAULT '[]'::jsonb,
                    location     TEXT DEFAULT '',
                    frequency    TEXT DEFAULT 'daily',
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_career_alerts_email ON charvak_career_job_alerts(email)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_career_saved_jobs (
                    save_id      TEXT PRIMARY KEY,
                    email        TEXT NOT NULL,
                    job_id       TEXT NOT NULL,
                    saved_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(email, job_id)
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_career_saved_email ON charvak_career_saved_jobs(email)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_career_company_follows (
                    follow_id    TEXT PRIMARY KEY,
                    email        TEXT NOT NULL,
                    company      TEXT NOT NULL,
                    followed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(email, company)
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_career_follows_email ON charvak_career_company_follows(email)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_career_salary_reports (
                    salary_id    TEXT PRIMARY KEY,
                    role         TEXT NOT NULL,
                    company      TEXT DEFAULT 'Anonymous',
                    amount       NUMERIC(12,2) DEFAULT 0,
                    location     TEXT DEFAULT '',
                    recorded_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_career_salary_role ON charvak_career_salary_reports(role)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_career_interviews (
                    interview_id      TEXT PRIMARY KEY,
                    candidate_email   TEXT NOT NULL,
                    employer          TEXT,
                    role              TEXT,
                    date              TEXT,
                    platform          TEXT DEFAULT 'Zoom',
                    status            TEXT DEFAULT 'scheduled',
                    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_career_interviews_email ON charvak_career_interviews(candidate_email)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_career_offers (
                    offer_id          TEXT PRIMARY KEY,
                    candidate_email   TEXT NOT NULL,
                    company           TEXT,
                    role              TEXT,
                    salary            NUMERIC(12,2) DEFAULT 0,
                    status            TEXT DEFAULT 'received',
                    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_career_offers_email ON charvak_career_offers(candidate_email)''')

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"career_v2 tables init failed: {e}")

    # ============================================================
    # 1. JOB ALERTS
    # ============================================================
    def create_job_alert(self, data: Dict) -> Dict:
        alert_id = f"ALERT-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_career_job_alerts
                    (alert_id, email, keywords, location, frequency)
                VALUES (%s, %s, %s::jsonb, %s, %s)
            ''', (
                alert_id,
                data.get("email"),
                json.dumps(data.get("keywords", [])),
                data.get("location", ""),
                data.get("frequency", "daily"),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_job_alert failed: {e}")
            return {"status": "error", "message": "Could not create job alert"}
        return {"status": "success", "alert_id": alert_id, "message": "Job alert created!"}

    def get_alerts(self, email: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT alert_id, email, keywords, location, frequency, created_at
                FROM charvak_career_job_alerts
                WHERE email = %s
                ORDER BY created_at DESC
            ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_alerts failed: {e}")
            return {"status": "error", "message": "Could not load alerts"}

        alerts = []
        for r in rows:
            alerts.append({
                "alert_id": r[0],
                "email": r[1],
                "keywords": r[2] if isinstance(r[2], list) else (json.loads(r[2]) if r[2] else []),
                "location": r[3] or "",
                "frequency": r[4],
                "created_at": r[5].isoformat() if hasattr(r[5], "isoformat") else str(r[5]),
            })
        return {"status": "success", "alerts": alerts, "count": len(alerts)}

    # ============================================================
    # 2. SAVED JOBS
    # ============================================================
    def save_job(self, data: Dict) -> Dict:
        save_id = f"SAVE-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_career_saved_jobs (save_id, email, job_id)
                VALUES (%s, %s, %s)
            ''', (save_id, data.get("email"), data.get("job_id")))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            msg = str(e).lower()
            if "unique" in msg or "duplicate" in msg:
                return {"status": "error", "message": "Job already saved"}
            logger.error(f"save_job failed: {e}")
            return {"status": "error", "message": "Could not save job"}
        return {"status": "success", "save_id": save_id, "message": "Job saved!"}

    def get_saved_jobs(self, email: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT save_id, email, job_id, saved_at
                FROM charvak_career_saved_jobs
                WHERE email = %s
                ORDER BY saved_at DESC
            ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_saved_jobs failed: {e}")
            return {"status": "error", "message": "Could not load saved jobs"}

        saved = [{
            "save_id": r[0], "email": r[1], "job_id": r[2],
            "saved_at": r[3].isoformat() if hasattr(r[3], "isoformat") else str(r[3]),
        } for r in rows]
        return {"status": "success", "saved_jobs": saved, "count": len(saved)}

    # ============================================================
    # 3. COMPANY FOLLOW
    # ============================================================
    def follow_company(self, data: Dict) -> Dict:
        follow_id = f"FOLLOW-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_career_company_follows (follow_id, email, company)
                VALUES (%s, %s, %s)
            ''', (follow_id, data.get("email"), data.get("company")))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            msg = str(e).lower()
            if "unique" in msg or "duplicate" in msg:
                return {"status": "error", "message": f"Already following {data.get('company')}"}
            logger.error(f"follow_company failed: {e}")
            return {"status": "error", "message": "Could not follow company"}
        return {"status": "success", "message": f"Following {data.get('company')}!"}

    # ============================================================
    # 4. SALARY INSIGHTS
    # ============================================================
    def add_salary(self, data: Dict) -> Dict:
        salary_id = f"SAL-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_career_salary_reports
                    (salary_id, role, company, amount, location)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                salary_id,
                data.get("role"),
                data.get("company", "Anonymous"),
                float(data.get("amount", 0)),
                data.get("location", ""),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"add_salary failed: {e}")
            return {"status": "error", "message": "Could not add salary"}
        return {"status": "success", "message": "Salary added anonymously"}

    def get_salary_insights(self, role: str = None) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            if role:
                cur.execute('''
                    SELECT COUNT(*) FROM charvak_career_salary_reports
                    WHERE LOWER(role) LIKE %s
                ''', (f"%{role.lower()}%",))
                count = cur.fetchone()[0]

                cur.execute('''
                    SELECT COALESCE(AVG(amount),0), COALESCE(MIN(amount),0), COALESCE(MAX(amount),0)
                    FROM charvak_career_salary_reports
                    WHERE amount > 0 AND LOWER(role) LIKE %s
                ''', (f"%{role.lower()}%",))
                avg, mn, mx = cur.fetchone()
            else:
                cur.execute('SELECT COUNT(*) FROM charvak_career_salary_reports')
                count = cur.fetchone()[0]
                cur.execute('''
                    SELECT COALESCE(AVG(amount),0), COALESCE(MIN(amount),0), COALESCE(MAX(amount),0)
                    FROM charvak_career_salary_reports
                    WHERE amount > 0
                ''')
                avg, mn, mx = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_salary_insights failed: {e}")
            return {"status": "error", "message": "Could not load salary insights"}

        return {
            "status": "success",
            "count": count,
            "average": round(float(avg), 2) if avg else 0,
            "min": float(mn) if mn else 0,
            "max": float(mx) if mx else 0,
        }

    # ============================================================
    # 5. INTERVIEW SCHEDULING
    # ============================================================
    def schedule_interview(self, data: Dict) -> Dict:
        interview_id = f"INT-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_career_interviews
                    (interview_id, candidate_email, employer, role, date, platform, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'scheduled')
            ''', (
                interview_id,
                data.get("candidate_email"),
                data.get("employer"),
                data.get("role"),
                data.get("date"),
                data.get("platform", "Zoom"),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"schedule_interview failed: {e}")
            return {"status": "error", "message": "Could not schedule interview"}
        return {"status": "success", "interview_id": interview_id, "message": "Interview scheduled!"}

    def get_interviews(self, email: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT interview_id, candidate_email, employer, role, date, platform, status
                FROM charvak_career_interviews
                WHERE candidate_email = %s
                ORDER BY created_at DESC
            ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_interviews failed: {e}")
            return {"status": "error", "message": "Could not load interviews"}

        interviews = [{
            "interview_id": r[0], "candidate_email": r[1], "employer": r[2],
            "role": r[3], "date": r[4], "platform": r[5], "status": r[6],
        } for r in rows]
        return {"status": "success", "interviews": interviews, "count": len(interviews)}

    # ============================================================
    # 6. OFFER MANAGEMENT
    # ============================================================
    def add_offer(self, data: Dict) -> Dict:
        offer_id = f"OFFER-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_career_offers
                    (offer_id, candidate_email, company, role, salary, status)
                VALUES (%s, %s, %s, %s, %s, 'received')
            ''', (
                offer_id,
                data.get("candidate_email"),
                data.get("company"),
                data.get("role"),
                float(data.get("salary", 0)),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"add_offer failed: {e}")
            return {"status": "error", "message": "Could not add offer"}
        return {"status": "success", "offer_id": offer_id, "message": "Offer added!"}

    def get_offers(self, email: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT offer_id, candidate_email, company, role, salary, status
                FROM charvak_career_offers
                WHERE candidate_email = %s
                ORDER BY created_at DESC
            ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_offers failed: {e}")
            return {"status": "error", "message": "Could not load offers"}

        offers = [{
            "offer_id": r[0], "candidate_email": r[1], "company": r[2],
            "role": r[3], "salary": float(r[4]) if r[4] is not None else 0, "status": r[5],
        } for r in rows]
        return {"status": "success", "offers": offers, "count": len(offers)}

    # ============================================================
    # 7. WITHDRAW APPLICATION (delegates to job_board_engine - untouched)
    # ============================================================
    def withdraw_application(self, application_id: str) -> Dict:
        from job_board_engine import job_board_engine
        for app in job_board_engine.applications:
            if app["application_id"] == application_id:
                app["status"] = "withdrawn"
                return {"status": "success", "message": "Application withdrawn"}
        return {"status": "error", "message": "Application not found"}

    # ============================================================
    # 8. JOB RECOMMENDATIONS (delegates to job_board_engine - untouched)
    # ============================================================
    def get_job_recommendations(self, email: str, skills: List[str] = None) -> Dict:
        from job_board_engine import job_board_engine
        jobs = job_board_engine.get_jobs()
        recommendations = jobs[:5] if jobs else [
            {"title": "Python Developer", "match": 95},
            {"title": "React Developer", "match": 88},
            {"title": "DevOps Engineer", "match": 82},
        ]
        return {"status": "success", "recommendations": recommendations, "count": len(recommendations)}

    # ============================================================
    # 9. STATS
    # ============================================================
    def get_stats(self) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            stats = {}
            for key, table in [
                ("job_alerts", "charvak_career_job_alerts"),
                ("saved_jobs", "charvak_career_saved_jobs"),
                ("followed_companies", "charvak_career_company_follows"),
                ("salary_records", "charvak_career_salary_reports"),
                ("interviews", "charvak_career_interviews"),
                ("offers", "charvak_career_offers"),
            ]:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                stats[key] = cur.fetchone()[0]
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}
        return {"status": "success", "stats": stats}


career_v2_engine = CareerV2Engine()