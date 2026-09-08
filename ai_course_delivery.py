"""
Charvak Enhanced AI Course Delivery
Multiple engagement models: Text, Interactive, Project-based, Assessment
"""
import logging
import json
import os
from datetime import datetime, timedelta

logger = logging.getLogger("charvakit.ai_delivery")

class AICourseDelivery:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        logger.info(f"AI Course Delivery - OpenAI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")
    
    def get_course_plan(self, course_name, duration_weeks):
        """AI generates complete course plan with delivery model."""
        if self.openai_api_key:
            plan = self._ai_generate_plan(course_name, duration_weeks)
            if plan:
                return plan
        
        return self._fallback_plan(course_name, duration_weeks)
    
    def _ai_generate_plan(self, course_name, duration_weeks):
        """AI generates detailed course plan."""
        try:
            import requests
            prompt = f"""Create a {duration_weeks}-week course plan for {course_name}.
            For EACH week provide:
            1. Week number and topic
            2. Learning objectives (3-5)
            3. Lesson content type (text/video/interactive)
            4. Code examples (if applicable)
            5. Practice exercises (3-5)
            6. Real-world project task
            7. Assessment/quiz
            8. Estimated hours
            
            Also provide:
            - Overall course structure
            - Final capstone project
            - Certification criteria
            
            Return JSON."""
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8, "max_tokens": 4000},
                timeout=25
            )
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger.error(f"AI plan failed: {e}")
        return None
    
    def _fallback_plan(self, course_name, duration_weeks):
        """Fallback plan."""
        weeks = []
        for i in range(1, duration_weeks + 1):
            weeks.append({
                "week": i,
                "topic": f"{course_name} - Week {i}",
                "objectives": [f"Learn concept {i}", f"Practice {i}", f"Apply {i}"],
                "content_type": "text + interactive",
                "examples": [f"Example {i}.1", f"Example {i}.2"],
                "exercises": [f"Exercise {i}.1", f"Exercise {i}.2", f"Exercise {i}.3"],
                "project": f"Build mini-project {i}",
                "assessment": f"Quiz {i}",
                "hours": 5
            })
        
        return {
            "course": course_name,
            "duration_weeks": duration_weeks,
            "weeks": weeks,
            "capstone_project": f"Build complete {course_name} project",
            "certification_criteria": "Complete all weeks + capstone project"
        }
    
    def get_weekly_lesson(self, course_name, week_num, topic):
        """AI generates complete weekly lesson."""
        if self.openai_api_key:
            lesson = self._ai_generate_lesson(course_name, week_num, topic)
            if lesson:
                return lesson
        
        return {
            "week": week_num,
            "topic": topic,
            "lesson_text": f"Comprehensive lesson on {topic} for {course_name} Week {week_num}",
            "code_examples": ["// Example code here"],
            "exercises": ["Exercise 1", "Exercise 2", "Exercise 3"],
            "project": f"Week {week_num} Project",
            "quiz": [
                {"question": f"Question 1 on {topic}", "options": ["A", "B", "C", "D"], "correct": 0}
            ]
        }
    
    def _ai_generate_lesson(self, course_name, week_num, topic):
        """AI generates complete lesson."""
        try:
            import requests
            prompt = f"""Generate Week {week_num} lesson for {course_name} on topic: {topic}.
            Include:
            1. Lesson explanation (detailed)
            2. Code examples
            3. Practice exercises
            4. Project task
            5. Quiz questions
            
            Return JSON."""
            
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
            logger.error(f"AI lesson failed: {e}")
        return None
    
    def get_project_guidance(self, course_name, project_description):
        """AI provides project guidance."""
        if self.openai_api_key:
            try:
                import requests
                prompt = f"Provide step-by-step guidance for {project_description} as part of {course_name} course. Include approach, steps, code snippets, and best practices."
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 2000},
                    timeout=15
                )
                data = response.json()
                return {"status": "success", "guidance": data["choices"][0]["message"]["content"]}
            except Exception as e:
                logger.error(f"AI guidance failed: {e}")
        
        return {"status": "success", "guidance": "Step-by-step guidance for your project."}

ai_delivery = AICourseDelivery()
