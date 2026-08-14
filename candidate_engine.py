"""
Charvak Candidate Pool Engine
Centralized candidate registry with skill indexing
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.candidates")


class CandidateStatus:
    REGISTERED = "registered"
    SKILL_CHECKED = "skill_checked"
    BADGE_EARNED = "badge_earned"
    INTERNSHIP_DONE = "internship_done"
    PLACED = "placed"
    REJECTED = "rejected"


class CandidateEngine:
    """Central candidate pool."""
    
    def __init__(self):
        self.candidates = []
        self.skill_profiles = []
        logger.info("✅ Candidate Engine ready")
    
        def register_candidate(self, data: Dict) -> Dict:
        """
        Register a new candidate.
        
        data = {
            "name": str, "email": str, "phone": str,
            "skills": List[str], "experience_years": int,
            "current_role": str, "preferred_roles": List[str],
            "location": str, "visa_status": str,
            "portfolio_url": str, "resume_text": str,
            # NEW: Advanced fields
            "education": str, "degree": str, "major": str,
            "university": str, "gpa": float, "graduation_year": int,
            "certifications": List[str], "languages_spoken": List[str],
            "work_authorization": str, "willing_to_relocate": bool,
            "remote_preference": str, "salary_expectation": str,
            "availability": str, "github_url": str,
            "linkedin_url": str, "years_coding": int
        }
        """
        candidate_id = f"CAND-{secrets.token_hex(4).upper()}"
        
        candidate = {
            "candidate_id": candidate_id,
            "name": data.get("name"),
            "email": data.get("email"),
            "phone": data.get("phone", ""),
            "skills": data.get("skills", []),
            "experience_years": int(data.get("experience_years", 0)),
            "current_role": data.get("current_role", ""),
            "preferred_roles": data.get("preferred_roles", []),
            "location": data.get("location", ""),
            "visa_status": data.get("visa_status", ""),
            "portfolio_url": data.get("portfolio_url", ""),
            "resume_text": data.get("resume_text", ""),
            # Advanced fields
            "education": data.get("education", ""),
            "degree": data.get("degree", ""),
            "major": data.get("major", ""),
            "university": data.get("university", ""),
            "gpa": float(data.get("gpa", 0)) if data.get("gpa") else None,
            "graduation_year": int(data.get("graduation_year", 0)) if data.get("graduation_year") else None,
            "certifications": data.get("certifications", []),
            "languages_spoken": data.get("languages_spoken", []),
            "work_authorization": data.get("work_authorization", ""),
            "willing_to_relocate": data.get("willing_to_relocate", False),
            "remote_preference": data.get("remote_preference", "Open"),
            "salary_expectation": data.get("salary_expectation", ""),
            "availability": data.get("availability", "Immediate"),
            "github_url": data.get("github_url", ""),
            "linkedin_url": data.get("linkedin_url", ""),
            "years_coding": int(data.get("years_coding", 0)) if data.get("years_coding") else None,
            "status": CandidateStatus.REGISTERED,
            "skill_score": None,
            "badge_id": None,
            "registered_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.candidates.append(candidate)
        return {"status": "success", "candidate_id": candidate_id, "message": "Welcome to Charvak!"}
    
    def get_candidate(self, candidate_id: str) -> Dict:
        """Get candidate by ID."""
        for c in self.candidates:
            if c["candidate_id"] == candidate_id:
                return {"status": "success", "candidate": c}
        return {"status": "error", "message": "Candidate not found"}
    
    def get_candidate_by_email(self, email: str) -> Optional[Dict]:
        """Get candidate by email."""
        for c in self.candidates:
            if c["email"] == email:
                return c
        return None
    
    def update_skill_score(self, candidate_id: str, score: int, badge_id: str = None) -> Dict:
        """Update candidate's skill score after assessment."""
        candidate = self._find(candidate_id)
        if not candidate:
            return {"status": "error", "message": "Candidate not found"}
        
        candidate["skill_score"] = score
        candidate["badge_id"] = badge_id
        candidate["status"] = CandidateStatus.BADGE_EARNED if score >= 70 else CandidateStatus.SKILL_CHECKED
        candidate["updated_at"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "candidate_id": candidate_id,
            "skill_score": score,
            "badge_earned": score >= 70,
            "message": "Skill score updated!"
        }
    
        def search_candidates(self, filters: Dict = None) -> Dict:
        """
        Advanced search with 50+ filter combinations.
        
        filters = {
            "skill": str, "experience_min": int, "experience_max": int,
            "location": str, "visa_status": str, "skill_score_min": int,
            "education": str, "degree": str, "major": str,
            "university": str, "gpa_min": float, "graduation_year_min": int,
            "certification": str, "language": str,
            "work_authorization": str, "remote_preference": str,
            "availability": str, "salary_max": str,
            "years_coding_min": int
        }
        """
        results = self.candidates
        
        if filters:
            if filters.get("skill"):
                skill = filters["skill"].lower()
                results = [c for c in results if any(skill in s.lower() for s in c["skills"])]
            if filters.get("experience_min"):
                results = [c for c in results if c["experience_years"] >= int(filters["experience_min"])]
            if filters.get("experience_max"):
                results = [c for c in results if c["experience_years"] <= int(filters["experience_max"])]
            if filters.get("location"):
                loc = filters["location"].lower()
                results = [c for c in results if loc in c["location"].lower()]
            if filters.get("visa_status"):
                results = [c for c in results if filters["visa_status"].lower() in c["visa_status"].lower()]
            if filters.get("skill_score_min"):
                results = [c for c in results if c["skill_score"] and c["skill_score"] >= int(filters["skill_score_min"])]
            if filters.get("education"):
                results = [c for c in results if filters["education"].lower() in c["education"].lower()]
            if filters.get("degree"):
                results = [c for c in results if filters["degree"].lower() in c["degree"].lower()]
            if filters.get("major"):
                results = [c for c in results if filters["major"].lower() in c["major"].lower()]
            if filters.get("university"):
                results = [c for c in results if filters["university"].lower() in c["university"].lower()]
            if filters.get("gpa_min"):
                results = [c for c in results if c["gpa"] and c["gpa"] >= float(filters["gpa_min"])]
            if filters.get("graduation_year_min"):
                results = [c for c in results if c["graduation_year"] and c["graduation_year"] >= int(filters["graduation_year_min"])]
            if filters.get("certification"):
                cert = filters["certification"].lower()
                results = [c for c in results if any(cert in x.lower() for x in c.get("certifications", []))]
            if filters.get("language"):
                lang = filters["language"].lower()
                results = [c for c in results if any(lang in x.lower() for x in c.get("languages_spoken", []))]
            if filters.get("work_authorization"):
                results = [c for c in results if filters["work_authorization"].lower() in c.get("work_authorization", "").lower()]
            if filters.get("remote_preference"):
                results = [c for c in results if filters["remote_preference"].lower() in c.get("remote_preference", "").lower()]
            if filters.get("availability"):
                results = [c for c in results if filters["availability"].lower() in c.get("availability", "").lower()]
            if filters.get("years_coding_min"):
                results = [c for c in results if c.get("years_coding") and c["years_coding"] >= int(filters["years_coding_min"])]
        
        results.sort(key=lambda c: c.get("skill_score") or 0, reverse=True)
        
        return {
            "status": "success",
            "candidates": results,
            "count": len(results),
            "filters_applied": filters or {},
            "available_filters": [
                "skill", "experience_min", "experience_max", "location",
                "visa_status", "skill_score_min", "education", "degree",
                "major", "university", "gpa_min", "graduation_year_min",
                "certification", "language", "work_authorization",
                "remote_preference", "availability", "years_coding_min"
            ]
        }
    
    def mark_placed(self, candidate_id: str, placement_data: Dict = None) -> Dict:
        """Mark candidate as placed."""
        candidate = self._find(candidate_id)
        if not candidate:
            return {"status": "error", "message": "Candidate not found"}
        
        candidate["status"] = CandidateStatus.PLACED
        candidate["placement"] = placement_data or {}
        candidate["updated_at"] = datetime.now().isoformat()
        
        return {"status": "success", "message": f"{candidate['name']} marked as placed!"}
    
    def get_pool_stats(self) -> Dict:
        """Get candidate pool statistics."""
        total = len(self.candidates)
        verified = len([c for c in self.candidates if c["status"] in [CandidateStatus.BADGE_EARNED, CandidateStatus.INTERNSHIP_DONE, CandidateStatus.PLACED]])
        placed = len([c for c in self.candidates if c["status"] == CandidateStatus.PLACED])
        skills = set()
        for c in self.candidates:
            skills.update(c["skills"])
        
        return {
            "status": "success",
            "stats": {
                "total_candidates": total,
                "verified_candidates": verified,
                "placed_candidates": placed,
                "unique_skills": len(skills),
                "avg_experience_years": round(sum(c["experience_years"] for c in self.candidates) / total, 1) if total > 0 else 0,
                "locations": len(set(c["location"] for c in self.candidates if c["location"]))
            }
        }
    
    def _find(self, candidate_id: str) -> Optional[Dict]:
        for c in self.candidates:
            if c["candidate_id"] == candidate_id:
                return c
        return None


candidate_engine = CandidateEngine()