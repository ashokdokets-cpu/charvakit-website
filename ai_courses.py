"""
Charvak AI-Driven Course System
AI plans curriculum, delivers content, assists projects, issues certificates
"""
import logging
import json
import os
from datetime import datetime, timedelta

logger = logging.getLogger("charvakit.ai_courses")

class AICourseSystem:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.courses = {}
        self.enrollments = {}
        self.certificates = {}
        logger.info(f"AI Course System - OpenAI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")
    
    def plan_curriculum(self, course_name, duration_weeks, user_level="beginner"):
        """AI plans curriculum based on course and duration."""
        if self.openai_api_key:
            curriculum = self._ai_plan_curriculum(course_name, duration_weeks, user_level)
            if curriculum:
                return curriculum
        
        # Fallback curriculum
        return self._fallback_curriculum(course_name, duration_weeks)
    
    def _ai_plan_curriculum(self, course_name, duration_weeks, user_level):
        """AI generates curriculum."""
        try:
            import requests
            prompt = f"Create a {duration_weeks}-week curriculum for {course_name} for {user_level} level. Include weekly topics, learning objectives, projects, and assessments. Return JSON."
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8, "max_tokens": 3000},
                timeout=20
            )
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger.error(f"AI curriculum failed: {e}")
        return None
    
    def _fallback_curriculum(self, course_name, duration_weeks):
        """Fallback curriculum."""
        weeks = []
        for i in range(1, duration_weeks + 1):
            weeks.append({
                "week": i,
                "topic": f"{course_name} - Week {i} Topic",
                "objectives": [f"Learn {course_name} concept {i}"],
                "project": f"Week {i} Project",
                "assessment": f"Week {i} Quiz"
            })
        return {"course": course_name, "duration_weeks": duration_weeks, "weeks": weeks}
    
    def enroll_student(self, email, course_name, duration_weeks, user_level="beginner"):
        """Enroll student in AI-driven course."""
        enrollment_id = f"ENROLL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        curriculum = self.plan_curriculum(course_name, duration_weeks, user_level)
        
        self.enrollments[enrollment_id] = {
            "enrollment_id": enrollment_id,
            "email": email,
            "course": course_name,
            "duration_weeks": duration_weeks,
            "user_level": user_level,
            "curriculum": curriculum,
            "progress": 0,
            "started_at": datetime.now().isoformat(),
            "status": "active",
            "ai_tutor": True
        }
        
        return {"status": "success", "enrollment": self.enrollments[enrollment_id]}
    
    def get_weekly_content(self, enrollment_id, week_num):
        """AI generates content for specific week."""
        if enrollment_id not in self.enrollments:
            return {"status": "error", "message": "Enrollment not found"}
        
        enrollment = self.enrollments[enrollment_id]
        curriculum = enrollment["curriculum"]
        
        if self.openai_api_key:
            content = self._ai_weekly_content(enrollment["course"], week_num, curriculum)
            if content:
                return {"status": "success", "content": content}
        
        return {
            "status": "success",
            "content": {
                "week": week_num,
                "lesson": f"AI-generated lesson for {enrollment['course']} Week {week_num}",
                "examples": ["Example 1", "Example 2"],
                "practice": ["Exercise 1", "Exercise 2"],
                "project": f"Week {week_num} Project"
            }
        }
    
    def _ai_weekly_content(self, course_name, week_num, curriculum):
        """AI generates weekly lesson content."""
        try:
            import requests
            prompt = f"Generate Week {week_num} lesson content for {course_name} course. Include: lesson explanation, code examples, practice exercises, and project task. Return JSON."
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8, "max_tokens": 2000},
                timeout=15
            )
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger.error(f"AI weekly content failed: {e}")
        return None
    
    def assist_project(self, enrollment_id, project_question):
        """AI assists with project in real-time."""
        if self.openai_api_key:
            try:
                import requests
                prompt = f"Help student with project question: {project_question}. Provide step-by-step guidance, code examples, and best practices."
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 1500},
                    timeout=15
                )
                data = response.json()
                return {"status": "success", "assistance": data["choices"][0]["message"]["content"]}
            except Exception as e:
                logger.error(f"AI project help failed: {e}")
        
        return {"status": "success", "assistance": "Step-by-step guidance will help you complete the project."}
    
    def complete_course(self, enrollment_id):
        """Complete course and issue certificate."""
        if enrollment_id not in self.enrollments:
            return {"status": "error", "message": "Enrollment not found"}
        
        enrollment = self.enrollments[enrollment_id]
        enrollment["status"] = "completed"
        enrollment["completed_at"] = datetime.now().isoformat()
        
        # Generate certificate
        cert_id = f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        certificate = {
            "certificate_id": cert_id,
            "email": enrollment["email"],
            "course": enrollment["course"],
            "duration": enrollment["duration_weeks"],
            "issued_at": datetime.now().isoformat(),
            "ai_driven": True
        }
        
        self.certificates[cert_id] = certificate
        
        return {"status": "success", "certificate": certificate}

ai_courses = AICourseSystem()
