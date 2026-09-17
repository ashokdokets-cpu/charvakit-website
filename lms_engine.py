"""
Charvak LMS Engine
Global Learning Management System
Ratings, quizzes, certificates, lessons, payouts, gamification
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets
import json

logger = logging.getLogger("charvakit.lms")


class LMS_Engine:
    """Advanced LMS features."""
    
    def __init__(self):
        self._ensure_tables()
        logger.info("LMS Engine ready (DB-backed)")

    def _ensure_tables(self):
        """Idempotent table creation for LMS tables."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_lms_ratings (
                    rating_id TEXT PRIMARY KEY, course_id TEXT NOT NULL,
                    student_email TEXT NOT NULL, rating INTEGER NOT NULL,
                    review TEXT DEFAULT '', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_lms_quizzes (
                    quiz_id TEXT PRIMARY KEY, course_id TEXT NOT NULL,
                    title TEXT DEFAULT 'Course Quiz', questions JSONB DEFAULT '[]'::jsonb,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_lms_quiz_attempts (
                    attempt_id TEXT PRIMARY KEY, quiz_id TEXT, course_id TEXT,
                    student_email TEXT NOT NULL, score INTEGER DEFAULT 0,
                    passed BOOLEAN DEFAULT FALSE, attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_lms_certificates (
                    certificate_id TEXT PRIMARY KEY, course_name TEXT,
                    student_email TEXT NOT NULL, student_name TEXT DEFAULT 'Student',
                    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, verification_url TEXT
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_lms_lesson_progress (
                    progress_id TEXT PRIMARY KEY, enrollment_id TEXT NOT NULL,
                    lesson_id TEXT NOT NULL, completed BOOLEAN DEFAULT TRUE,
                    time_spent_minutes INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_lms_discussions (
                    discussion_id TEXT PRIMARY KEY, course_id TEXT NOT NULL,
                    author TEXT, title TEXT, content TEXT,
                    replies JSONB DEFAULT '[]'::jsonb,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_lms_lessons (
                    lesson_id TEXT PRIMARY KEY, course_id TEXT NOT NULL,
                    title TEXT DEFAULT 'Lesson', video_url TEXT DEFAULT '',
                    duration_minutes INTEGER DEFAULT 10, lesson_order INTEGER DEFAULT 1
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_lms_payouts (
                    payout_id TEXT PRIMARY KEY, trainer_email TEXT NOT NULL,
                    amount NUMERIC(10,2) DEFAULT 0, status TEXT DEFAULT 'pending',
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"lms tables init failed: {e}")


    def rate_course(self, data: Dict) -> Dict:
        rating_id = f"RATE-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_lms_ratings
                    (rating_id, course_id, student_email, rating, review)
                VALUES (%s, %s, %s, %s, %s)
            ''', (rating_id, data.get("course_id"), data.get("student_email"),
                  int(data.get("rating", 5)), data.get("review", "")))
            conn.commit()
            cur.close(); conn.close()
            return {"status": "success", "rating_id": rating_id, "message": "Rating submitted!"}
        except Exception as e:
            logger.error(f"rate_course failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_course_ratings(self, course_id: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT rating_id, course_id, student_email, rating, review, created_at
                FROM charvak_lms_ratings WHERE course_id = %s
                ORDER BY created_at DESC
            ''', (course_id,))
            rows = cur.fetchall()
            cur.close(); conn.close()
            reviews = [{
                "rating_id": r[0], "course_id": r[1], "student_email": r[2],
                "rating": r[3], "review": r[4] or "",
                "created_at": r[5].isoformat() if r[5] else None,
            } for r in rows]
            avg = sum(x["rating"] for x in reviews) / len(reviews) if reviews else 0
            return {
                "status": "success",
                "average_rating": round(avg, 1),
                "total_ratings": len(reviews),
                "reviews": reviews,
            }
        except Exception as e:
            logger.error(f"get_course_ratings failed: {e}")
            return {"status": "error", "message": str(e), "average_rating": 0, "total_ratings": 0, "reviews": []}


    def create_quiz(self, data: Dict) -> Dict:
        quiz_id = f"QUIZ-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_lms_quizzes
                    (quiz_id, course_id, title, questions)
                VALUES (%s, %s, %s, %s::jsonb)
            ''', (quiz_id, data.get("course_id"),
                  data.get("title", "Course Quiz"),
                  json.dumps(data.get("questions", []))))
            conn.commit()
            cur.close(); conn.close()
            return {"status": "success", "quiz_id": quiz_id, "message": "Quiz created!"}
        except Exception as e:
            logger.error(f"create_quiz failed: {e}")
            return {"status": "error", "message": str(e)}


    def submit_quiz(self, data: Dict) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT quiz_id, course_id, questions FROM charvak_lms_quizzes
                WHERE quiz_id = %s
            ''', (data.get("quiz_id"),))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Quiz not found"}
            quiz_id, course_id, questions_raw = row
            questions = questions_raw if isinstance(questions_raw, list) else json.loads(questions_raw or "[]")
            answers = data.get("answers", [])
            correct = 0
            total = len(questions)
            for i, question in enumerate(questions):
                if i < len(answers) and answers[i] == question.get("correct_index"):
                    correct += 1
            score = int((correct / total) * 100) if total > 0 else 0
            attempt_id = f"ATT-{secrets.token_hex(4).upper()}"
            passed = score >= 70
            cur.execute('''
                INSERT INTO charvak_lms_quiz_attempts
                    (attempt_id, quiz_id, course_id, student_email, score, passed)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (attempt_id, quiz_id, course_id, data.get("student_email"), score, passed))
            conn.commit()
            cur.close(); conn.close()
            return {"status": "success", "score": score, "passed": passed, "message": f"Score: {score}%"}
        except Exception as e:
            logger.error(f"submit_quiz failed: {e}")
            return {"status": "error", "message": str(e)}


    def issue_certificate(self, data: Dict) -> Dict:
        cert_id = f"CERT-{secrets.token_hex(6).upper()}"
        course_name = data.get("course_name", "Course")
        student_email = data.get("student_email")
        student_name = data.get("student_name", "Student")
        verification_url = f"https://charvakit.com/verify-certificate/{cert_id}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_lms_certificates
                    (certificate_id, course_name, student_email, student_name, verification_url)
                VALUES (%s, %s, %s, %s, %s)
            ''', (cert_id, course_name, student_email, student_name, verification_url))
            conn.commit()
            cur.close(); conn.close()
            try:
                from badge_engine import badge_engine
                badge_engine.issue_badge({
                    "user_name": student_name,
                    "user_email": student_email,
                    "badge_type": "course_completion",
                    "level": "verified",
                })
            except Exception:
                pass
            return {"status": "success", "certificate_id": cert_id, "message": "Certificate issued!"}
        except Exception as e:
            logger.error(f"issue_certificate failed: {e}")
            return {"status": "error", "message": str(e)}


    def verify_certificate(self, cert_id: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT certificate_id, course_name, student_email, student_name,
                       issued_at, verification_url
                FROM charvak_lms_certificates WHERE certificate_id = %s
            ''', (cert_id,))
            r = cur.fetchone()
            cur.close(); conn.close()
            if not r:
                return {"status": "error", "verified": False, "message": "Certificate not found"}
            cert = {
                "certificate_id": r[0], "course_name": r[1],
                "student_email": r[2], "student_name": r[3],
                "issued_at": r[4].isoformat() if r[4] else None,
                "verification_url": r[5],
            }
            return {"status": "success", "verified": True, "certificate": cert}
        except Exception as e:
            logger.error(f"verify_certificate failed: {e}")
            return {"status": "error", "verified": False, "message": str(e)}


    def update_progress(self, data: Dict) -> Dict:
        progress_id = f"PROG-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_lms_lesson_progress
                    (progress_id, enrollment_id, lesson_id, completed, time_spent_minutes)
                VALUES (%s, %s, %s, %s, %s)
            ''', (progress_id, data.get("enrollment_id"), data.get("lesson_id"),
                  bool(data.get("completed", True)),
                  int(data.get("time_spent_minutes", 0))))
            conn.commit()
            cur.close(); conn.close()
            return {"status": "success", "progress_id": progress_id, "message": "Progress updated"}
        except Exception as e:
            logger.error(f"update_progress failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_progress(self, enrollment_id: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT completed, time_spent_minutes FROM charvak_lms_lesson_progress
                WHERE enrollment_id = %s
            ''', (enrollment_id,))
            rows = cur.fetchall()
            cur.close(); conn.close()
            lessons = [{"completed": r[0], "time_spent_minutes": r[1] or 0} for r in rows]
            completed = [l for l in lessons if l["completed"]]
            total_time = sum(l["time_spent_minutes"] for l in lessons)
            pct = round(len(completed) / len(lessons) * 100, 1) if lessons else 0
            return {
                "status": "success",
                "total_lessons_completed": len(completed),
                "total_time_spent_minutes": total_time,
                "progress_percent": pct,
            }
        except Exception as e:
            logger.error(f"get_progress failed: {e}")
            return {"status": "error", "message": str(e), "total_lessons_completed": 0, "total_time_spent_minutes": 0, "progress_percent": 0}


    def post_discussion(self, data: Dict) -> Dict:
        discussion_id = f"DISC-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_lms_discussions
                    (discussion_id, course_id, author, title, content, replies)
                VALUES (%s, %s, %s, %s, %s, '[]'::jsonb)
            ''', (discussion_id, data.get("course_id"), data.get("author"),
                  data.get("title"), data.get("content")))
            conn.commit()
            cur.close(); conn.close()
            return {"status": "success", "discussion_id": discussion_id, "message": "Discussion posted!"}
        except Exception as e:
            logger.error(f"post_discussion failed: {e}")
            return {"status": "error", "message": str(e)}


    def reply_discussion(self, data: Dict) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT replies FROM charvak_lms_discussions WHERE discussion_id = %s
            ''', (data.get("discussion_id"),))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Discussion not found"}
            replies = row[0] if isinstance(row[0], list) else json.loads(row[0] or "[]")
            replies.append({
                "author": data.get("author"),
                "content": data.get("content"),
                "replied_at": datetime.now().isoformat(),
            })
            cur.execute('''
                UPDATE charvak_lms_discussions SET replies = %s::jsonb
                WHERE discussion_id = %s
            ''', (json.dumps(replies), data.get("discussion_id")))
            conn.commit()
            cur.close(); conn.close()
            return {"status": "success", "message": "Reply added!"}
        except Exception as e:
            logger.error(f"reply_discussion failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_recommendations(self, student_email: str) -> Dict:
        recommendations = [
            {"course": "Advanced Python", "match": 95},
            {"course": "Data Structures", "match": 88},
            {"course": "System Design", "match": 82}
        ]
        return {"status": "success", "recommendations": recommendations}

    def add_lesson(self, data: Dict) -> Dict:
        lesson_id = f"LESSON-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_lms_lessons
                    (lesson_id, course_id, title, video_url, duration_minutes, lesson_order)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (lesson_id, data.get("course_id"),
                  data.get("title", "Lesson"),
                  data.get("video_url", ""),
                  int(data.get("duration_minutes", 10)),
                  int(data.get("order", 1))))
            conn.commit()
            cur.close(); conn.close()
            return {"status": "success", "lesson_id": lesson_id, "message": "Lesson added!"}
        except Exception as e:
            logger.error(f"add_lesson failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_course_lessons(self, course_id: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT lesson_id, course_id, title, video_url, duration_minutes, lesson_order
                FROM charvak_lms_lessons WHERE course_id = %s
                ORDER BY lesson_order
            ''', (course_id,))
            rows = cur.fetchall()
            cur.close(); conn.close()
            lessons = [{
                "lesson_id": r[0], "course_id": r[1], "title": r[2],
                "video_url": r[3] or "", "duration_minutes": r[4] or 10,
                "order": r[5] or 1,
            } for r in rows]
            return {"status": "success", "lessons": lessons, "count": len(lessons)}
        except Exception as e:
            logger.error(f"get_course_lessons failed: {e}")
            return {"status": "error", "message": str(e), "lessons": [], "count": 0}


    def request_payout(self, data: Dict) -> Dict:
        payout_id = f"PAYOUT-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_lms_payouts
                    (payout_id, trainer_email, amount, status)
                VALUES (%s, %s, %s, 'pending')
            ''', (payout_id, data.get("trainer_email"), float(data.get("amount", 0))))
            conn.commit()
            cur.close(); conn.close()
            return {"status": "success", "payout_id": payout_id, "message": "Payout requested"}
        except Exception as e:
            logger.error(f"request_payout failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_payouts(self, trainer_email: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT payout_id, trainer_email, amount, status, requested_at
                FROM charvak_lms_payouts WHERE trainer_email = %s
                ORDER BY requested_at DESC
            ''', (trainer_email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
            payouts = [{
                "payout_id": r[0], "trainer_email": r[1],
                "amount": float(r[2] or 0), "status": r[3],
                "requested_at": r[4].isoformat() if r[4] else None,
            } for r in rows]
            return {"status": "success", "payouts": payouts}
        except Exception as e:
            logger.error(f"get_payouts failed: {e}")
            return {"status": "error", "message": str(e), "payouts": []}


    def award_points(self, data: Dict) -> Dict:
        points = data.get("points", 10)
        return {"status": "success", "points_earned": points, "message": f"+{points} points!"}

    def send_course_notification(self, data: Dict) -> Dict:
        return {"status": "success", "message": "Notification sent!"}
    def search_courses(self, query: str = None, category: str = None, price: float = None, max_price: float = None, language: str = None) -> Dict:
        try:
            from training_engine import training_engine
            courses = training_engine.get_courses().get("courses", [])
        except:
            courses = []

        if query:
            q = query.lower()
            courses = [c for c in courses if q in c.get("course_name", "").lower()]

        if category:
            courses = [c for c in courses if c.get("category") == category]

        if max_price:
            courses = [c for c in courses if c.get("price", 0) <= max_price]

        if language:
            courses = [c for c in courses if c.get("language", "").lower() == language.lower()]

        return {"status": "success", "courses": courses, "count": len(courses)}
        
    def get_stats(self) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM charvak_lms_ratings")
            total_ratings = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_lms_quizzes")
            total_quizzes = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_lms_certificates")
            total_certificates = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_lms_discussions")
            total_discussions = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_lms_lessons")
            total_lessons = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_lms_payouts")
            total_payouts = cur.fetchone()[0] or 0
            cur.close(); conn.close()
            return {
                "status": "success",
                "stats": {
                    "total_ratings": total_ratings,
                    "total_quizzes": total_quizzes,
                    "total_certificates": total_certificates,
                    "total_discussions": total_discussions,
                    "total_lessons": total_lessons,
                    "total_payouts": total_payouts,
                },
            }
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": str(e), "stats": {}}



lms_engine = LMS_Engine()
