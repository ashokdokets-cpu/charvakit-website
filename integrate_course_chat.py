with open('ai_courses.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add chat-based learning to AI courses
addition = '''
    def start_course_chat(self, email, course_name, duration_weeks):
        """Start AI Tutor chat for a specific course."""
        enrollment = self.enroll_student(email, course_name, duration_weeks)
        
        if enrollment["status"] != "success":
            return enrollment
        
        enrollment_id = enrollment["enrollment"]["enrollment_id"]
        curriculum = enrollment["enrollment"]["curriculum"]
        
        # Get first week topic
        first_topic = curriculum.get("weeks", [{}])[0].get("topic", course_name)
        
        # Start AI tutoring session
        from interactive_tutor import interactive_tutor
        session = interactive_tutor.start_tutoring_session(
            email, course_name, first_topic, "beginner"
        )
        
        return {
            "status": "success",
            "enrollment_id": enrollment_id,
            "tutor_session_id": session.get("session_id"),
            "ai_message": session.get("ai_message"),
            "curriculum": curriculum
        }
    
    def get_course_lesson(self, enrollment_id, week_num):
        """Get AI lesson for a specific week of the course."""
        if enrollment_id not in self.enrollments:
            return {"status": "error", "message": "Enrollment not found"}
        
        enrollment = self.enrollments[enrollment_id]
        curriculum = enrollment["curriculum"]
        
        weeks = curriculum.get("weeks", [])
        if week_num > len(weeks):
            return {"status": "error", "message": "Week not found"}
        
        week_data = weeks[week_num - 1]
        
        # Generate AI lesson content
        lesson_content = self._generate_lesson_content(
            enrollment["course"], week_num, week_data.get("topic", "")
        )
        
        return {
            "status": "success",
            "week": week_num,
            "topic": week_data.get("topic"),
            "objectives": week_data.get("objectives", []),
            "lesson": lesson_content,
            "project": week_data.get("project"),
            "assessment": week_data.get("assessment")
        }
    
    def _generate_lesson_content(self, course_name, week_num, topic):
        """Generate lesson content via AI."""
        if self.openai_api_key:
            try:
                import requests
                prompt = f"Create Week {week_num} lesson for {course_name} on {topic}. Include: explanation, example, practice exercise. Keep under 200 words."
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8, "max_tokens": 500},
                    timeout=15
                )
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except:
                pass
        
        return f"Week {week_num} lesson on {topic} for {course_name}."
'''

# Add methods to the class
if 'def start_course_chat' not in content:
    content = content.replace('    def enroll_student', addition + '\n    def enroll_student', 1)
    with open('ai_courses.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Course chat integrated with AI Tutor!')
else:
    print('Already exists')
