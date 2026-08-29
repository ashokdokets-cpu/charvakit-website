"""
Charvak LMS Engine
Global Learning Management System
Ratings, quizzes, certificates, lessons, payouts, gamification
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.lms")


class LMS_Engine:
    """Advanced LMS features."""
    
    def __init__(self):
        self.ratings = []
        self.quizzes = []
        self.quiz_attempts = []
        self.certificates = []
        self.lesson_progress = []
        self.discussions = []
        self.lessons = []
        self.payouts = []
        logger.info("LMS Engine ready")

    def rate_course(self, data: Dict) -> Dict:
        rating_id = f"RATE-{secrets.token_hex(4).upper()}"
        rating = {
            "rating_id": rating_id,
            "course_id": data.get("course_id"),
            "student_email": data.get("student_email"),
            "rating": int(data.get("rating", 5)),
            "review": data.get("review", ""),
            "created_at": datetime.now().isoformat()
        }
        self.ratings.append(rating)
        return {"status": "success", "rating_id": rating_id, "message": "Rating submitted!"}

    def get_course_ratings(self, course_id: str) -> Dict:
        course_ratings = [r for r in self.ratings if r["course_id"] == course_id]
        avg = sum(r["rating"] for r in course_ratings) / len(course_ratings) if course_ratings else 0
        return {
            "status": "success",
            "average_rating": round(avg, 1),
            "total_ratings": len(course_ratings),
            "reviews": course_ratings
        }

    def create_quiz(self, data: Dict) -> Dict:
        quiz_id = f"QUIZ-{secrets.token_hex(4).upper()}"
        quiz = {
            "quiz_id": quiz_id,
            "course_id": data.get("course_id"),
            "title": data.get("title", "Course Quiz"),
            "questions": data.get("questions", []),
            "created_at": datetime.now().isoformat()
        }
        self.quizzes.append(quiz)
        return {"status": "success", "quiz_id": quiz_id, "message": "Quiz created!"}

    def submit_quiz(self, data: Dict) -> Dict:
        quiz = None
        for q in self.quizzes:
            if q["quiz_id"] == data.get("quiz_id"):
                quiz = q
                break
        if not quiz:
            return {"status": "error", "message": "Quiz not found"}
        answers = data.get("answers", [])
        correct = 0
        total = len(quiz["questions"])
        for i, question in enumerate(quiz["questions"]):
            if i < len(answers) and answers[i] == question.get("correct_index"):
                correct += 1
        score = int((correct / total) * 100) if total > 0 else 0
        attempt = {
            "attempt_id": f"ATT-{secrets.token_hex(4).upper()}",
            "student_email": data.get("student_email"),
            "score": score,
            "passed": score >= 70,
            "attempted_at": datetime.now().isoformat()
        }
        self.quiz_attempts.append(attempt)
        return {"status": "success", "score": score, "passed": score >= 70, "message": f"Score: {score}%"}

    def issue_certificate(self, data: Dict) -> Dict:
        cert_id = f"CERT-{secrets.token_hex(6).upper()}"
        certificate = {
            "certificate_id": cert_id,
            "course_name": data.get("course_name", "Course"),
            "student_email": data.get("student_email"),
            "student_name": data.get("student_name", "Student"),
            "issued_at": datetime.now().isoformat(),
            "verification_url": f"https://charvakit.com/verify-certificate/{cert_id}"
        }
        self.certificates.append(certificate)
        try:
            from badge_engine import badge_engine
            badge_engine.issue_badge({
                "user_name": data.get("student_name"),
                "user_email": data.get("student_email"),
                "badge_type": "course_completion",
                "level": "verified"
            })
        except:
            pass
        return {"status": "success", "certificate_id": cert_id, "message": "Certificate issued!"}

    def verify_certificate(self, cert_id: str) -> Dict:
        for cert in self.certificates:
            if cert["certificate_id"] == cert_id:
                return {"status": "success", "verified": True, "certificate": cert}
        return {"status": "error", "verified": False, "message": "Certificate not found"}

    def update_progress(self, data: Dict) -> Dict:
        progress_id = f"PROG-{secrets.token_hex(4).upper()}"
        progress = {
            "progress_id": progress_id,
            "enrollment_id": data.get("enrollment_id"),
            "lesson_id": data.get("lesson_id"),
            "completed": data.get("completed", True),
            "time_spent_minutes": data.get("time_spent_minutes", 0),
            "updated_at": datetime.now().isoformat()
        }
        self.lesson_progress.append(progress)
        return {"status": "success", "progress_id": progress_id, "message": "Progress updated"}

    def get_progress(self, enrollment_id: str) -> Dict:
        lessons = [p for p in self.lesson_progress if p["enrollment_id"] == enrollment_id]
        completed = [l for l in lessons if l["completed"]]
        return {
            "status": "success",
            "total_lessons_completed": len(completed),
            "total_time_spent_minutes": sum(l["time_spent_minutes"] for l in lessons),
            "progress_percent": round(len(completed) / len(lessons) * 100, 1) if lessons else 0
        }

    def post_discussion(self, data: Dict) -> Dict:
        discussion_id = f"DISC-{secrets.token_hex(4).upper()}"
        discussion = {
            "discussion_id": discussion_id,
            "course_id": data.get("course_id"),
            "author": data.get("author"),
            "title": data.get("title"),
            "content": data.get("content"),
            "replies": [],
            "created_at": datetime.now().isoformat()
        }
        self.discussions.append(discussion)
        return {"status": "success", "discussion_id": discussion_id, "message": "Discussion posted!"}

    def reply_discussion(self, data: Dict) -> Dict:
        for disc in self.discussions:
            if disc["discussion_id"] == data.get("discussion_id"):
                disc["replies"].append({
                    "author": data.get("author"),
                    "content": data.get("content"),
                    "replied_at": datetime.now().isoformat()
                })
                return {"status": "success", "message": "Reply added!"}
        return {"status": "error", "message": "Discussion not found"}

    def get_recommendations(self, student_email: str) -> Dict:
        recommendations = [
            {"course": "Advanced Python", "match": 95},
            {"course": "Data Structures", "match": 88},
            {"course": "System Design", "match": 82}
        ]
        return {"status": "success", "recommendations": recommendations}

    def add_lesson(self, data: Dict) -> Dict:
        lesson_id = f"LESSON-{secrets.token_hex(4).upper()}"
        lesson = {
            "lesson_id": lesson_id,
            "course_id": data.get("course_id"),
            "title": data.get("title", "Lesson"),
            "video_url": data.get("video_url", ""),
            "duration_minutes": data.get("duration_minutes", 10),
            "order": data.get("order", 1)
        }
        self.lessons.append(lesson)
        return {"status": "success", "lesson_id": lesson_id, "message": "Lesson added!"}

    def get_course_lessons(self, course_id: str) -> Dict:
        lessons = [l for l in self.lessons if l["course_id"] == course_id]
        lessons.sort(key=lambda l: l["order"])
        return {"status": "success", "lessons": lessons, "count": len(lessons)}

    def request_payout(self, data: Dict) -> Dict:
        payout_id = f"PAYOUT-{secrets.token_hex(4).upper()}"
        payout = {
            "payout_id": payout_id,
            "trainer_email": data.get("trainer_email"),
            "amount": float(data.get("amount", 0)),
            "status": "pending",
            "requested_at": datetime.now().isoformat()
        }
        self.payouts.append(payout)
        return {"status": "success", "payout_id": payout_id, "message": "Payout requested"}

    def get_payouts(self, trainer_email: str) -> Dict:
        trainer_payouts = [p for p in self.payouts if p["trainer_email"] == trainer_email]
        return {"status": "success", "payouts": trainer_payouts}

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
        return {
            "status": "success",
            "stats": {
                "total_ratings": len(self.ratings),
                "total_quizzes": len(self.quizzes),
                "total_certificates": len(self.certificates),
                "total_discussions": len(self.discussions),
                "total_lessons": len(self.lessons),
                "total_payouts": len(self.payouts)
            }
        }


lms_engine = LMS_Engine()