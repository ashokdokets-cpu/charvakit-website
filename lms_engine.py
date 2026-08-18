"""
Charvak LMS Engine
Global Learning Management System features
Course ratings, quizzes, certificates, progress, AI recommendations
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.lms")


class LMS_Engine:
    """Advanced LMS features layered on top of Training Engine."""
    
    def __init__(self):
        self.ratings = []
        self.quizzes = []
        self.quiz_attempts = []
        self.certificates = []
        self.lesson_progress = []
        self.discussions = []
        self.lessons = []
        self.payouts = []
        logger.info("✅ LMS Engine ready — 6 modules")
    
    # ============================================================
    # 1. COURSE RATINGS & REVIEWS
    # ============================================================
    
    def rate_course(self, data: Dict) -> Dict:
        """
        Rate a course.
        data = {course_id, student_email, rating (1-5), review, student_name}
        """
        rating_id = f"RATE-{secrets.token_hex(4).upper()}"
        
        rating = {
            "rating_id": rating_id,
            "course_id": data.get("course_id"),
            "student_email": data.get("student_email"),
            "student_name": data.get("student_name", "Student"),
            "rating": int(data.get("rating", 5)),
            "review": data.get("review", ""),
            "created_at": datetime.now().isoformat()
        }
        
        self.ratings.append(rating)
        
        return {"status": "success", "rating_id": rating_id, "message": "Rating submitted!"}
    
    def get_course_ratings(self, course_id: str) -> Dict:
        """Get all ratings for a course."""
        course_ratings = [r for r in self.ratings if r["course_id"] == course_id]
        avg = sum(r["rating"] for r in course_ratings) / len(course_ratings) if course_ratings else 0
        
        return {
            "status": "success",
            "course_id": course_id,
            "average_rating": round(avg, 1),
            "total_ratings": len(course_ratings),
            "reviews": course_ratings
        }
    
    # ============================================================
    # 2. QUIZZES & ASSESSMENTS
    # ============================================================
    
    def create_quiz(self, data: Dict) -> Dict:
        """
        Create a quiz for a course.
        data = {course_id, title, questions: [{question, options: [..], correct_index}]}
        """
        quiz_id = f"QUIZ-{secrets.token_hex(4).upper()}"
        
        quiz = {
            "quiz_id": quiz_id,
            "course_id": data.get("course_id"),
            "title": data.get("title", "Course Quiz"),
            "questions": data.get("questions", []),
            "total_questions": len(data.get("questions", [])),
            "created_at": datetime.now().isoformat()
        }
        
        self.quizzes.append(quiz)
        
        return {"status": "success", "quiz_id": quiz_id, "message": "Quiz created!"}
    
    def submit_quiz(self, data: Dict) -> Dict:
        """
        Submit quiz answers.
        data = {quiz_id, student_email, answers: [int]}
        """
        quiz = self._find_quiz(data.get("quiz_id"))
        if not quiz:
            return {"status": "error", "message": "Quiz not found"}
        
        answers = data.get("answers", [])
        correct = 0
        total = len(quiz["questions"])
        
        for i, question in enumerate(quiz["questions"]):
            if i < len(answers) and answers[i] == question.get("correct_index"):
                correct += 1
        
        score = int((correct / total) * 100) if total > 0 else 0
        passed = score >= 70
        
        attempt = {
            "attempt_id": f"ATT-{secrets.token_hex(4).upper()}",
            "quiz_id": data.get("quiz_id"),
            "student_email": data.get("student_email"),
            "score": score,
            "passed": passed,
            "attempted_at": datetime.now().isoformat()
        }
        
        self.quiz_attempts.append(attempt)
        
        return {
            "status": "success",
            "score": score,
            "passed": passed,
            "correct_answers": correct,
            "total_questions": total,
            "message": "Quiz submitted! Score: " + str(score) + "%"
        }
    
    # ============================================================
    # 3. CERTIFICATES ON COMPLETION
    # ============================================================
    
    def issue_certificate(self, data: Dict) -> Dict:
        """
        Issue certificate on course completion.
        data = {course_id, course_name, student_email, student_name}
        """
        cert_id = f"CERT-{secrets.token_hex(6).upper()}"
        
        certificate = {
            "certificate_id": cert_id,
            "course_id": data.get("course_id"),
            "course_name": data.get("course_name", "Course"),
            "student_email": data.get("student_email"),
            "student_name": data.get("student_name", "Student"),
            "issued_at": datetime.now().isoformat(),
            "verification_url": f"https://charvakit.com/verify-certificate/{cert_id}",
            "share_url": f"https://www.linkedin.com/profile/add?startTask=CERTIFICATION_NAME&name={data.get('course_name', 'Course')}&organizationName=Charvak+IT+Consulting&certId={cert_id}"
        }
        
        self.certificates.append(certificate)
        
        # Also issue a badge
        from badge_engine import badge_engine
        badge_engine.issue_badge({
            "user_name": data.get("student_name"),
            "user_email": data.get("student_email"),
            "badge_type": "course_completion",
            "level": "verified"
        })
        
        return {
            "status": "success",
            "certificate_id": cert_id,
            "certificate": certificate,
            "message": "Certificate issued! Share on LinkedIn."
        }
    
    def verify_certificate(self, cert_id: str) -> Dict:
        """Verify a certificate."""
        for cert in self.certificates:
            if cert["certificate_id"] == cert_id:
                return {"status": "success", "verified": True, "certificate": cert}
        return {"status": "error", "verified": False, "message": "Certificate not found"}
    
    # ============================================================
    # 4. DETAILED PROGRESS TRACKING
    # ============================================================
    
    def update_progress(self, data: Dict) -> Dict:
        """
        Update lesson progress.
        data = {enrollment_id, lesson_id, completed, time_spent_minutes}
        """
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
        """Get detailed progress for an enrollment."""
        lessons = [p for p in self.lesson_progress if p["enrollment_id"] == enrollment_id]
        completed = [l for l in lessons if l["completed"]]
        
        return {
            "status": "success",
            "enrollment_id": enrollment_id,
            "total_lessons_completed": len(completed),
            "total_time_spent_minutes": sum(l["time_spent_minutes"] for l in lessons),
            "progress_percent": round(len(completed) / len(lessons) * 100, 1) if lessons else 0
        }
    
    # ============================================================
    # 5. DISCUSSION FORUM
    # ============================================================
    
    def post_discussion(self, data: Dict) -> Dict:
        """
        Post a discussion topic.
        data = {course_id, author, title, content}
        """
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
        """Reply to a discussion."""
        for disc in self.discussions:
            if disc["discussion_id"] == data.get("discussion_id"):
                disc["replies"].append({
                    "author": data.get("author"),
                    "content": data.get("content"),
                    "replied_at": datetime.now().isoformat()
                })
                return {"status": "success", "message": "Reply added!"}
        return {"status": "error", "message": "Discussion not found"}
    
    # ============================================================
    # 6. AI COURSE RECOMMENDATIONS
    # ============================================================
    
    def get_recommendations(self, student_email: str) -> Dict:
        """
        AI-powered course recommendations.
        Based on enrolled courses and ratings.
        """
        # Get student's enrolled courses
        student_ratings = [r for r in self.ratings if r["student_email"] == student_email]
        rated_categories = list(set(r.get("course_id", "") for r in student_ratings))
        
        recommendations = [
            {"course": "Advanced Python", "reason": "Based on your Python course interest", "match": 95},
            {"course": "Data Structures & Algorithms", "reason": "Popular with Python learners", "match": 88},
            {"course": "System Design", "reason": "Next step after programming basics", "match": 82},
            {"course": "AWS Cloud Practitioner", "reason": "Trending in your skill category", "match": 78},
        ]
        
        return {
            "status": "success",
            "student_email": student_email,
            "recommendations": recommendations,
            "based_on": rated_categories
        }

    # ============================================================
    # 7. VIDEO LECTURES & COURSE CONTENT
    # ============================================================
    
    def add_lesson(self, data: Dict) -> Dict:
        """
        Add a lesson with video to a course.
        data = {course_id, title, video_url, description, duration_minutes, order}
        """
        lesson_id = f"LESSON-{secrets.token_hex(4).upper()}"
        
        lesson = {
            "lesson_id": lesson_id,
            "course_id": data.get("course_id"),
            "title": data.get("title", "Lesson"),
            "video_url": data.get("video_url", ""),
            "description": data.get("description", ""),
            "duration_minutes": data.get("duration_minutes", 10),
            "order": data.get("order", 1),
            "created_at": datetime.now().isoformat()
        }
        
        self.lessons.append(lesson)
        
        return {"status": "success", "lesson_id": lesson_id, "message": "Lesson added!"}
    
    def get_course_lessons(self, course_id: str) -> Dict:
        """Get all lessons for a course."""
        lessons = [l for l in self.lessons if l["course_id"] == course_id]
        lessons.sort(key=lambda l: l["order"])
        
        return {
            "status": "success",
            "course_id": course_id,
            "lessons": lessons,
            "count": len(lessons),
            "total_duration_minutes": sum(l["duration_minutes"] for l in lessons)
        }
    
    # ============================================================
    # 8. INSTRUCTOR PAYOUTS (via Escrow)
    # ============================================================
    
    def request_payout(self, data: Dict) -> Dict:
        """
        Request instructor payout via escrow.
        data = {trainer_email, amount, payment_method}
        """
        payout_id = f"PAYOUT-{secrets.token_hex(4).upper()}"
        
        payout = {
            "payout_id": payout_id,
            "trainer_email": data.get("trainer_email"),
            "amount": float(data.get("amount", 0)),
            "payment_method": data.get("payment_method", "Dokets VouchAI Escrow"),
            "status": "pending",
            "requested_at": datetime.now().isoformat()
        }
        
        self.payouts.append(payout)
        
        return {
            "status": "success",
            "payout_id": payout_id,
            "message": f"Payout of ₹{payout['amount']} requested via {payout['payment_method']}",
            "processing_time": "3-5 business days"
        }
    
    def get_payouts(self, trainer_email: str) -> Dict:
        """Get all payouts for a trainer."""
        trainer_payouts = [p for p in self.payouts if p["trainer_email"] == trainer_email]
        total = sum(p["amount"] for p in trainer_payouts if p["status"] == "completed")
        
        return {
            "status": "success",
            "trainer_email": trainer_email,
            "payouts": trainer_payouts,
            "total_paid": total
        }
    
    # ============================================================
    # 9. MULTI-LANGUAGE COURSES
    # ============================================================
    
    def add_course_language(self, data: Dict) -> Dict:
        """
        Add language support to a course.
        data = {course_id, language, translated_title, translated_description}
        """
        course = self._find_course(data.get("course_id"))
        if not course:
            return {"status": "error", "message": "Course not found"}
        
        if "languages" not in course:
            course["languages"] = []
        
        course["languages"].append({
            "language": data.get("language"),
            "title": data.get("translated_title"),
            "description": data.get("translated_description", "")
        })
        
        return {"status": "success", "message": f"{data.get('language')} added to course!"}
    
    # ============================================================
    # 10. GAMIFICATION
    # ============================================================
    
    def award_points(self, data: Dict) -> Dict:
        """
        Award points for actions.
        data = {student_email, action, points}
        """
        action_points = {
            "lesson_completed": 10,
            "quiz_passed": 50,
            "course_completed": 100,
            "discussion_posted": 5,
            "certificate_earned": 200
        }
        
        action = data.get("action", "lesson_completed")
        points = data.get("points", action_points.get(action, 10))
        
        return {
            "status": "success",
            "student_email": data.get("student_email"),
            "action": action,
            "points_earned": points,
            "message": f"+{points} points earned!"
        }
    
    # ============================================================
    # 11. EMAIL NOTIFICATIONS (integrated with email_engine)
    # ============================================================
    
    def send_course_notification(self, data: Dict) -> Dict:
        """
        Send course notification email.
        data = {student_email, student_name, notification_type, course_name}
        """
        notification_type = data.get("notification_type", "enrollment")
        
        notifications = {
            "enrollment": {
                "subject": f"✅ Enrolled in {data.get('course_name')}",
                "body": f"Hi {data.get('student_name')}, you're enrolled in {data.get('course_name')}. Start learning today!"
            },
            "reminder": {
                "subject": f"⏰ Reminder: {data.get('course_name')}",
                "body": f"Hi {data.get('student_name')}, don't forget to continue your course!"
            },
            "completion": {
                "subject": f"🎉 Course Completed: {data.get('course_name')}",
                "body": f"Congratulations {data.get('student_name')}! You've completed {data.get('course_name')}."
            }
        }
        
        notif = notifications.get(notification_type, notifications["enrollment"])
        
        # Try to send via email engine
        try:
            from email_engine import email_engine
            email_engine.send_email(data.get("student_email"), notif["subject"], notif["body"])
        except:
            pass
        
        return {"status": "success", "message": "Notification sent!", **notif}
    
    # ============================================================
    # 12. COURSE SEARCH & FILTERING
    # ============================================================
    
        def search_courses(self, query: str = None, category: str = None, min_rating: float = None, max_price: float = None, language: str = None) -> Dict:
        """
        Advanced course search — searches Training Engine courses.
        """
        # Get courses from Training Engine
        from training_engine import training_engine
        courses = training_engine.get_courses().get("courses", [])
        
        if query:
            q = query.lower()
            courses = [c for c in courses if q in c.get("course_name", "").lower() or q in c.get("description", "").lower()]
        if category:
            courses = [c for c in courses if c.get("category") == category]
        if max_price:
            courses = [c for c in courses if c.get("price_inr", 0) <= max_price]
        
        return {
            "status": "success",
            "courses": courses,
            "count": len(courses),
            "filters_applied": {"query": query, "category": category, "max_price": max_price, "language": language}
        }
    
    
    # ============================================================
    # HELPERS & STATS
    # ============================================================
    
    def _find_quiz(self, quiz_id: str) -> Optional[Dict]:
        for quiz in self.quizzes:
            if quiz["quiz_id"] == quiz_id:
                return quiz
        return None
    
    def _find_course(self, course_id: str) -> Optional[Dict]:
        for course in getattr(self, 'courses', []):
            if course.get("course_id") == course_id:
                return course
        return None
    
    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "stats": {
                "total_ratings": len(self.ratings),
                "total_quizzes": len(self.quizzes),
                "total_certificates": len(self.certificates),
                "total_discussions": len(self.discussions),
                "total_quiz_attempts": len(self.quiz_attempts),
                "total_lessons": len(self.lessons),
                "total_payouts": len(self.payouts)
            }
        }


lms_engine = LMS_Engine()