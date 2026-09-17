"""
Charvak Training Engine
Course posting, enrollment, classroom management
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets
import json

logger = logging.getLogger("charvakit.training")


class CourseStatus:
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TrainingEngine:
    """Handles course management and enrollment."""
    
    def __init__(self):
        self._ensure_tables()
        logger.info("Training Engine ready (DB-backed)")

    def _ensure_tables(self):
        """Idempotent table creation for training tables."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_training_courses (
                    course_id         TEXT PRIMARY KEY,
                    course_name       TEXT NOT NULL,
                    trainer_name      TEXT,
                    trainer_email     TEXT NOT NULL,
                    category          TEXT DEFAULT 'Programming',
                    duration_weeks    INTEGER DEFAULT 4,
                    price_inr         NUMERIC(10,2) NOT NULL DEFAULT 0,
                    platform_fee      NUMERIC(10,2) DEFAULT 0,
                    trainer_payout    NUMERIC(10,2) DEFAULT 0,
                    description       TEXT DEFAULT '',
                    skills            JSONB DEFAULT '[]'::jsonb,
                    schedule          TEXT DEFAULT 'Flexible',
                    status            TEXT DEFAULT 'published',
                    enrolled_count    INTEGER DEFAULT 0,
                    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_training_enrollments (
                    enrollment_id     TEXT PRIMARY KEY,
                    course_id         TEXT NOT NULL,
                    student_name      TEXT,
                    student_email     TEXT NOT NULL,
                    payment_status    TEXT DEFAULT 'pending',
                    payment_id        TEXT,
                    progress_percent  INTEGER DEFAULT 0,
                    enrolled_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at      TIMESTAMP
                )
            ''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"training tables init failed: {e}")

    def _row_to_course(self, r):
        """Convert DB row to course dict."""
        if not r:
            return None
        return {
            "course_id": r[0], "course_name": r[1],
            "trainer_name": r[2] or "", "trainer_email": r[3],
            "category": r[4] or "Programming",
            "duration_weeks": r[5] or 4,
            "price_inr": float(r[6] or 0),
            "platform_fee": float(r[7] or 0),
            "trainer_payout": float(r[8] or 0),
            "description": r[9] or "",
            "skills": r[10] if isinstance(r[10], list) else json.loads(r[10] or "[]"),
            "schedule": r[11] or "Flexible",
            "status": r[12] or "published",
            "enrolled_count": r[13] or 0,
            "created_at": r[14].isoformat() if r[14] else None,
        }

    def _row_to_enrollment(self, r):
        """Convert DB row to enrollment dict."""
        if not r:
            return None
        return {
            "enrollment_id": r[0], "course_id": r[1],
            "student_name": r[2] or "", "student_email": r[3],
            "payment_status": r[4] or "pending",
            "payment_id": r[5],
            "progress_percent": r[6] or 0,
            "enrolled_at": r[7].isoformat() if r[7] else None,
            "completed_at": r[8].isoformat() if r[8] else None,
        }


    def post_course(self, data: Dict) -> Dict:
        """Post a new course (trainer-created)."""
        course_id = f"CRS-{secrets.token_hex(4).upper()}"
        price = float(data.get("price_inr", 0))
        platform_fee = round(price * 0.20, 2)
        trainer_payout = round(price * 0.80, 2)
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_training_courses
                    (course_id, course_name, trainer_name, trainer_email,
                     category, duration_weeks, price_inr, platform_fee,
                     trainer_payout, description, skills, schedule, status,
                     enrolled_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb,
                        %s, 'published', 0)
            ''', (course_id, data.get("course_name"), data.get("trainer_name"),
                  data.get("trainer_email"),
                  data.get("category", "Programming"),
                  int(data.get("duration_weeks", 4)), price, platform_fee,
                  trainer_payout, data.get("description", ""),
                  json.dumps(data.get("skills", [])),
                  data.get("schedule", "Flexible")))
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"Course posted: {course_id} - {data.get('course_name')}")
            return {
                "status": "success",
                "course_id": course_id,
                "message": "Course published! Students can now enroll.",
                "revenue_split": {
                    "trainer_gets": f"80% (INR {trainer_payout})",
                    "platform_gets": f"20% (INR {platform_fee})",
                },
            }
        except Exception as e:
            logger.error(f"post_course failed: {e}")
            return {"status": "error", "message": str(e)}


    def enroll_student(self, data: Dict) -> Dict:
        """Enroll a student in a course."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            # Confirm course exists
            cur.execute("SELECT course_name FROM charvak_training_courses WHERE course_id = %s", (data.get("course_id"),))
            course_row = cur.fetchone()
            if not course_row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Course not found"}
            course_name = course_row[0]
            enrollment_id = f"ENR-{secrets.token_hex(4).upper()}"
            payment_status = "completed" if data.get("payment_id") else "pending"
            cur.execute('''
                INSERT INTO charvak_training_enrollments
                    (enrollment_id, course_id, student_name, student_email,
                     payment_status, payment_id, progress_percent)
                VALUES (%s, %s, %s, %s, %s, %s, 0)
            ''', (enrollment_id, data.get("course_id"),
                  data.get("student_name"), data.get("student_email"),
                  payment_status, data.get("payment_id")))
            cur.execute('''
                UPDATE charvak_training_courses
                SET enrolled_count = enrolled_count + 1
                WHERE course_id = %s
            ''', (data.get("course_id"),))
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"Enrollment: {enrollment_id} - {data.get('student_name')} -> {course_name}")
            return {
                "status": "success",
                "enrollment_id": enrollment_id,
                "message": f"Enrolled in {course_name}!",
                "classroom_link": f"/online-classroom?enrollment={enrollment_id}",
            }
        except Exception as e:
            logger.error(f"enroll_student failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_courses(self, category: str = None) -> Dict:
        """Get all published courses."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            if category:
                cur.execute('''
                    SELECT course_id, course_name, trainer_name, trainer_email,
                           category, duration_weeks, price_inr, platform_fee,
                           trainer_payout, description, skills, schedule, status,
                           enrolled_count, created_at
                    FROM charvak_training_courses
                    WHERE status = 'published' AND category = %s
                    ORDER BY created_at DESC
                ''', (category,))
            else:
                cur.execute('''
                    SELECT course_id, course_name, trainer_name, trainer_email,
                           category, duration_weeks, price_inr, platform_fee,
                           trainer_payout, description, skills, schedule, status,
                           enrolled_count, created_at
                    FROM charvak_training_courses
                    WHERE status = 'published'
                    ORDER BY created_at DESC
                ''')
            rows = cur.fetchall()
            courses = [self._row_to_course(r) for r in rows]
            # distinct categories
            cur.execute("SELECT DISTINCT category FROM charvak_training_courses WHERE status = 'published'")
            categories = [r[0] for r in cur.fetchall() if r[0]]
            cur.close(); conn.close()
            return {
                "status": "success",
                "courses": courses,
                "count": len(courses),
                "categories": categories,
                "total_enrolled": sum(c["enrolled_count"] for c in courses),
            }
        except Exception as e:
            logger.error(f"get_courses failed: {e}")
            return {"status": "error", "message": str(e), "courses": [], "count": 0}


    def get_course(self, course_id: str) -> Dict:
        """Get course details."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT course_id, course_name, trainer_name, trainer_email,
                       category, duration_weeks, price_inr, platform_fee,
                       trainer_payout, description, skills, schedule, status,
                       enrolled_count, created_at
                FROM charvak_training_courses WHERE course_id = %s
            ''', (course_id,))
            r = cur.fetchone()
            cur.close(); conn.close()
            if not r:
                return {"status": "error", "message": "Course not found"}
            return {"status": "success", "course": self._row_to_course(r)}
        except Exception as e:
            logger.error(f"get_course failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_trainer_dashboard(self, trainer_email: str) -> Dict:
        """Get trainer's courses and revenue."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT course_id, course_name, trainer_name, trainer_email,
                       category, duration_weeks, price_inr, platform_fee,
                       trainer_payout, description, skills, schedule, status,
                       enrolled_count, created_at
                FROM charvak_training_courses
                WHERE trainer_email = %s
                ORDER BY created_at DESC
            ''', (trainer_email,))
            rows = cur.fetchall()
            courses = [self._row_to_course(r) for r in rows]
            total_students = sum(c["enrolled_count"] for c in courses)
            total_revenue = sum(c["enrolled_count"] * c["trainer_payout"] for c in courses)
            cur.close(); conn.close()
            return {
                "status": "success",
                "trainer_email": trainer_email,
                "courses": courses,
                "stats": {
                    "total_courses": len(courses),
                    "total_students": total_students,
                    "total_revenue_inr": round(total_revenue, 2),
                },
            }
        except Exception as e:
            logger.error(f"get_trainer_dashboard failed: {e}")
            return {"status": "error", "message": str(e), "courses": [], "stats": {}}


    def get_student_dashboard(self, student_email: str) -> Dict:
        """Get student's enrollments."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT enrollment_id, course_id, student_name, student_email,
                       payment_status, payment_id, progress_percent,
                       enrolled_at, completed_at
                FROM charvak_training_enrollments
                WHERE student_email = %s
                ORDER BY enrolled_at DESC
            ''', (student_email,))
            rows = cur.fetchall()
            enrollments = [self._row_to_enrollment(r) for r in rows]
            cur.close(); conn.close()
            return {
                "status": "success",
                "student_email": student_email,
                "enrollments": enrollments,
                "count": len(enrollments),
            }
        except Exception as e:
            logger.error(f"get_student_dashboard failed: {e}")
            return {"status": "error", "message": str(e), "enrollments": [], "count": 0}


    def _find_course(self, course_id: str) -> Optional[Dict]:
        """Internal helper: return course dict or None."""
        result = self.get_course(course_id)
        if result.get("status") == "success":
            return result.get("course")
        return None



training_engine = TrainingEngine()