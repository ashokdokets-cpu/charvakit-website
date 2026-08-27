"""
Charvak Exam Analytics Engine
Tracks performance, identifies weak/strong areas, provides AI advice
"""
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger("charvakit.exam_analytics")

class ExamAnalyticsEngine:
    def __init__(self):
        self.user_performance = {}
        self.user_history = {}
        logger.info("Exam Analytics Engine ready")
    
    def record_answer(self, email: str, exam_id: str, topic: str, question_id: int, correct: bool, time_taken: int) -> Dict:
        """Record user answer."""
        if email not in self.user_performance:
            self.user_performance[email] = {}
        
        key = f"{exam_id}_{topic}"
        if key not in self.user_performance[email]:
            self.user_performance[email][key] = {
                "total": 0,
                "correct": 0,
                "wrong": 0,
                "accuracy": 0,
                "avg_time": 0
            }
        
        perf = self.user_performance[email][key]
        perf["total"] += 1
        if correct:
            perf["correct"] += 1
        else:
            perf["wrong"] += 1
        perf["accuracy"] = round((perf["correct"] / perf["total"]) * 100, 2)
        perf["avg_time"] = round(((perf["avg_time"] * (perf["total"] - 1)) + time_taken) / perf["total"], 2)
        
        # Track history
        if email not in self.user_history:
            self.user_history[email] = []
        self.user_history[email].append({
            "exam_id": exam_id,
            "topic": topic,
            "correct": correct,
            "time_taken": time_taken,
            "timestamp": datetime.now().isoformat()
        })
        
        return {"status": "success", "performance": perf}
    
    def get_analytics(self, email: str) -> Dict:
        """Get complete analytics for user."""
        if email not in self.user_performance:
            return {"status": "success", "message": "No data yet", "analytics": {}}
        
        perf = self.user_performance[email]
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for key, data in perf.items():
            if data["accuracy"] >= 70:
                strengths.append({"topic": key, "accuracy": data["accuracy"]})
            elif data["accuracy"] < 50:
                weaknesses.append({"topic": key, "accuracy": data["accuracy"]})
        
        # AI Advice
        advice = []
        if weaknesses:
            advice.append(f"Focus on improving: {', '.join(w['topic'] for w in weaknesses[:3])}")
        if strengths:
            advice.append(f"Strong areas: {', '.join(s['topic'] for s in strengths[:3])}")
        advice.append("Practice 30 minutes daily for best results")
        advice.append("Take mock tests weekly to track improvement")
        
        return {
            "status": "success",
            "analytics": {
                "total_questions": sum(d["total"] for d in perf.values()),
                "total_correct": sum(d["correct"] for d in perf.values()),
                "overall_accuracy": round(sum(d["correct"] for d in perf.values()) / max(sum(d["total"] for d in perf.values()), 1) * 100, 2),
                "strengths": strengths,
                "weaknesses": weaknesses,
                "ai_advice": advice,
                "topics": perf
            }
        }
    
    def get_improvement(self, email: str) -> Dict:
        """Track improvement over time."""
        if email not in self.user_history:
            return {"status": "success", "improvement": []}
        
        history = self.user_history[email]
        
        # Group by date
        daily = {}
        for entry in history:
            date = entry["timestamp"][:10]
            if date not in daily:
                daily[date] = {"total": 0, "correct": 0}
            daily[date]["total"] += 1
            if entry["correct"]:
                daily[date]["correct"] += 1
        
        improvement = [
            {"date": date, "accuracy": round((data["correct"] / data["total"]) * 100, 2)}
            for date, data in sorted(daily.items())
        ]
        
        return {"status": "success", "improvement": improvement}

exam_analytics_engine = ExamAnalyticsEngine()