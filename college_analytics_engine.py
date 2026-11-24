"""
College Admin Analytics Engine - Session 123 Option B
Aggregates placement pipeline data for college dashboards.
"""
import logging
from datetime import datetime, timedelta, timezone
from database import db

logger = logging.getLogger("charvakit.college_analytics")


class CollegeAnalyticsEngine:
    def get_overview(self, college_slug: str) -> dict:
        """Top-level KPI cards."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            # Total students
            cur.execute("SELECT COUNT(*) FROM charvak_students WHERE college_slug = %s", (college_slug,))
            total_students = cur.fetchone()[0]

            # Total jobs saved by this college's students
            cur.execute("""
                SELECT COUNT(*) FROM charvak_saved_jobs sj
                JOIN charvak_students s ON s.student_id = sj.student_id
                WHERE s.college_slug = %s
            """, (college_slug,))
            total_saved = cur.fetchone()[0]

            # Applications submitted
            cur.execute("""
                SELECT COUNT(*) FROM charvak_saved_jobs sj
                JOIN charvak_students s ON s.student_id = sj.student_id
                WHERE s.college_slug = %s AND sj.status IN ('applied','interviewing','offer','rejected')
            """, (college_slug,))
            total_applied = cur.fetchone()[0]

            # Interviews
            cur.execute("""
                SELECT COUNT(*) FROM charvak_saved_jobs sj
                JOIN charvak_students s ON s.student_id = sj.student_id
                WHERE s.college_slug = %s AND sj.status IN ('interviewing','offer')
            """, (college_slug,))
            total_interviews = cur.fetchone()[0]

            # Offers
            cur.execute("""
                SELECT COUNT(*) FROM charvak_saved_jobs sj
                JOIN charvak_students s ON s.student_id = sj.student_id
                WHERE s.college_slug = %s AND sj.status = 'offer'
            """, (college_slug,))
            total_offers = cur.fetchone()[0]

            placement_rate = round((total_offers / total_students * 100), 1) if total_students > 0 else 0
            application_rate = round((total_applied / total_students * 100), 1) if total_students > 0 else 0

            return {
                "total_students": total_students,
                "total_saved": total_saved,
                "total_applied": total_applied,
                "total_interviews": total_interviews,
                "total_offers": total_offers,
                "placement_rate": placement_rate,
                "application_rate": application_rate,
            }
        finally:
            cur.close()
            conn.close()

    def get_status_breakdown(self, college_slug: str) -> dict:
        """Counts per status stage."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT sj.status, COUNT(*) FROM charvak_saved_jobs sj
                JOIN charvak_students s ON s.student_id = sj.student_id
                WHERE s.college_slug = %s
                GROUP BY sj.status
            """, (college_slug,))
            counts = {r[0]: r[1] for r in cur.fetchall()}
            return {
                "saved": counts.get("saved", 0),
                "applied": counts.get("applied", 0),
                "interviewing": counts.get("interviewing", 0),
                "offer": counts.get("offer", 0),
                "rejected": counts.get("rejected", 0),
            }
        finally:
            cur.close()
            conn.close()

    def get_top_companies(self, college_slug: str, limit: int = 10) -> list:
        """Top companies by applications."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT j.company, COUNT(*) AS cnt
                FROM charvak_saved_jobs sj
                JOIN charvak_students s ON s.student_id = sj.student_id
                JOIN charvak_jobs j ON j.job_id = sj.job_id
                WHERE s.college_slug = %s AND sj.status != 'saved'
                GROUP BY j.company
                ORDER BY cnt DESC
                LIMIT %s
            """, (college_slug, limit))
            return [{"company": r[0], "count": r[1]} for r in cur.fetchall()]
        finally:
            cur.close()
            conn.close()

    def get_top_roles(self, college_slug: str, limit: int = 10) -> list:
        """Top roles by applications."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT j.role_category, COUNT(*) AS cnt
                FROM charvak_saved_jobs sj
                JOIN charvak_students s ON s.student_id = sj.student_id
                JOIN charvak_jobs j ON j.job_id = sj.job_id
                WHERE s.college_slug = %s AND sj.status != 'saved'
                GROUP BY j.role_category
                ORDER BY cnt DESC
                LIMIT %s
            """, (college_slug, limit))
            return [{"category": r[0] or "uncategorized", "count": r[1]} for r in cur.fetchall()]
        finally:
            cur.close()
            conn.close()

    def get_activity_trend(self, college_slug: str, days: int = 14) -> list:
        """Applications per day for last N days."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT DATE(sj.applied_at) AS day, COUNT(*) AS cnt
                FROM charvak_saved_jobs sj
                JOIN charvak_students s ON s.student_id = sj.student_id
                WHERE s.college_slug = %s
                  AND sj.applied_at IS NOT NULL
                  AND sj.applied_at >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(sj.applied_at)
                ORDER BY day
            """, (college_slug, days))
            return [{"day": str(r[0]), "count": r[1]} for r in cur.fetchall()]
        finally:
            cur.close()
            conn.close()

    def get_top_students(self, college_slug: str, limit: int = 10) -> list:
        """Top performing students — those with the most interviews/offers."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT s.name, s.email,
                       COUNT(CASE WHEN sj.status IN ('interviewing','offer') THEN 1 END) as interviews,
                       COUNT(CASE WHEN sj.status = 'offer' THEN 1 END) as offers,
                       COUNT(CASE WHEN sj.status != 'saved' THEN 1 END) as applications
                FROM charvak_students s
                LEFT JOIN charvak_saved_jobs sj ON sj.student_id = s.student_id
                WHERE s.college_slug = %s
                GROUP BY s.student_id, s.name, s.email
                HAVING COUNT(sj.save_id) > 0
                ORDER BY interviews DESC, offers DESC, applications DESC
                LIMIT %s
            """, (college_slug, limit))
            return [
                {
                    "name": r[0] or "Anonymous",
                    "email_masked": (r[1][:3] + "***") if r[1] else "***",
                    "interviews": r[2],
                    "offers": r[3],
                    "applications": r[4],
                }
                for r in cur.fetchall()
            ]
        finally:
            cur.close()
            conn.close()

    def get_full_dashboard(self, college_slug: str) -> dict:
        """All analytics in one call."""
        return {
            "overview": self.get_overview(college_slug),
            "status_breakdown": self.get_status_breakdown(college_slug),
            "top_companies": self.get_top_companies(college_slug),
            "top_categories": self.get_top_roles(college_slug),
            "activity_trend": self.get_activity_trend(college_slug),
            "top_students": self.get_top_students(college_slug),
        }


college_analytics = CollegeAnalyticsEngine()