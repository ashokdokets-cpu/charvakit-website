"""
Charvak Complete Results & Reporting System
Monitors all assessments, generates reports for every user
"""
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.results_system")

class ResultsReportingSystem:
    def __init__(self):
        self.user_results = {}
        self.assessment_history = {}
        logger.info("Results & Reporting System ready")
    
    def record_assessment_result(self, email, assessment_type, assessment_name, score, total_questions, correct_answers, details=None):
        """Record any assessment result."""
        result_id = f"RES-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        result = {
            "result_id": result_id,
            "email": email,
            "assessment_type": assessment_type,  # versant, mcq, company_mock
            "assessment_name": assessment_name,  # TCS Mock, MCQ Aptitude, etc.
            "score": score,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "percentage": round((correct_answers / total_questions * 100) if total_questions > 0 else 0, 1),
            "pass": score >= 60,
            "details": details or {},
            "completed_at": datetime.now().isoformat()
        }
        
        # Store by user
        if email not in self.user_results:
            self.user_results[email] = []
        self.user_results[email].append(result)
        
        # Store by assessment type
        if assessment_type not in self.assessment_history:
            self.assessment_history[assessment_type] = []
        self.assessment_history[assessment_type].append(result)
        
        return {"status": "success", "result": result}
    
    def get_user_report(self, email):
        """Get complete report for a user."""
        if email not in self.user_results:
            return {"status": "error", "message": "No results found for this user"}
        
        results = self.user_results[email]
        
        total_assessments = len(results)
        average_score = sum(r["score"] for r in results) / total_assessments if total_assessments > 0 else 0
        passed = sum(1 for r in results if r["pass"])
        
        return {
            "status": "success",
            "email": email,
            "total_assessments": total_assessments,
            "average_score": round(average_score, 1),
            "passed": passed,
            "failed": total_assessments - passed,
            "results": results,
            "generated_at": datetime.now().isoformat()
        }
    
    def get_assessment_report(self, result_id):
        """Get specific assessment report."""
        for email, results in self.user_results.items():
            for result in results:
                if result["result_id"] == result_id:
                    return {"status": "success", "report": result}
        return {"status": "error", "message": "Result not found"}
    
    def get_type_report(self, assessment_type):
        """Get report for all users for a specific assessment type."""
        if assessment_type not in self.assessment_history:
            return {"status": "error", "message": "No results for this type"}
        
        results = self.assessment_history[assessment_type]
        total = len(results)
        avg_score = sum(r["score"] for r in results) / total if total > 0 else 0
        passed = sum(1 for r in results if r["pass"])
        
        return {
            "status": "success",
            "assessment_type": assessment_type,
            "total_attempts": total,
            "average_score": round(avg_score, 1),
            "passed": passed,
            "failed": total - passed,
            "results": results
        }
    
    def get_user_progress(self, email):
        """Get user's progress over time."""
        if email not in self.user_results:
            return {"status": "error", "message": "No results found"}
        
        results = self.user_results[email]
        progress = []
        
        for r in results:
            progress.append({
                "date": r["completed_at"],
                "assessment": r["assessment_name"],
                "score": r["score"],
                "pass": r["pass"]
            })
        
        return {"status": "success", "email": email, "progress": progress}
    
    def get_placement_readiness(self, email):
        """Calculate overall placement readiness."""
        if email not in self.user_results:
            return {"status": "success", "readiness": "Not Started", "score": 0}
        
        results = self.user_results[email]
        avg_score = sum(r["score"] for r in results) / len(results) if results else 0
        
        if avg_score >= 80:
            readiness = "🎯 Placement Ready"
        elif avg_score >= 65:
            readiness = "📈 Almost Ready"
        elif avg_score >= 50:
            readiness = "📚 In Progress"
        else:
            readiness = "💪 Needs Practice"
        
        return {
            "status": "success",
            "email": email,
            "average_score": round(avg_score, 1),
            "readiness": readiness,
            "total_assessments": len(results)
        }
    
    def generate_detailed_report(self, email):
        """Generate detailed PDF-style report data."""
        if email not in self.user_results:
            return {"status": "error", "message": "No results found"}
        
        results = self.user_results[email]
        
        report = {
            "email": email,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_assessments": len(results),
                "average_score": round(sum(r["score"] for r in results) / len(results), 1),
                "total_questions_attempted": sum(r["total_questions"] for r in results),
                "total_correct": sum(r["correct_answers"] for r in results),
                "overall_accuracy": round(sum(r["correct_answers"] for r in results) / sum(r["total_questions"] for r in results) * 100, 1) if results else 0
            },
            "assessments": results,
            "readiness": self.get_placement_readiness(email)
        }
        
        return {"status": "success", "report": report}

results_system = ResultsReportingSystem()
