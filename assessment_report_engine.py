"""
Charvak Assessment Report Engine
Generates and delivers reports for all assessment types
"""
import logging
from datetime import datetime
from typing import Dict, Optional
import secrets

logger = logging.getLogger("charvakit.reports")


class AssessmentReportEngine:
    """Generates assessment reports and delivers to all parties."""
    
    def __init__(self):
        self.reports = []
        logger.info("Assessment Report Engine ready")
    
    def generate_report(self, data: Dict) -> Dict:
        """Generate assessment report and deliver."""
        report_id = f"RPT-{secrets.token_hex(6).upper()}"
        
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
            "verification_id": f"VERIFY-{secrets.token_hex(4).upper()}",
            "generated_at": datetime.now().isoformat()
        }
        
        self.reports.append(report)
        delivery = self._deliver_report(report)
        
        return {
            "status": "success",
            "report_id": report_id,
            "report": report,
            "delivery": delivery,
            "message": "Report generated!"
        }
    
    def _deliver_report(self, report: Dict) -> Dict:
        """Deliver report to candidate and employer."""
        delivery = {"candidate_copy": "not_sent", "employer_copy": "not_sent"}
        
        try:
            from email_engine import email_engine
            subject = f"Your {report['assessment_type']} Assessment Report"
            body = self._format_report(report)
            result = email_engine.send_email(report["candidate_email"], subject, body)
            delivery["candidate_copy"] = "sent" if result["status"] == "success" else "pending_email_config"
        except:
            delivery["candidate_copy"] = "email_not_configured"
        
        if report.get("employer_email"):
            try:
                from email_engine import email_engine
                subject = f"Candidate Report: {report['candidate_name']} - {report['score']}%"
                body = self._format_report(report, for_employer=True)
                result = email_engine.send_email(report["employer_email"], subject, body)
                delivery["employer_copy"] = "sent" if result["status"] == "success" else "pending_email_config"
            except:
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
    
    def get_report(self, report_id: str) -> Dict:
        for report in self.reports:
            if report["report_id"] == report_id:
                return {"status": "success", "report": report}
        return {"status": "error", "message": "Report not found"}
    
    def verify_report(self, verification_id: str) -> Dict:
        for report in self.reports:
            if report["verification_id"] == verification_id:
                return {"status": "success", "verified": True, "report": report}
        return {"status": "error", "verified": False, "message": "Report not found"}
    
    def get_candidate_reports(self, email: str) -> Dict:
        reports = [r for r in self.reports if r["candidate_email"] == email]
        return {"status": "success", "reports": reports, "count": len(reports)}
    
    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "stats": {
                "total_reports": len(self.reports),
                "passed": len([r for r in self.reports if r["passed"]]),
                "average_score": round(sum(r["score"] for r in self.reports) / len(self.reports), 1) if self.reports else 0
            }
        }


assessment_report_engine = AssessmentReportEngine()