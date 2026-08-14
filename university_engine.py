"""
Charvak University Engine
University admin portal + first-destination outcome reporting
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.university")


class UniversityEngine:
    """Handles university partnerships and outcome reporting."""
    
    def __init__(self):
        self.universities = []
        self.students = []
        self.outcomes = []
        logger.info("✅ University Engine ready")
    
    def register_university(self, data: Dict) -> Dict:
        """
        Register a university.
        data = {"name": str, "admin_email": str, "location": str, "type": str}
        """
        university_id = f"UNI-{secrets.token_hex(4).upper()}"
        
        university = {
            "university_id": university_id,
            "name": data.get("name"),
            "admin_email": data.get("admin_email"),
            "location": data.get("location", ""),
            "type": data.get("type", "University"),
            "student_count": 0,
            "created_at": datetime.now().isoformat()
        }
        
        self.universities.append(university)
        
        return {
            "status": "success",
            "university_id": university_id,
            "message": "University registered!",
            "admin_portal": f"https://charvakit.com/university/{university_id}"
        }
    
    def add_student(self, data: Dict) -> Dict:
        """
        Add student under a university.
        data = {"university_id": str, "name": str, "email": str, "graduation_year": int}
        """
        student_id = f"STU-{secrets.token_hex(4).upper()}"
        
        student = {
            "student_id": student_id,
            "university_id": data.get("university_id"),
            "name": data.get("name"),
            "email": data.get("email"),
            "graduation_year": int(data.get("graduation_year", 2026)),
            "status": "enrolled",
            "placement_status": "not_placed",
            "created_at": datetime.now().isoformat()
        }
        
        self.students.append(student)
        
        for uni in self.universities:
            if uni["university_id"] == data.get("university_id"):
                uni["student_count"] += 1
        
        return {"status": "success", "student_id": student_id, "message": "Student added"}
    
    def record_outcome(self, data: Dict) -> Dict:
        """
        Record first-destination outcome.
        data = {
            "student_id": str,
            "outcome_type": "employed" / "higher_education" / "entrepreneur" / "seeking",
            "company_name": str,
            "salary": float,
            "job_title": str,
            "location": str
        }
        """
        outcome_id = f"OUT-{secrets.token_hex(4).upper()}"
        
        outcome = {
            "outcome_id": outcome_id,
            "student_id": data.get("student_id"),
            "outcome_type": data.get("outcome_type", "employed"),
            "company_name": data.get("company_name", ""),
            "salary": float(data.get("salary", 0)),
            "job_title": data.get("job_title", ""),
            "location": data.get("location", ""),
            "recorded_at": datetime.now().isoformat()
        }
        
        self.outcomes.append(outcome)
        
        # Update student placement
        for student in self.students:
            if student["student_id"] == data.get("student_id"):
                student["placement_status"] = "placed" if data.get("outcome_type") == "employed" else data.get("outcome_type")
        
        return {"status": "success", "outcome_id": outcome_id, "message": "Outcome recorded"}
    
    def get_first_destination_report(self, university_id: str) -> Dict:
        """Generate first-destination outcome report."""
        uni = self._find_university(university_id)
        if not uni:
            return {"status": "error", "message": "University not found"}
        
        uni_students = [s for s in self.students if s["university_id"] == university_id]
        student_ids = [s["student_id"] for s in uni_students]
        uni_outcomes = [o for o in self.outcomes if o["student_id"] in student_ids]
        
        employed = [o for o in uni_outcomes if o["outcome_type"] == "employed"]
        salaries = [o["salary"] for o in employed if o["salary"] > 0]
        
        return {
            "status": "success",
            "university": uni["name"],
            "report": {
                "total_students": len(uni_students),
                "outcomes_recorded": len(uni_outcomes),
                "employment_rate": round(len(employed) / len(uni_students) * 100, 1) if uni_students else 0,
                "average_salary": round(sum(salaries) / len(salaries), 2) if salaries else 0,
                "top_companies": self._get_top_companies(employed),
                "top_locations": self._get_top_locations(employed)
            }
        }
    
    def get_university_dashboard(self, university_id: str) -> Dict:
        """Get university admin dashboard."""
        uni = self._find_university(university_id)
        if not uni:
            return {"status": "error", "message": "University not found"}
        
        uni_students = [s for s in self.students if s["university_id"] == university_id]
        
        return {
            "status": "success",
            "university": uni,
            "students": uni_students,
            "report": self.get_first_destination_report(university_id)["report"] if uni_students else None
        }
    
    def get_stats(self) -> Dict:
        """Get university engine statistics."""
        return {
            "status": "success",
            "stats": {
                "total_universities": len(self.universities),
                "total_students": len(self.students),
                "total_outcomes": len(self.outcomes),
                "employment_rate": round(len([o for o in self.outcomes if o["outcome_type"] == "employed"]) / len(self.outcomes) * 100, 1) if self.outcomes else 0
            }
        }
    
    def _get_top_companies(self, outcomes: List[Dict], limit: int = 5) -> List[Dict]:
        company_counts = {}
        for o in outcomes:
            if o["company_name"]:
                company_counts[o["company_name"]] = company_counts.get(o["company_name"], 0) + 1
        sorted_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"company": c, "hires": n} for c, n in sorted_companies[:limit]]
    
    def _get_top_locations(self, outcomes: List[Dict], limit: int = 5) -> List[Dict]:
        location_counts = {}
        for o in outcomes:
            if o["location"]:
                location_counts[o["location"]] = location_counts.get(o["location"], 0) + 1
        sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"location": l, "count": n} for l, n in sorted_locations[:limit]]
    
    def _find_university(self, university_id: str) -> Optional[Dict]:
        for uni in self.universities:
            if uni["university_id"] == university_id:
                return uni
        return None


university_engine = UniversityEngine()