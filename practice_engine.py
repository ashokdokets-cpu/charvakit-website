"""
Practice Mode Engine - Session 118
Generates low-stakes practice questions and tracks progress.
"""
import os
import json
import secrets
import logging
from datetime import datetime, timezone
from database import db

logger = logging.getLogger("charvakit.practice")

class PracticeEngine:
    def generate_daily_drill(self, role: str, topic: str) -> list:
        """Generate 5 practice questions for a specific role/topic."""
        # In a full build, this calls OpenAI. For now, we mock the structure.
        questions = []
        for i in range(5):
            questions.append({
                "question_id": f"Q-{secrets.token_hex(3)}",
                "text": f"Practice question {i+1} for {role} - {topic}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0 # Index of the correct option
            })
        return questions

    def record_attempt(self, student_id: str, role: str, topic: str, total: int, correct: int, time_spent: int):
        """Save the practice results to the database."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            attempt_id = f"PRAC-{secrets.token_hex(4).upper()}"
            cur.execute("""
                INSERT INTO charvak_practice_attempts 
                (attempt_id, student_id, role, topic, questions_total, questions_correct, time_spent_seconds)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (attempt_id, student_id, role, topic, total, correct, time_spent))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to record practice attempt: {e}")
            return False
        finally:
            cur.close()
            conn.close()

    def get_student_stats(self, student_id: str) -> dict:
        """Get overall practice stats for the dashboard."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            # Total questions answered
            cur.execute("""
                SELECT COALESCE(SUM(questions_total), 0), COALESCE(SUM(questions_correct), 0)
                FROM charvak_practice_attempts WHERE student_id = %s
            """, (student_id,))
            total_q, correct_q = cur.fetchone()
            
            accuracy = int((correct_q / total_q * 100)) if total_q > 0 else 0
            
            return {
                "total_questions": total_q,
                "correct_questions": correct_q,
                "accuracy": accuracy
            }
        finally:
            cur.close()
            conn.close()

practice_engine = PracticeEngine()