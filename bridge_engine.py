"""
Charvak Bridge Engine
5-step assessment journey, radar chart data, revenue calculator
Integrates with existing engines without breaking
"""
import logging
from datetime import datetime
from typing import Dict, List
import secrets

logger = logging.getLogger("charvakit.bridge")


class BridgeEngine:
    """5-step journey: Diagnose → Measure → Bridge → Match → Monetize."""
    
    CATEGORIES = [
        {"key": "comm", "label": "Communication"},
        {"key": "prob", "label": "Problem Solving"},
        {"key": "tech", "label": "Technical Execution"},
        {"key": "dom", "label": "Domain Knowledge"},
        {"key": "adapt", "label": "Adaptability"},
    ]
    
    THRESHOLD = 75
    
    QUESTIONS = [
        {"id": "comm", "prompt": "A client emails asking for an update on a delayed project. What's your first move?",
         "options": ["Wait for full solution", "Forward to manager", "Reply immediately with revised timeline"],
         "scores": [40, 55, 95]},
        {"id": "prob", "prompt": "Code passes sample tests but fails hidden tests. What do you do?",
         "options": ["Ask for help", "Rewrite everything", "Find edge cases and test"],
         "scores": [40, 55, 95]},
        {"id": "tech", "prompt": "Fixing a bug in unfamiliar codebase. Your approach?",
         "options": ["Random fixes", "Rewrite module", "Trace stack + reproduce locally"],
         "scores": [40, 60, 95]},
        {"id": "dom", "prompt": "Stakeholder uses an unfamiliar industry term. What do you do?",
         "options": ["Nod and move on", "Look it up later", "Ask them directly"],
         "scores": [40, 65, 90]},
        {"id": "adapt", "prompt": "Team switches tools mid-project. How do you respond?",
         "options": ["Push back", "Complain but comply", "Learn new tool quickly"],
         "scores": [40, 55, 95]},
    ]
    
    def __init__(self):
        self.sessions = []
        logger.info("Bridge Engine ready")
    
    def start_journey(self, data: Dict = None) -> Dict:
        """Start 5-step assessment journey."""
        session_id = f"BRIDGE-{secrets.token_hex(4).upper()}"
        session = {
            "session_id": session_id,
            "current_step": 1,
            "answers": {},
            "scores": {},
            "readiness": 0,
            "started_at": datetime.now().isoformat()
        }
        self.sessions.append(session)
        return {
            "status": "success",
            "session_id": session_id,
            "steps": ["diagnose", "measure", "bridge", "match", "monetize"],
            "current_step": 1,
            "first_question": self.QUESTIONS[0]
        }
    
    def submit_answer(self, data: Dict) -> Dict:
        """Submit answer and get next question."""
        session_id = data.get("session_id")
        question_id = data.get("question_id")
        answer_index = data.get("answer_index", 0)
        
        session = self._find_session(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}
        
        # Find question
        question = next((q for q in self.QUESTIONS if q["id"] == question_id), None)
        if not question:
            return {"status": "error", "message": "Question not found"}
        
        # Save score
        score = question["scores"][answer_index] if 0 <= answer_index < len(question["scores"]) else 0
        session["scores"][question_id] = score
        
        # Check if complete
        answered = len(session["scores"])
        if answered >= len(self.QUESTIONS):
            session["current_step"] = 2
            session["readiness"] = self._calculate_readiness(session["scores"])
            return {
                "status": "success",
                "complete": True,
                "readiness": session["readiness"],
                "next_step": "measure",
                "radar_data": self.get_radar_data(session["scores"])
            }
        
        # Get next question
        next_question = self.QUESTIONS[answered]
        return {
            "status": "success",
            "complete": False,
            "answered": answered,
            "total": len(self.QUESTIONS),
            "next_question": next_question
        }
    
    def _calculate_readiness(self, scores: Dict) -> int:
        """Calculate average readiness score."""
        if not scores:
            return 0
        return round(sum(scores.values()) / len(scores))
    
    def get_radar_data(self, scores: Dict) -> Dict:
        """Generate radar chart data."""
        return {
            "status": "success",
            "threshold": self.THRESHOLD,
            "radar": [
                {"category": c["label"], "score": scores.get(c["key"], 0), "threshold": self.THRESHOLD}
                for c in self.CATEGORIES
            ],
            "gaps": [
                {"category": c["label"], "score": scores.get(c["key"], 0),
                 "gap": max(0, self.THRESHOLD - scores.get(c["key"], 0))}
                for c in self.CATEGORIES
            ]
        }
    
    def get_learning_path(self, scores: Dict) -> Dict:
        """Generate learning path based on gaps."""
        modules = {
            "comm": {"title": "Client Communication Under Pressure", "duration": "2 hrs"},
            "prob": {"title": "Debugging Ambiguous Failures", "duration": "3 hrs"},
            "tech": {"title": "Reproduce, Isolate, Fix", "duration": "4 hrs"},
            "dom": {"title": "Industry Vocabulary Sprints", "duration": "1 hr"},
            "adapt": {"title": "Tool-Switch Fire Drill", "duration": "1.5 hrs"},
        }
        
        gaps = [
            {"category": c["key"], "label": c["label"],
             "gap": max(0, self.THRESHOLD - scores.get(c["key"], 0)),
             "module": modules.get(c["key"])}
            for c in self.CATEGORIES
            if max(0, self.THRESHOLD - scores.get(c["key"], 0)) > 0
        ]
        
        gaps.sort(key=lambda g: g["gap"], reverse=True)
        
        return {"status": "success", "learning_path": gaps, "total_modules": len(gaps)}
    
    def calculate_revenue(self, data: Dict) -> Dict:
        """Calculate 4 revenue streams with ISA model."""
        students = int(data.get("students", 1000))
        placement_rate = float(data.get("placement_rate", 45))
        avg_salary = float(data.get("avg_salary", 600000))
        isa_percent = float(data.get("isa_percent", 12))
        isa_months = int(data.get("isa_months", 24))
        
        placed = round(students * placement_rate / 100)
        isa_revenue = round(placed * avg_salary * isa_percent / 100 * isa_months / 12)
        employer_partners = max(4, round(students / 50))
        corp_subs = employer_partners * 300000
        college_partners = max(2, round(students / 200))
        licensing = college_partners * 500000
        premium_students = round(students * 0.2)
        premium = premium_students * 4999
        total = isa_revenue + corp_subs + licensing + premium
        
        return {
            "status": "success",
            "revenue_streams": {
                "isa": {"label": "ISA Revenue", "amount": isa_revenue, "detail": f"{placed} placements × {isa_percent}% × {isa_months}mo"},
                "corporate": {"label": "Corporate Subscriptions", "amount": corp_subs, "detail": f"{employer_partners} partners × ₹3L/yr"},
                "licensing": {"label": "College Licensing", "amount": licensing, "detail": f"{college_partners} licenses × ₹5L/yr"},
                "premium": {"label": "Premium Tier", "amount": premium, "detail": f"{premium_students} students × ₹4,999"}
            },
            "total": total,
            "placed_students": placed,
            "per_student": round(total / students, 2) if students > 0 else 0
        }
    
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
                "total_questions": len(self.QUESTIONS),
                "categories": len(self.CATEGORIES)
            }
        }


bridge_engine = BridgeEngine()