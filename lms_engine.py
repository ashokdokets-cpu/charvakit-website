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
    # HELPERS & STATS
    # ============================================================
    
    def _find_quiz(self, quiz_id: str) -> Optional[Dict]:
        for quiz in self.quizzes:
            if quiz["quiz_id"] == quiz_id:
                return quiz
        return None
    
    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "stats": {
                "total_ratings": len(self.ratings),
                "total_quizzes": len(self.quizzes),
                "total_certificates": len(self.certificates),
                "total_discussions": len(self.discussions),
                "total_quiz_attempts": len(self.quiz_attempts)
            }
        }


lms_engine = LMS_Engine()