"""
Charvak Enterprise Engine
Complete enterprise career services: benchmarking, pathways, approvals,
appointments, compliance, tiering, resume books, kiosk, surveys
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.enterprise")


class EnterpriseEngine:
    """Complete enterprise career services platform."""
    
    def __init__(self):
        self.salary_data = []
        self.pathways = []
        self.resume_approvals = []
        self.appointments = []
        self.employer_tiers = []
        self.resume_books = []
        self.surveys = []
        self.kiosk_sessions = []
        logger.info("✅ Enterprise Engine ready — 8 modules loaded")
    
    # ============================================================
    # 1. SALARY BENCHMARKING
    # ============================================================
    
    def record_salary(self, data: Dict) -> Dict:
        """
        Record anonymized salary data.
        data = {university, major, company, industry, base_salary, signing_bonus, location, graduation_year}
        """
        salary_id = f"SAL-{secrets.token_hex(4).upper()}"
        
        record = {
            "salary_id": salary_id,
            "university": data.get("university", "Unknown"),
            "major": data.get("major", ""),
            "industry": data.get("industry", ""),
            "base_salary": float(data.get("base_salary", 0)),
            "signing_bonus": float(data.get("signing_bonus", 0)),
            "location": data.get("location", ""),
            "graduation_year": int(data.get("graduation_year", 2026)),
            "recorded_at": datetime.now().isoformat()
        }
        
        self.salary_data.append(record)
        
        return {"status": "success", "salary_id": salary_id, "message": "Salary recorded anonymously"}
    
    def get_salary_benchmarks(self, filters: Dict = None) -> Dict:
        """
        Get anonymized salary benchmarks.
        filters = {university, major, industry, location, graduation_year}
        """
        data = self.salary_data
        
        if filters:
            if filters.get("university"):
                data = [d for d in data if d["university"] == filters["university"]]
            if filters.get("major"):
                data = [d for d in data if filters["major"].lower() in d["major"].lower()]
            if filters.get("industry"):
                data = [d for d in data if filters["industry"].lower() in d["industry"].lower()]
            if filters.get("location"):
                data = [d for d in data if filters["location"].lower() in d["location"].lower()]
        
        if not data:
            return {"status": "success", "count": 0, "message": "No data available"}
        
        salaries = [d["base_salary"] for d in data if d["base_salary"] > 0]
        bonuses = [d["signing_bonus"] for d in data if d["signing_bonus"] > 0]
        
        return {
            "status": "success",
            "count": len(data),
            "benchmarks": {
                "average_base_salary": round(sum(salaries) / len(salaries), 2) if salaries else 0,
                "median_base_salary": round(sorted(salaries)[len(salaries)//2], 2) if salaries else 0,
                "average_signing_bonus": round(sum(bonuses) / len(bonuses), 2) if bonuses else 0,
                "top_industries": self._get_top_industries(data),
                "top_locations": self._get_top_locations(data)
            }
        }
    
    # ============================================================
    # 2. STUDENT PATHWAYS
    # ============================================================
    
    def create_pathway(self, data: Dict) -> Dict:
        """
        Create a career pathway.
        data = {name, description, steps: [{name, description, required}]}
        """
        pathway_id = f"PATH-{secrets.token_hex(4).upper()}"
        
        pathway = {
            "pathway_id": pathway_id,
            "name": data.get("name", "Career Readiness Track"),
            "description": data.get("description", ""),
            "steps": data.get("steps", [
                {"name": "Upload Resume", "required": True},
                {"name": "Take Skill Check", "required": True},
                {"name": "Complete Micro-Internship", "required": False},
                {"name": "Earn Verified Badge", "required": True},
                {"name": "Apply to Jobs", "required": True}
            ]),
            "created_at": datetime.now().isoformat()
        }
        
        self.pathways.append(pathway)
        
        return {"status": "success", "pathway_id": pathway_id, "message": "Pathway created"}
    
    def assign_pathway(self, student_id: str, pathway_id: str) -> Dict:
        """Assign a pathway to a student."""
        for pathway in self.pathways:
            if pathway["pathway_id"] == pathway_id:
                return {
                    "status": "success",
                    "student_id": student_id,
                    "pathway": pathway,
                    "progress": [{"step": s["name"], "completed": False} for s in pathway["steps"]]
                }
        return {"status": "error", "message": "Pathway not found"}
    
    # ============================================================
    # 3. RESUME APPROVAL WORKFLOW
    # ============================================================
    
    def submit_resume_for_review(self, data: Dict) -> Dict:
        """
        Submit resume for approval.
        data = {student_id, student_name, resume_text}
        """
        review_id = f"REV-{secrets.token_hex(4).upper()}"
        
        review = {
            "review_id": review_id,
            "student_id": data.get("student_id"),
            "student_name": data.get("student_name"),
            "resume_text": data.get("resume_text", ""),
            "status": "pending",
            "reviewer_comments": "",
            "submitted_at": datetime.now().isoformat(),
            "reviewed_at": None
        }
        
        self.resume_approvals.append(review)
        
        return {"status": "success", "review_id": review_id, "message": "Resume submitted for review"}
    
    def review_resume(self, review_id: str, decision: str, comments: str = "") -> Dict:
        """
        Review a resume.
        decision = "approve" / "reject" / "request_changes"
        """
        for review in self.resume_approvals:
            if review["review_id"] == review_id:
                review["status"] = decision
                review["reviewer_comments"] = comments
                review["reviewed_at"] = datetime.now().isoformat()
                return {"status": "success", "message": f"Resume {decision}d"}
        return {"status": "error", "message": "Review not found"}
    
    def get_pending_reviews(self) -> Dict:
        """Get all pending resume reviews."""
        pending = [r for r in self.resume_approvals if r["status"] == "pending"]
        return {"status": "success", "pending": pending, "count": len(pending)}
    
    # ============================================================
    # 4. APPOINTMENT BOOKING
    # ============================================================
    
    def create_appointment(self, data: Dict) -> Dict:
        """
        Book an appointment.
        data = {student_id, student_name, advisor_id, date, duration_minutes, reason}
        """
        appointment_id = f"APT-{secrets.token_hex(4).upper()}"
        
        appointment = {
            "appointment_id": appointment_id,
            "student_id": data.get("student_id"),
            "student_name": data.get("student_name"),
            "advisor_id": data.get("advisor_id", "ADVISOR-001"),
            "date": data.get("date"),
            "duration_minutes": int(data.get("duration_minutes", 30)),
            "reason": data.get("reason", "Career Counseling"),
            "status": "booked",
            "created_at": datetime.now().isoformat()
        }
        
        self.appointments.append(appointment)
        
        return {"status": "success", "appointment_id": appointment_id, "message": "Appointment booked"}
    
    def get_appointments(self, advisor_id: str = None) -> Dict:
        """Get appointments."""
        appointments = self.appointments
        if advisor_id:
            appointments = [a for a in appointments if a["advisor_id"] == advisor_id]
        return {"status": "success", "appointments": appointments, "count": len(appointments)}
    
    # ============================================================
    # 5. EMPLOYER TIERING
    # ============================================================
    
    def set_employer_tier(self, data: Dict) -> Dict:
        """
        Set employer tier.
        data = {company_name, tier: "tier1" / "tier2" / "tier3", notes}
        """
        tier_id = f"TIER-{secrets.token_hex(4).upper()}"
        
        tier = {
            "tier_id": tier_id,
            "company_name": data.get("company_name"),
            "tier": data.get("tier", "tier2"),
            "notes": data.get("notes", ""),
            "set_at": datetime.now().isoformat()
        }
        
        self.employer_tiers.append(tier)
        
        return {"status": "success", "tier_id": tier_id, "message": f"{data.get('company_name')} set as {data.get('tier')}"}
    
    def get_employers_by_tier(self, tier: str = None) -> Dict:
        """Get employers by tier."""
        employers = self.employer_tiers
        if tier:
            employers = [e for e in employers if e["tier"] == tier]
        return {"status": "success", "employers": employers, "count": len(employers)}
    
    # ============================================================
    # 6. RESUME BOOKS
    # ============================================================
    
    def create_resume_book(self, data: Dict) -> Dict:
        """
        Create a resume book.
        data = {name, description, student_ids: List[str]}
        """
        book_id = f"BOOK-{secrets.token_hex(4).upper()}"
        
        book = {
            "book_id": book_id,
            "name": data.get("name", "Resume Book"),
            "description": data.get("description", ""),
            "student_ids": data.get("student_ids", []),
            "created_at": datetime.now().isoformat()
        }
        
        self.resume_books.append(book)
        
        return {
            "status": "success",
            "book_id": book_id,
            "message": f"Resume book created with {len(book['student_ids'])} students",
            "download_url": f"https://charvakit.com/api/resume-books/{book_id}/pdf"
        }
    
    # ============================================================
    # 7. SURVEY-ON-LOGIN
    # ============================================================
    
    def create_survey(self, data: Dict) -> Dict:
        """
        Create a survey.
        data = {title, questions: List[str]}
        """
        survey_id = f"SURVEY-{secrets.token_hex(4).upper()}"
        
        survey = {
            "survey_id": survey_id,
            "title": data.get("title", "Outcome Survey"),
            "questions": data.get("questions", [
                "Are you currently employed?",
                "What is your current salary?",
                "Who is your employer?",
                "What is your job title?"
            ]),
            "responses": 0,
            "created_at": datetime.now().isoformat()
        }
        
        self.surveys.append(survey)
        
        return {"status": "success", "survey_id": survey_id, "message": "Survey created"}
    
    def record_survey_response(self, survey_id: str, data: Dict) -> Dict:
        """Record survey response."""
        for survey in self.surveys:
            if survey["survey_id"] == survey_id:
                survey["responses"] += 1
                return {"status": "success", "message": "Response recorded"}
        return {"status": "error", "message": "Survey not found"}
    
    # ============================================================
    # 8. KIOSK MODE
    # ============================================================
    
    def start_kiosk(self, data: Dict) -> Dict:
        """
        Start kiosk mode for event check-in.
        data = {event_id, location}
        """
        kiosk_id = f"KIOSK-{secrets.token_hex(4).upper()}"
        
        kiosk = {
            "kiosk_id": kiosk_id,
            "event_id": data.get("event_id"),
            "location": data.get("location", "Main Entrance"),
            "status": "active",
            "check_ins": 0,
            "started_at": datetime.now().isoformat()
        }
        
        self.kiosk_sessions.append(kiosk)
        
        return {
            "status": "success",
            "kiosk_id": kiosk_id,
            "message": "Kiosk mode started!",
            "check_in_url": f"https://charvakit.com/kiosk/{kiosk_id}"
        }
    
    def kiosk_check_in(self, kiosk_id: str, student_id: str) -> Dict:
        """Check in student via kiosk."""
        for kiosk in self.kiosk_sessions:
            if kiosk["kiosk_id"] == kiosk_id:
                kiosk["check_ins"] += 1
                return {"status": "success", "message": f"Student {student_id} checked in!"}
        return {"status": "error", "message": "Kiosk not found"}
    
    # ============================================================
    # HELPERS
    # ============================================================
    
    def _get_top_industries(self, data: List[Dict], limit: int = 5) -> List[Dict]:
        industry_counts = {}
        for d in data:
            if d["industry"]:
                industry_counts[d["industry"]] = industry_counts.get(d["industry"], 0) + 1
        sorted_ind = sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"industry": i, "count": c} for i, c in sorted_ind[:limit]]
    
    def _get_top_locations(self, data: List[Dict], limit: int = 5) -> List[Dict]:
        loc_counts = {}
        for d in data:
            if d["location"]:
                loc_counts[d["location"]] = loc_counts.get(d["location"], 0) + 1
        sorted_loc = sorted(loc_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"location": l, "count": c} for l, c in sorted_loc[:limit]]
    
    def get_stats(self) -> Dict:
        """Get enterprise engine statistics."""
        return {
            "status": "success",
            "stats": {
                "salary_records": len(self.salary_data),
                "pathways": len(self.pathways),
                "pending_resume_reviews": len([r for r in self.resume_approvals if r["status"] == "pending"]),
                "appointments": len(self.appointments),
                "employer_tiers": len(self.employer_tiers),
                "resume_books": len(self.resume_books),
                "surveys": len(self.surveys),
                "active_kiosks": len([k for k in self.kiosk_sessions if k["status"] == "active"])
            }
        }


enterprise_engine = EnterpriseEngine()