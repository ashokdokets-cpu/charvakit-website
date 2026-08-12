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
            "name": str,
            "email": str,
            "phone": str,
            "skills": List[str],
            "experience_years": int,
            "current_role": str,
            "preferred_roles": List[str],
            "location": str,
            "visa_status": str,  # For NA module
            "portfolio_url": str,
            "resume_text": str
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
            "status": CandidateStatus.REGISTERED,
            "skill_score": None,
            "badge_id": None,
            "registered_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.candidates.append(candidate)
        logger.info(f"Candidate registered: {candidate_id} - {data.get('name')}")
        
        return {
            "status": "success",
            "candidate_id": candidate_id,
            "message": "Welcome to Charvak! Next step: Take your free Skill Check.",
            "next_step": "/skill-check"
        }
    
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
        Search candidate pool.
        filters = {"skill": str, "experience_min": int, "location": str, "visa_status": str}
        """
        results = self.candidates
        
        if filters:
            if filters.get("skill"):
                skill = filters["skill"].lower()
                results = [c for c in results if any(skill in s.lower() for s in c["skills"])]
            if filters.get("experience_min"):
                min_exp = int(filters["experience_min"])
                results = [c for c in results if c["experience_years"] >= min_exp]
            if filters.get("location"):
                loc = filters["location"].lower()
                results = [c for c in results if loc in c["location"].lower()]
            if filters.get("visa_status"):
                results = [c for c in results if filters["visa_status"].lower() in c["visa_status"].lower()]
            if filters.get("skill_score_min"):
                min_score = int(filters["skill_score_min"])
                results = [c for c in results if c["skill_score"] and c["skill_score"] >= min_score]
        
        # Sort by skill score descending
        results.sort(key=lambda c: c.get("skill_score") or 0, reverse=True)
        
        return {
            "status": "success",
            "candidates": results,
            "count": len(results),
            "verified_count": len([c for c in results if c["status"] == CandidateStatus.BADGE_EARNED]),
            "placed_count": len([c for c in results if c["status"] == CandidateStatus.PLACED])
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