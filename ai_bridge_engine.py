"""
Charvak AI Bridge Engine
AI-powered personalized assessment with monetization
Uses GPT-4o-mini for question generation and answer evaluation
"""
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.aibridge")

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except:
    OPENAI_AVAILABLE = False

import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


class AIBridgeEngine:
    """AI-powered career assessment with personalized feedback."""
    
    ROLES = ["Software Developer", "Data Scientist", "UI/UX Designer", "Marketing Specialist", "Business Analyst", "DevOps Engineer"]
    INDUSTRIES = ["IT/Tech", "Finance", "Healthcare", "E-commerce", "Manufacturing", "Education"]
    LEVELS = ["Fresher", "Mid-Level", "Senior"]
    
    def __init__(self):
        self.sessions = []
        self.premium_reports = []
        self.revenue = 0
        logger.info(f"AI Bridge Engine ready | OpenAI: {'Available' if OPENAI_AVAILABLE and OPENAI_API_KEY else 'Not Configured'}")
    
    def start_ai_assessment(self, data: Dict) -> Dict:
        """
        Start AI-powered assessment.
        data = {role, industry, experience_level, name, email}
        """
        session_id = f"AIB-{secrets.token_hex(4).upper()}"
        
        role = data.get("role", "Software Developer")
        industry = data.get("industry", "IT/Tech")
        level = data.get("experience_level", "Fresher")
        
        # Generate AI questions
        questions = self._generate_ai_questions(role, industry, level)
        
        session = {
            "session_id": session_id,
            "role": role,
            "industry": industry,
            "level": level,
            "name": data.get("name", "Candidate"),
            "email": data.get("email", ""),
            "questions": questions,
            "answers": [],
            "current_question": 0,
            "started_at": datetime.now().isoformat()
        }
        
        self.sessions.append(session)
        
        return {
            "status": "success",
            "session_id": session_id,
            "questions_count": len(questions),
            "first_question": questions[0] if questions else None,
            "message": f"AI assessment started for {role} ({level}) in {industry}"
        }
    
    def _generate_ai_questions(self, role: str, industry: str, level: str) -> List[Dict]:
        """Generate role-specific questions using AI or fallback."""
        
        # Fallback questions if AI not available
        fallback = [
            {"id": "q1", "prompt": f"Describe a real-world {role} challenge you've faced and how you solved it.", "type": "open_ended"},
            {"id": "q2", "prompt": f"What tools and technologies do you use daily as a {role}?", "type": "open_ended"},
            {"id": "q3", "prompt": f"How do you handle feedback and criticism in your {role} work?", "type": "open_ended"},
            {"id": "q4", "prompt": f"Describe a time you had to learn something new quickly for your {role} role.", "type": "open_ended"},
            {"id": "q5", "prompt": f"What's your approach to collaborating with team members in {industry}?", "type": "open_ended"},
        ]
        
        # Try AI generation
        if OPENAI_AVAILABLE and OPENAI_API_KEY:
            try:
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                prompt = f"""Generate 5 open-ended scenario questions for a {level} {role} in {industry}.
                Return JSON array: [{{"id":"q1","prompt":"question text","type":"open_ended"}}]
                Questions should assess real skills, not trivia."""
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                
                content = response.choices[0].message.content
                questions = json.loads(content)
                return questions
            except Exception as e:
                logger.error(f"AI question generation failed: {e}")
        
        return fallback
    
    def submit_ai_answer(self, data: Dict) -> Dict:
        """
        Submit an open-ended answer.
        data = {session_id, question_id, answer_text}
        """
        session_id = data.get("session_id")
        session = self._find_session(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}
        
        answer = {
            "question_id": data.get("question_id"),
            "answer_text": data.get("answer_text", ""),
            "submitted_at": datetime.now().isoformat()
        }
        session["answers"].append(answer)
        
        # Check if complete
        if len(session["answers"]) >= len(session["questions"]):
            return self._generate_report(session)
        
        # Next question
        next_index = len(session["answers"])
        return {
            "status": "success",
            "complete": False,
            "answered": len(session["answers"]),
            "total": len(session["questions"]),
            "next_question": session["questions"][next_index]
        }
    
    def _generate_report(self, session: Dict) -> Dict:
        """Generate AI-powered personalized report."""
        
        # AI evaluation
        if OPENAI_AVAILABLE and OPENAI_API_KEY:
            try:
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                answers_text = "\n".join([f"Q: {a['question_id']}\nA: {a['answer_text']}" for a in session["answers"]])
                
                prompt = f"""Evaluate these assessment answers for a {session['level']} {session['role']} in {session['industry']}.
                
                {answers_text}
                
                Return JSON:
                {{"score": 0-100, "strengths": [3 items], "weaknesses": [3 items], "learning_path": [3 recommendations], "job_recommendations": [3 roles]}}"""
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=600,
                    temperature=0.5
                )
                
                report = json.loads(response.choices[0].message.content)
                report["session_id"] = session["session_id"]
                report["generated_at"] = datetime.now().isoformat()
                report["ai_generated"] = True
                
                session["report"] = report
                
                return {
                    "status": "success",
                    "complete": True,
                    "report": report,
                    "premium_available": True,
                    "premium_price": 99,
                    "message": "AI assessment complete! Upgrade for full report."
                }
            except Exception as e:
                logger.error(f"AI report generation failed: {e}")
        
        # Fallback report
        report = {
            "session_id": session["session_id"],
            "score": 72,
            "strengths": ["Good communication", "Practical approach", "Willingness to learn"],
            "weaknesses": ["Need more hands-on experience", "Could improve technical depth"],
            "learning_path": ["Complete 2 micro-internships", "Take advanced courses", "Build portfolio projects"],
            "job_recommendations": [session["role"], f"Junior {session['role']}"],
            "generated_at": datetime.now().isoformat(),
            "ai_generated": False
        }
        
        session["report"] = report
        
        return {
            "status": "success",
            "complete": True,
            "report": report,
            "premium_available": True,
            "premium_price": 99,
            "message": "Assessment complete! Upgrade for full report."
        }
    
    def get_premium_report(self, session_id: str) -> Dict:
        """Get premium report (monetized)."""
        session = self._find_session(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}
        
        premium_id = f"PREM-{secrets.token_hex(4).upper()}"
        
        premium_report = {
            "premium_id": premium_id,
            "session_id": session_id,
            "report": session.get("report", {}),
            "detailed_feedback": self._generate_detailed_feedback(session),
            "learning_path": session.get("report", {}).get("learning_path", []),
            "badge_issued": True,
            "price": 99,
            "purchased_at": datetime.now().isoformat()
        }
        
        self.premium_reports.append(premium_report)
        self.revenue += 99
        
        return {
            "status": "success",
            "premium_report": premium_report,
            "message": "Premium report unlocked!",
            "revenue_earned": 99
        }
    
    def _generate_detailed_feedback(self, session: Dict) -> str:
        """Generate detailed feedback."""
        return f"Based on your answers, you demonstrate solid potential as a {session['level']} {session['role']}. Focus on building real project experience and continuous learning."
    
    def _find_session(self, session_id: str):
        for session in self.sessions:
            if session["session_id"] == session_id:
                return session
        return None
    
    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "stats": {
                "total_sessions": len(self.sessions),
                "premium_reports": len(self.premium_reports),
                "total_revenue": self.revenue,
                "openai_available": OPENAI_AVAILABLE and bool(OPENAI_API_KEY)
            }
        }


ai_bridge_engine = AIBridgeEngine()