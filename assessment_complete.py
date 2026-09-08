"""
Charvak Complete Assessment System
Answer tracking, auto-scoring, results generation
"""
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.assessment_complete")

class CompleteAssessmentSystem:
    def __init__(self):
        self.assessments = {}
        self.results = {}
        logger.info("Complete Assessment System ready")
    
    def start_assessment(self, email, assessment_type):
        """Start a new assessment session."""
        assessment_id = f"ASMT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.assessments[assessment_id] = {
            "assessment_id": assessment_id,
            "email": email,
            "type": assessment_type,
            "started_at": datetime.now().isoformat(),
            "answers": [],
            "status": "in_progress"
        }
        
        return {"status": "success", "assessment_id": assessment_id}
    
    def submit_answer(self, assessment_id, question_id, answer):
        """Submit an answer for tracking."""
        if assessment_id not in self.assessments:
            return {"status": "error", "message": "Assessment not found"}
        
        self.assessments[assessment_id]["answers"].append({
            "question_id": question_id,
            "answer": answer,
            "submitted_at": datetime.now().isoformat()
        })
        
        return {"status": "success", "total_answers": len(self.assessments[assessment_id]["answers"])}
    
    def complete_assessment(self, assessment_id):
        """Complete assessment and generate results."""
        if assessment_id not in self.assessments:
            return {"status": "error", "message": "Assessment not found"}
        
        assessment = self.assessments[assessment_id]
        assessment["status"] = "completed"
        assessment["completed_at"] = datetime.now().isoformat()
        
        # Generate results
        results = self._generate_results(assessment)
        self.results[assessment_id] = results
        
        return {"status": "success", "results": results}
    
    def _generate_results(self, assessment):
        """Generate assessment results."""
        answers = assessment["answers"]
        
        # Calculate score (simplified - in production, use AI scoring)
        total_questions = len(answers)
        correct_answers = sum(1 for a in answers if a.get("is_correct", False))
        score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Generate CEFR level (for Versant)
        cefr_level = self._get_cefr_level(score)
        
        return {
            "assessment_id": assessment["assessment_id"],
            "email": assessment["email"],
            "type": assessment["type"],
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "score": round(score, 1),
            "cefr_level": cefr_level,
            "answers": answers,
            "generated_at": datetime.now().isoformat()
        }
    
    def _get_cefr_level(self, score):
        """Map score to CEFR level."""
        if score >= 90: return "C2 (Mastery)"
        elif score >= 75: return "C1 (Advanced)"
        elif score >= 60: return "B2 (Upper Intermediate)"
        elif score >= 45: return "B1 (Intermediate)"
        elif score >= 30: return "A2 (Elementary)"
        else: return "A1 (Beginner)"
    
    def get_results(self, assessment_id):
        """Get assessment results."""
        if assessment_id not in self.results:
            return {"status": "error", "message": "Results not found"}
        return {"status": "success", "results": self.results[assessment_id]}
    
    def get_user_results(self, email):
        """Get all results for a user."""
        user_results = [r for r in self.results.values() if r["email"] == email]
        return {"status": "success", "total": len(user_results), "results": user_results}

assessment_system = CompleteAssessmentSystem()
