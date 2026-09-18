"""
Charvak Assessment Report Engine
Generates and delivers reports for all assessment types
(DB-backed - Session H/1)
"""
import json
import logging
import secrets
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger("charvakit.reports")


class AssessmentReportEngine:
    """Generates assessment reports and delivers to all parties (DB-backed)."""

    def __init__(self):
        self._ensure_tables()
        logger.info("Assessment Report Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_assessment_reports (
                    report_id          TEXT PRIMARY KEY,
                    verification_id    TEXT UNIQUE NOT NULL,
                    assessment_type    TEXT DEFAULT 'general',
                    candidate_name     TEXT,
                    candidate_email    TEXT,
                    employer_email     TEXT DEFAULT '',
                    score              NUMERIC(5,2) DEFAULT 0,
                    passed             BOOLEAN DEFAULT FALSE,
                    skills_tested      JSONB DEFAULT '[]'::jsonb,
                    total_questions    INTEGER DEFAULT 0,
                    correct_answers    INTEGER DEFAULT 0,
                    strengths          JSONB DEFAULT '[]'::jsonb,
                    improvements       JSONB DEFAULT '[]'::jsonb,
                    recommendations    JSONB DEFAULT '[]'::jsonb,
                    generated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_asr_candidate_email ON charvak_assessment_reports(candidate_email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_asr_verification    ON charvak_assessment_reports(verification_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_asr_passed          ON charvak_assessment_reports(passed)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"assessment_report tables init failed: {e}")

    _SELECT_COLS = """report_id, verification_id, assessment_type, candidate_name,
                      candidate_email, employer_email, score, passed,
                      skills_tested, total_questions, correct_answers,
                      strengths, improvements, recommendations, generated_at"""

    @staticmethod
    def _d(x, default):
        if isinstance(x, type(default)) or x is None:
            return x if x is not None else default
        try:
            return json.loads(x)
        except Exception:
            return default

    @classmethod
    def _row_to_report(cls, row) -> Dict:
        if not row:
            return {}
        return {
            "report_id": row[0],
            "verification_id": row[1],
            "assessment_type": row[2],
            "candidate_name": row[3],
            "candidate_email": row[4],
            "employer_email": row[5] or "",
            "score": float(row[6]) if row[6] is not None else 0,
            "passed": bool(row[7]),
            "skills_tested": cls._d(row[8], []),
            "total_questions": row[9],
            "correct_answers": row[10],
            "strengths": cls._d(row[11], []),
            "improvements": cls._d(row[12], []),
            "recommendations": cls._d(row[13], []),
            "generated_at": row[14].isoformat() if hasattr(row[14], "isoformat") else str(row[14]),
        }

    # ============================================================
    # GENERATE
    # ============================================================

    def generate_report(self, data: Dict) -> Dict:
        """Generate assessment report and deliver."""
        report_id = f"RPT-{secrets.token_hex(6).upper()}"
        verification_id = f"VERIFY-{secrets.token_hex(4).upper()}"

        report = {
            "report_id": report_id,
            "assessment_type": data.get("assessment_type", "general"),
            "candidate_name": data.get("candidate_name", "Candidate"),
            "candidate_email": data.get("candidate_email"),
            "employer_email": data.get("employer_email", ""),
            "score": float(data.get("score", 0)),
            "passed": data.get("passed", False),
            "skills_tested": data.get("skills_tested", []),
            "total_questions": data.get("total_questions", 0),
            "correct_answers": data.get("correct_answers", 0),
            "strengths": data.get("strengths", []),
            "improvements": data.get("improvements", []),
            "recommendations": data.get("recommendations", []),
            "verification_id": verification_id,
            "generated_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_assessment_reports (
                    report_id, verification_id, assessment_type, candidate_name,
                    candidate_email, employer_email, score, passed,
                    skills_tested, total_questions, correct_answers,
                    strengths, improvements, recommendations
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                          %s::jsonb, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb)
            ''', (
                report_id, verification_id, report["assessment_type"],
                report["candidate_name"], report["candidate_email"],
                report["employer_email"], report["score"], report["passed"],
                json.dumps(report["skills_tested"]),
                report["total_questions"], report["correct_answers"],
                json.dumps(report["strengths"]),
                json.dumps(report["improvements"]),
                json.dumps(report["recommendations"]),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"generate_report failed: {e}")
            return {"status": "error", "message": "Could not generate report"}

        delivery = self._deliver_report(report)

        return {
            "status": "success",
            "report_id": report_id,
            "report": report,
            "delivery": delivery,
            "message": "Report generated!",
        }

    # ============================================================
    # DELIVERY (email_engine unchanged)
    # ============================================================

    def _deliver_report(self, report: Dict) -> Dict:
        """Deliver report to candidate and employer."""
        delivery = {"candidate_copy": "not_sent", "employer_copy": "not_sent"}

        try:
            from email_engine import email_engine
            subject = f"Your {report['assessment_type']} Assessment Report"
            body = self._format_report(report)
            result = email_engine.send_email(report["candidate_email"], subject, body)
            delivery["candidate_copy"] = "sent" if result["status"] == "success" else "pending_email_config"
        except Exception:
            delivery["candidate_copy"] = "email_not_configured"

        if report.get("employer_email"):
            try:
                from email_engine import email_engine
                subject = f"Candidate Report: {report['candidate_name']} - {report['score']}%"
                body = self._format_report(report, for_employer=True)
                result = email_engine.send_email(report["employer_email"], subject, body)
                delivery["employer_copy"] = "sent" if result["status"] == "success" else "pending_email_config"
            except Exception:
                delivery["employer_copy"] = "email_not_configured"

        return delivery

    def _format_report(self, report: Dict, for_employer: bool = False) -> str:
        """Format report as text."""
        return f"""
CHARVAK ASSESSMENT REPORT
=========================
Report ID: {report['report_id']}
Verification: {report['verification_id']}
Date: {report['generated_at'][:10]}

Candidate: {report['candidate_name']}
Type: {report['assessment_type']}
Score: {report['score']}%
Result: {'PASSED' if report['passed'] else 'NOT PASSED'}

Skills Tested: {", ".join(report.get('skills_tested', []))}
Questions: {report['correct_answers']}/{report['total_questions']} correct

Verify: https://charvakit.com/verify-report/{report['verification_id']}
"""

    # ============================================================
    # READS
    # ============================================================

    def get_report(self, report_id: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(f'SELECT {self._SELECT_COLS} FROM charvak_assessment_reports WHERE report_id = %s', (report_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_report failed: {e}")
            return {"status": "error", "message": "Report not found"}

        if not row:
            return {"status": "error", "message": "Report not found"}
        return {"status": "success", "report": self._row_to_report(row)}

    def verify_report(self, verification_id: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(f'SELECT {self._SELECT_COLS} FROM charvak_assessment_reports WHERE verification_id = %s', (verification_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"verify_report failed: {e}")
            return {"status": "error", "verified": False, "message": "Report not found"}

        if not row:
            return {"status": "error", "verified": False, "message": "Report not found"}
        return {"status": "success", "verified": True, "report": self._row_to_report(row)}

    def get_candidate_reports(self, email: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(f'''
                SELECT {self._SELECT_COLS}
                FROM charvak_assessment_reports
                WHERE candidate_email = %s
                ORDER BY generated_at ASC
            ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_candidate_reports failed: {e}")
            return {"status": "success", "reports": [], "count": 0}

        reports = [self._row_to_report(r) for r in rows]
        return {"status": "success", "reports": reports, "count": len(reports)}

    def get_stats(self) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM charvak_assessment_reports')
            total = int(cur.fetchone()[0] or 0)
            cur.execute('SELECT COUNT(*) FROM charvak_assessment_reports WHERE passed = TRUE')
            passed = int(cur.fetchone()[0] or 0)
            cur.execute('SELECT COALESCE(AVG(score), 0) FROM charvak_assessment_reports')
            avg_score = float(cur.fetchone()[0] or 0)
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "total_reports": total,
                "passed": passed,
                "average_score": round(avg_score, 1) if total else 0,
            },
        }


assessment_report_engine = AssessmentReportEngine()