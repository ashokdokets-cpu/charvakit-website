"""
Charvak Complete Results & Reporting System
Monitors all assessments, generates reports for every user
"""
import logging
import json
import secrets
import os
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.results_system")

class ResultsReportingSystem:
    def __init__(self):
        self._ensure_tables()
        logger.info("Results & Reporting System ready (DB-backed)")

    def _ensure_tables(self):
        """Idempotent table creation for assessment results."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_assessment_results (
                    result_id        TEXT PRIMARY KEY,
                    email            TEXT NOT NULL,
                    assessment_type  TEXT NOT NULL,
                    assessment_name  TEXT NOT NULL,
                    score            NUMERIC(5,2) NOT NULL,
                    total_questions  INTEGER NOT NULL,
                    correct_answers  INTEGER NOT NULL,
                    percentage       NUMERIC(5,2) NOT NULL,
                    passed           BOOLEAN NOT NULL,
                    details_json     JSONB,
                    completed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_assessment_results_email ON charvak_assessment_results(email)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_assessment_results_type ON charvak_assessment_results(assessment_type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_assessment_results_completed ON charvak_assessment_results(completed_at DESC)")
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"results tables init failed: {e}")


    def record_assessment_result(self, email, assessment_type, assessment_name, score, total_questions, correct_answers, details=None):
        """Record any assessment result. Persists to Postgres."""
        result_id = "RES-" + secrets.token_hex(6).upper()
        percentage = round((correct_answers / total_questions * 100) if total_questions > 0 else 0, 1)
        passed = score >= 60
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_assessment_results
                    (result_id, email, assessment_type, assessment_name,
                     score, total_questions, correct_answers, percentage, passed, details_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            """, (result_id, email, assessment_type, assessment_name,
                  round(score, 2), int(total_questions), int(correct_answers),
                  percentage, passed, json.dumps(details or {})))
            conn.commit()
            cur.close(); conn.close()
            result = {
                "result_id": result_id,
                "email": email,
                "assessment_type": assessment_type,
                "assessment_name": assessment_name,
                "score": round(score, 2),
                "total_questions": int(total_questions),
                "correct_answers": int(correct_answers),
                "percentage": percentage,
                "pass": passed,
                "details": details or {},
                "completed_at": datetime.now().isoformat(),
            }
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error(f"record_assessment_result failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_user_report(self, email):
        """Get complete report for a user."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT result_id, assessment_type, assessment_name, score,
                       total_questions, correct_answers, percentage, passed,
                       details_json, completed_at
                FROM charvak_assessment_results
                WHERE email = %s
                ORDER BY completed_at DESC
            """, (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
            if not rows:
                return {"status": "error", "message": "No results found for this user"}
            results = []
            for r in rows:
                results.append({
                    "result_id": r[0],
                    "assessment_type": r[1],
                    "assessment_name": r[2],
                    "score": float(r[3]),
                    "total_questions": r[4],
                    "correct_answers": r[5],
                    "percentage": float(r[6]),
                    "pass": r[7],
                    "details": r[8] if isinstance(r[8], dict) else {},
                    "completed_at": r[9].isoformat() if r[9] else None,
                })
            total = len(results)
            avg = sum(x["score"] for x in results) / total if total else 0
            passed = sum(1 for x in results if x["pass"])
            return {
                "status": "success",
                "email": email,
                "total_assessments": total,
                "average_score": round(avg, 1),
                "passed": passed,
                "failed": total - passed,
                "results": results,
                "generated_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"get_user_report failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_assessment_report(self, result_id):
        """Get specific assessment report."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT result_id, email, assessment_type, assessment_name, score,
                       total_questions, correct_answers, percentage, passed,
                       details_json, completed_at
                FROM charvak_assessment_results WHERE result_id = %s
            """, (result_id,))
            r = cur.fetchone()
            cur.close(); conn.close()
            if not r:
                return {"status": "error", "message": "Result not found"}
            report = {
                "result_id": r[0],
                "email": r[1],
                "assessment_type": r[2],
                "assessment_name": r[3],
                "score": float(r[4]),
                "total_questions": r[5],
                "correct_answers": r[6],
                "percentage": float(r[7]),
                "pass": r[8],
                "details": r[9] if isinstance(r[9], dict) else {},
                "completed_at": r[10].isoformat() if r[10] else None,
            }
            return {"status": "success", "report": report}
        except Exception as e:
            logger.error(f"get_assessment_report failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_type_report(self, assessment_type):
        """Get report for all users for a specific assessment type."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT result_id, email, assessment_name, score, total_questions,
                       correct_answers, percentage, passed, completed_at
                FROM charvak_assessment_results
                WHERE assessment_type = %s
                ORDER BY completed_at DESC
            """, (assessment_type,))
            rows = cur.fetchall()
            cur.close(); conn.close()
            if not rows:
                return {"status": "error", "message": "No results for this type"}
            results = []
            for r in rows:
                results.append({
                    "result_id": r[0],
                    "email": r[1],
                    "assessment_name": r[2],
                    "score": float(r[3]),
                    "total_questions": r[4],
                    "correct_answers": r[5],
                    "percentage": float(r[6]),
                    "pass": r[7],
                    "completed_at": r[8].isoformat() if r[8] else None,
                })
            total = len(results)
            avg = sum(x["score"] for x in results) / total if total else 0
            passed = sum(1 for x in results if x["pass"])
            return {
                "status": "success",
                "assessment_type": assessment_type,
                "total_attempts": total,
                "average_score": round(avg, 1),
                "passed": passed,
                "failed": total - passed,
                "results": results,
            }
        except Exception as e:
            logger.error(f"get_type_report failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_user_progress(self, email):
        """Get user's progress over time."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT completed_at, assessment_name, score, passed
                FROM charvak_assessment_results
                WHERE email = %s
                ORDER BY completed_at ASC
            """, (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
            if not rows:
                return {"status": "error", "message": "No results found"}
            progress = []
            for r in rows:
                progress.append({
                    "date": r[0].isoformat() if r[0] else None,
                    "assessment": r[1],
                    "score": float(r[2]),
                    "pass": r[3],
                })
            return {"status": "success", "email": email, "progress": progress}
        except Exception as e:
            logger.error(f"get_user_progress failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_placement_readiness(self, email):
        """Calculate overall placement readiness."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT AVG(score), COUNT(*) FROM charvak_assessment_results
                WHERE email = %s
            """, (email,))
            row = cur.fetchone()
            cur.close(); conn.close()
            avg_score = float(row[0]) if row and row[0] else 0
            total = int(row[1]) if row and row[1] else 0
            if total == 0:
                return {"status": "success", "readiness": "Not Started", "score": 0}
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
                "total_assessments": total,
            }
        except Exception as e:
            logger.error(f"get_placement_readiness failed: {e}")
            return {"status": "error", "message": str(e)}


    def generate_detailed_report(self, email):
        """Generate detailed PDF-style report data."""
        report = self.get_user_report(email)
        if report.get("status") != "success":
            return report
        results = report["results"]
        total_q = sum(r["total_questions"] for r in results)
        total_c = sum(r["correct_answers"] for r in results)
        overall = round(total_c / total_q * 100, 1) if total_q > 0 else 0
        return {
            "status": "success",
            "report": {
                "email": email,
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_assessments": len(results),
                    "average_score": round(sum(r["score"] for r in results) / len(results), 1) if results else 0,
                    "total_questions_attempted": total_q,
                    "total_correct": total_c,
                    "overall_accuracy": overall,
                },
                "assessments": results,
                "readiness": self.get_placement_readiness(email),
            },
        }


results_system = ResultsReportingSystem()
