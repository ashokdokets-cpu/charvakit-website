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

    def subscribe_university(self, data: Dict) -> Dict:
        """
        Record a university subscription after credits are charged by the route.
        data = {"university_id", "admin_email", "tier", "credits_used"}
        """
        from datetime import datetime, timedelta
        university_id = (data.get("university_id") or "").strip()
        admin_email = (data.get("admin_email") or "").strip().lower()
        tier = (data.get("tier") or "").strip().lower()
        credits_used = int(data.get("credits_used") or 0)

        if not university_id or not admin_email or not tier:
            return {"status": "error", "message": "university_id, admin_email, tier required"}

        tier_prices = {
            "starter": 19999,
            "growth": 49999,
            "enterprise": 99999,
        }
        if tier not in tier_prices:
            return {"status": "error", "message": f"Unknown tier: {tier}"}

        price_inr = tier_prices[tier]
        started_at = datetime.now()
        expires_at = started_at + timedelta(days=365)

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_university_subscriptions (
                    university_id   TEXT PRIMARY KEY,
                    admin_email     TEXT NOT NULL,
                    tier            TEXT NOT NULL,
                    price_inr       INTEGER,
                    credits_used    INTEGER NOT NULL DEFAULT 0,
                    started_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at      TIMESTAMP NOT NULL,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                INSERT INTO charvak_university_subscriptions
                    (university_id, admin_email, tier, price_inr, credits_used, started_at, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (university_id) DO UPDATE SET
                    admin_email = EXCLUDED.admin_email,
                    tier = EXCLUDED.tier,
                    price_inr = EXCLUDED.price_inr,
                    credits_used = EXCLUDED.credits_used,
                    started_at = EXCLUDED.started_at,
                    expires_at = EXCLUDED.expires_at
            """, (university_id, admin_email, tier, price_inr, credits_used, started_at, expires_at))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"subscribe_university persist failed: {e}")
            return {"status": "error", "message": "Subscription could not be saved"}

        return {
            "status": "success",
            "university_id": university_id,
            "tier": tier,
            "price_inr": price_inr,
            "credits_used": credits_used,
            "started_at": started_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "days_remaining": 365,
            "message": f"{tier.title()} plan active. 365 days of portal access.",
        }

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



    # ==========================================================================
    # Session 81 — Proof Dashboard methods (added 2026-10-24)
    # ==========================================================================

    def record_cert_view(self, certificate_id: str, viewer_info: Dict) -> Dict:
        """Record a view of a readiness certificate. Idempotent per (cert, ip, 5-min)."""
        from database import db
        import hashlib
        import secrets

        viewer_ip = (viewer_info.get("ip") or "").strip()
        ip_hash = hashlib.sha256(viewer_ip.encode()).hexdigest()[:32] if viewer_ip else None

        viewer_type = (viewer_info.get("viewer_type") or "anonymous").strip().lower()
        if viewer_type not in ("anonymous", "employer", "dean", "admin"):
            viewer_type = "anonymous"

        viewer_email = (viewer_info.get("viewer_email") or "").strip().lower() or None
        user_agent = (viewer_info.get("user_agent") or "")[:500]
        referrer = (viewer_info.get("referrer") or "")[:500]

        university_id = None
        try:
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT c.email, us.university_id
                FROM charvak_readiness_certificates c
                LEFT JOIN charvak_university_students us
                  ON LOWER(us.email) = LOWER(c.email)
                WHERE c.certificate_id = %s
                LIMIT 1
            """, (certificate_id,))
            row = cur.fetchone()
            if row:
                university_id = row[1]
            cur.close()
            conn.close()
        except Exception as e:
            logger.debug(f"record_cert_view cert lookup failed: {e}")

        try:
            conn = db.get_connection()
            cur = conn.cursor()
            if ip_hash:
                cur.execute("""
                    SELECT view_id FROM charvak_certificate_views
                    WHERE certificate_id = %s AND viewer_ip_hash = %s
                      AND viewed_at > NOW() - INTERVAL '5 minutes'
                    LIMIT 1
                """, (certificate_id, ip_hash))
                if cur.fetchone():
                    cur.close()
                    conn.close()
                    return {"status": "deduplicated"}

            view_id = f"CV-{secrets.token_hex(6).upper()}"
            cur.execute("""
                INSERT INTO charvak_certificate_views
                (view_id, certificate_id, viewer_ip_hash, viewer_type,
                 viewer_email, user_agent, referrer, university_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (view_id, certificate_id, ip_hash, viewer_type,
                  viewer_email, user_agent, referrer, university_id))
            conn.commit()
            cur.close()
            conn.close()
            return {"status": "success", "view_id": view_id}
        except Exception as e:
            logger.warning(f"record_cert_view insert failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_proof_dashboard(self, university_id: str) -> Dict:
        """Comprehensive proof dashboard for a university."""
        from database import db
        uni = self._find_university(university_id)
        if not uni:
            return {"status": "error", "message": "University not found"}

        try:
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT COUNT(*) FROM charvak_university_students
                WHERE university_id = %s
            """, (university_id,))
            cohort_size = cur.fetchone()[0] or 0

            cur.execute("""
                SELECT email FROM charvak_university_students
                WHERE university_id = %s AND email IS NOT NULL
            """, (university_id,))
            cohort_emails = [r[0].lower() for r in cur.fetchall() if r[0]]

            certs = []
            if cohort_emails:
                placeholders = ",".join(["%s"] * len(cohort_emails))
                cur.execute(
                    "SELECT certificate_id, email, display_name, role, "
                    "readiness_score, created_at, payload_json "
                    "FROM charvak_readiness_certificates "
                    "WHERE LOWER(email) IN (" + placeholders + ") "
                    "ORDER BY created_at DESC",
                    cohort_emails
                )
                certs = cur.fetchall()

            certified_count = len(certs)
            cert_rate = round(certified_count * 100.0 / cohort_size, 1) if cohort_size else 0.0

            scores = [c[4] for c in certs if c[4] is not None]
            avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
            median_score = sorted(scores)[len(scores)//2] if scores else 0
            top_quartile = sorted(scores)[int(len(scores) * 0.75)] if scores else 0

            dept_map = {}
            for c in certs:
                role = c[3] or "Unknown"
                if role not in dept_map:
                    dept_map[role] = {"count": 0, "total_score": 0}
                dept_map[role]["count"] += 1
                dept_map[role]["total_score"] += c[4] or 0

            dept_breakdown = []
            for role, data in dept_map.items():
                dept_breakdown.append({
                    "department": role,
                    "students": data["count"],
                    "avg_score": round(data["total_score"] / data["count"], 1) if data["count"] else 0
                })
            dept_breakdown.sort(key=lambda x: x["avg_score"], reverse=True)

            trend = []
            if cohort_emails:
                cur.execute(
                    "SELECT TO_CHAR(created_at, 'YYYY-MM') AS month, "
                    "COUNT(*) AS certs, ROUND(AVG(readiness_score)::numeric, 1) AS avg_score "
                    "FROM charvak_readiness_certificates "
                    "WHERE LOWER(email) IN (" + placeholders + ") "
                    "AND created_at > NOW() - INTERVAL '90 days' "
                    "GROUP BY 1 ORDER BY 1",
                    cohort_emails
                )
                trend = [{"month": r[0], "certs": r[1], "avg_score": float(r[2]) if r[2] else 0}
                         for r in cur.fetchall()]

            top_students = []
            for c in certs[:10]:
                top_students.append({
                    "certificate_id": c[0],
                    "email": c[1],
                    "name": c[2] or "Anonymous",
                    "role": c[3],
                    "score": c[4],
                    "date": c[5].isoformat() if c[5] else None
                })

            cur.execute("""
                SELECT
                    COUNT(*) AS total_views,
                    COUNT(DISTINCT viewer_ip_hash) AS unique_viewers,
                    COUNT(DISTINCT certificate_id) AS unique_certs_viewed,
                    COUNT(*) FILTER (WHERE viewer_type = 'employer') AS employer_views,
                    COUNT(*) FILTER (WHERE viewer_type = 'dean') AS dean_views
                FROM charvak_certificate_views
                WHERE university_id = %s
            """, (university_id,))
            vrow = cur.fetchone()
            cert_views = {
                "total_views": vrow[0] or 0,
                "unique_viewers": vrow[1] or 0,
                "unique_certs_viewed": vrow[2] or 0,
                "employer_views": vrow[3] or 0,
                "dean_views": vrow[4] or 0,
                "view_rate_pct": round((vrow[2] or 0) * 100.0 / certified_count, 1) if certified_count else 0.0
            }

            cur.execute("""
                WITH peer_avgs AS (
                    SELECT us.university_id, AVG(c.readiness_score) AS avg_score
                    FROM charvak_university_students us
                    JOIN charvak_readiness_certificates c
                      ON LOWER(c.email) = LOWER(us.email)
                    WHERE us.university_id != %s
                    GROUP BY us.university_id
                )
                SELECT AVG(avg_score), COUNT(*) FROM peer_avgs
            """, (university_id,))
            peer_row = cur.fetchone()
            peer_avg = round(float(peer_row[0]), 1) if peer_row[0] else 0.0
            peer_count = peer_row[1] or 0

            peer_percentile = 50
            if avg_score and peer_avg and peer_avg > 0:
                peer_percentile = min(99, int((avg_score / peer_avg) * 50))

            cur.close()
            conn.close()

            from datetime import datetime as _dt
            return {
                "status": "success",
                "university": {
                    "university_id": uni.get("university_id"),
                    "name": uni.get("name"),
                    "location": uni.get("location"),
                    "type": uni.get("type"),
                },
                "cohort": {
                    "total_students": cohort_size,
                    "certified_students": certified_count,
                    "cert_rate_pct": cert_rate,
                },
                "readiness": {
                    "avg_score": avg_score,
                    "median_score": median_score,
                    "top_quartile": top_quartile,
                },
                "departments": dept_breakdown,
                "trend_90d": trend,
                "top_students": top_students,
                "certificate_views": cert_views,
                "peer_benchmark": {
                    "peer_avg_score": peer_avg,
                    "peer_institution_count": peer_count,
                    "percentile": peer_percentile,
                },
                "generated_at": _dt.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"get_proof_dashboard failed: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

university_engine = UniversityEngine()