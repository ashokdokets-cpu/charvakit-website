"""
Charvak Interactive AI Tutor
Real-time one-to-one training, hands-on scenarios, adaptive learning
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.ai_tutor")

class InteractiveAITutor:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.sessions = {}
        logger.info(f"Interactive AI Tutor - OpenAI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")
    
    def start_tutoring_session(self, email, course_name, topic, user_level):
        """Start interactive tutoring session."""
        session_id = f"TUTOR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "email": email,
            "course": course_name,
            "topic": topic,
            "user_level": user_level,
            "conversation": [],
            "started_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # AI initiates conversation
        greeting = self._ai_start_conversation(course_name, topic, user_level)
        
        return {
            "status": "success",
            "session_id": session_id,
            "ai_message": greeting
        }
    
    def _ai_start_conversation(self, course_name, topic, user_level):
        """AI starts conversation."""
        if self.openai_api_key:
            try:
                import requests
                prompt = f"Start a tutoring session for {course_name} on {topic} for {user_level} level. Greet the student, explain what they'll learn, and ask a question to gauge their understanding."
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8, "max_tokens": 500},
                    timeout=10
                )
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"AI greeting failed: {e}")
        
        return f"Welcome to {course_name}! Let's learn {topic} together. What do you already know about {topic}?"
    
    def chat_with_tutor(self, session_id, user_message):
        """Real-time chat with AI tutor."""
        if session_id not in self.sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.sessions[session_id]
        session["conversation"].append({"role": "user", "message": user_message})
        
        # AI responds
        ai_response = self._ai_respond(session, user_message)
        session["conversation"].append({"role": "ai", "message": ai_response})
        
        return {"status": "success", "ai_response": ai_response}
    
    def _ai_respond(self, session, user_message):
        """AI generates response based on context."""
        if self.openai_api_key:
            try:
                import requests
                
                # Build context from conversation
                context = "\\n".join([f"{c['role']}: {c['message'][:200]}" for c in session["conversation"][-5:]])
                
                prompt = f"""You are an AI tutor teaching {session['course']} on topic {session['topic']} to a {session['user_level']} student.
                
                Conversation so far:
                {context}
                
                Student says: {user_message}
                
                Teach effectively:
                1. Answer clearly
                2. Give a simple example
                3. Provide a practice exercise
                4. Encourage the student
                5. Keep it under 150 words
                """
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8, "max_tokens": 1000},
                    timeout=15
                )
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"AI response failed: {e}")
        
        return "That's a great question! Let me explain with an example..."
    
    def get_real_scenario(self, session_id):
        """AI generates real-world scenario for practice."""
        if session_id not in self.sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.sessions[session_id]
        
        if self.openai_api_key:
            try:
                import requests
                prompt = f"Create a real-world scenario related to {session['topic']} in {session['course']} for a {session['user_level']} student. Include: scenario description, problem to solve, hints, and expected solution approach."
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8, "max_tokens": 1000},
                    timeout=15
                )
                data = response.json()
                return {"status": "success", "scenario": data["choices"][0]["message"]["content"]}
            except Exception as e:
                logger.error(f"AI scenario failed: {e}")
        
        return {"status": "success", "scenario": f"Real-world scenario for {session['topic']}: Build a simple application that demonstrates this concept."}
    
    def evaluate_answer(self, session_id, user_answer):
        """AI evaluates user's answer and provides feedback."""
        if self.openai_api_key:
            try:
                import requests
                prompt = f"Evaluate this student answer for {self.sessions[session_id]['topic']}: '{user_answer}'. Provide: correctness score (0-100), what's good, what's missing, and improvement suggestions."
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 500},
                    timeout=10
                )
                data = response.json()
                return {"status": "success", "feedback": data["choices"][0]["message"]["content"]}
            except Exception as e:
                logger.error(f"AI evaluation failed: {e}")
        
        return {"status": "success", "feedback": "Good attempt! Here's how to improve..."}

interactive_tutor = InteractiveAITutor()
