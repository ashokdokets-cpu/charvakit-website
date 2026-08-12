"""
Charvak Training Engine
Course posting, enrollment, classroom management
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

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
        self.courses = []
        self.enrollments = []
        self.trainers = []
        self.classrooms = []
        logger.info("✅ Training Engine ready")
    
    def post_course(self, data: Dict) -> Dict:
        """
        Post a new course.
        
        data = {
            "course_name": str,
            "trainer_name": str,
            "trainer_email": str,
            "category": str,
            "duration_weeks": int,
            "price_inr": float,
            "description": str,
            "skills": List[str],
            "schedule": str
        }
        """
        course_id = f"CRS-{secrets.token_hex(4).upper()}"
        price = float(data.get("price_inr", 0))
        
        course = {
            "course_id": course_id,
            "course_name": data.get("course_name"),
            "trainer_name": data.get("trainer_name"),
            "trainer_email": data.get("trainer_email"),
            "category": data.get("category", "Programming"),
            "duration_weeks": int(data.get("duration_weeks", 4)),
            "price_inr": price,
            "platform_fee": round(price * 0.20, 2),
            "trainer_payout": round(price * 0.80, 2),
            "description": data.get("description", ""),
            "skills": data.get("skills", []),
            "schedule": data.get("schedule", "Flexible"),
            "status": CourseStatus.PUBLISHED,
            "enrolled_count": 0,
            "created_at": datetime.now().isoformat()
        }
        
        self.courses.append(course)
        logger.info(f"Course posted: {course_id} - {data.get('course_name')}")
        
        return {
            "status": "success",
            "course_id": course_id,
            "message": "Course published! Students can now enroll.",
            "revenue_split": {
                "trainer_gets": f"80% (₹{course['trainer_payout']})",
                "platform_gets": f"20% (₹{course['platform_fee']})"
            }
        }
    
    def enroll_student(self, data: Dict) -> Dict:
        """
        Enroll a student in a course.
        
        data = {
            "course_id": str,
            "student_name": str,
            "student_email": str,
            "payment_id": str (optional)
        }
        """
        course = self._find_course(data.get("course_id"))
        if not course:
            return {"status": "error", "message": "Course not found"}
        
        enrollment_id = f"ENR-{secrets.token_hex(4).upper()}"
        
        enrollment = {
            "enrollment_id": enrollment_id,
            "course_id": data.get("course_id"),
            "student_name": data.get("student_name"),
            "student_email": data.get("student_email"),
            "payment_status": "completed" if data.get("payment_id") else "pending",
            "enrolled_at": datetime.now().isoformat(),
            "progress_percent": 0,
            "completed_at": None
        }
        
        self.enrollments.append(enrollment)
        course["enrolled_count"] += 1
        
        logger.info(f"Enrollment: {enrollment_id} - {data.get('student_name')} → {course['course_name']}")
        
        return {
            "status": "success",
            "enrollment_id": enrollment_id,
            "message": f"Enrolled in {course['course_name']}!",
            "classroom_link": f"/online-classroom?enrollment={enrollment_id}"
        }
    
    def get_courses(self, category: str = None) -> Dict:
        """Get all published courses."""
        courses = [c for c in self.courses if c["status"] == CourseStatus.PUBLISHED]
        if category:
            courses = [c for c in courses if c["category"] == category]
        
        return {
            "status": "success",
            "courses": courses,
            "count": len(courses),
            "categories": list(set(c["category"] for c in self.courses)),
            "total_enrolled": sum(c["enrolled_count"] for c in courses)
        }
    
    def get_course(self, course_id: str) -> Dict:
        """Get course details."""
        course = self._find_course(course_id)
        if not course:
            return {"status": "error", "message": "Course not found"}
        return {"status": "success", "course": course}
    
    def get_trainer_dashboard(self, trainer_email: str) -> Dict:
        """Get trainer's courses and revenue."""
        trainer_courses = [c for c in self.courses if c["trainer_email"] == trainer_email]
        total_students = sum(c["enrolled_count"] for c in trainer_courses)
        total_revenue = sum(c["enrolled_count"] * c["trainer_payout"] for c in trainer_courses)
        
        return {
            "status": "success",
            "trainer_email": trainer_email,
            "courses": trainer_courses,
            "stats": {
                "total_courses": len(trainer_courses),
                "total_students": total_students,
                "total_revenue_inr": total_revenue
            }
        }
    
    def get_student_dashboard(self, student_email: str) -> Dict:
        """Get student's enrollments."""
        student_enrollments = [e for e in self.enrollments if e["student_email"] == student_email]
        return {
            "status": "success",
            "student_email": student_email,
            "enrollments": student_enrollments,
            "count": len(student_enrollments)
        }
    
    def _find_course(self, course_id: str) -> Optional[Dict]:
        for course in self.courses:
            if course["course_id"] == course_id:
                return course
        return None


training_engine = TrainingEngine()