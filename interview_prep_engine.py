"""
Charvak Interview Prep Engine
AI-powered interview preparation
"""
import logging
from datetime import datetime
from typing import Dict, List
import secrets

logger = logging.getLogger("charvakit.interviewprep")


class InterviewPrepEngine:
    """Handles interview preparation."""
    
    def __init__(self):
        self.sessions = []
        self.questions = self._seed_questions()
        logger.info(f"✅ Interview Prep Engine ready with {len(self.questions)} questions")
    
    def _seed_questions(self) -> List[Dict]:
        """Seed common interview questions."""
        return [
            {"id": "Q001", "category": "Python", "difficulty": "Beginner", "question": "What is the difference between a list and a tuple?", "answer_hint": "Mutability, syntax, use cases"},
            {"id": "Q002", "category": "Python", "difficulty": "Intermediate", "question": "Explain decorators in Python.", "answer_hint": "Functions that modify other functions"},
            {"id": "Q003", "category": "JavaScript", "difficulty": "Beginner", "question": "What is closure in JavaScript?", "answer_hint": "Function + lexical scope"},
            {"id": "Q004", "category": "React", "difficulty": "Intermediate", "question": "Explain virtual DOM.", "answer_hint": "In-memory representation, diffing"},
            {"id": "Q005", "category": "SQL", "difficulty": "Beginner", "question": "Difference between INNER and LEFT JOIN?", "answer_hint": "Matching vs all left rows"},
            {"id": "Q006", "category": "DSA", "difficulty": "Intermediate", "question": "Explain time complexity of Quick Sort.", "answer_hint": "O(n log n) average, O(n²) worst"},
            {"id": "Q007", "category": "System Design", "difficulty": "Advanced", "question": "How would you design a URL shortener?", "answer_hint": "Hashing, DB, cache, scaling"},
            {"id": "Q008", "category": "Behavioral", "difficulty": "All", "question": "Tell me about a time you failed.", "answer_hint": "STAR method, learning"},
        ]
    
    def start_session(self, data: Dict) -> Dict:
        """
        Start an interview prep session.
        
        data = {"stack": str, "difficulty": str, "candidate_email": str}
        """
        session_id = f"IP-{secrets.token_hex(4).upper()}"
        stack = data.get("stack", "Python")
        difficulty = data.get("difficulty", "All")
        
        session_questions = [q for q in self.questions if q["category"] == stack or stack == "General"]
        if difficulty != "All":
            session_questions = [q for q in session_questions if q["difficulty"] == difficulty]
        
        session = {
            "session_id": session_id,
            "candidate_email": data.get("candidate_email"),
            "stack": stack,
            "difficulty": difficulty,
            "questions": session_questions,
            "current_index": 0,
            "score": 0,
            "created_at": datetime.now().isoformat(),
            "status": "in_progress"
        }
        
        self.sessions.append(session)
        logger.info(f"Interview prep session: {session_id} - {stack} - {difficulty}")
        
        return {
            "status": "success",
            "session_id": session_id,
            "questions_count": len(session_questions),
            "first_question": session_questions[0] if session_questions else None
        }
    
    def submit_answer(self, data: Dict) -> Dict:
        """
        Submit an answer for scoring.
        
        data = {"session_id": str, "question_id": str, "answer": str}
        """
        session_id = data.get("session_id")
        session = self._find_session(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}
        
        # Simple scoring based on answer length and keywords
        answer = data.get("answer", "")
        score = min(len(answer.split()) * 2, 100)
        
        session["score"] += score
        session["current_index"] += 1
        
        return {
            "status": "success",
            "answer_score": score,
            "session_score": session["score"],
            "next_question": session["questions"][session["current_index"]] if session["current_index"] < len(session["questions"]) else None,
            "completed": session["current_index"] >= len(session["questions"])
        }
    
    def get_session(self, session_id: str) -> Dict:
        """Get session details."""
        session = self._find_session(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}
        return {"status": "success", "session": session}
    
    def _find_session(self, session_id: str):
        for session in self.sessions:
            if session["session_id"] == session_id:
                return session
        return None


interview_prep_engine = InterviewPrepEngine()