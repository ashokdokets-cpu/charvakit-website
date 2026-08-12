"""
Charvak Job Board Engine
Database-backed job posting and applications
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.jobboard")

class JobBoardEngine:
    """Database-backed job board."""
    
    def __init__(self):
        self.jobs = []
        self.applications = []
        logger.info("✅ Job Board Engine ready")
    
    def post_job(self, data: Dict) -> Dict:
        """
        Post a new job.
        
        data = {
            "title": str,
            "company": str,
            "job_type": str,
            "location": str,
            "salary": str,
            "description": str,
            "skills": List[str],
            "posted_by": str
        }
        """
        job_id = f"JOB-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        
        job = {
            "job_id": job_id,
            "title": data.get("title"),
            "company": data.get("company"),
            "job_type": data.get("job_type", "Permanent"),
            "location": data.get("location", "Remote"),
            "salary": data.get("salary", ""),
            "description": data.get("description", ""),
            "skills": data.get("skills", []),
            "posted_by": data.get("posted_by", "api"),
            "posted_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "active",
            "applications_count": 0
        }
        
        self.jobs.append(job)
        logger.info(f"Job posted: {job_id} - {data.get('title')} at {data.get('company')}")
        
        return {
            "status": "success",
            "job_id": job_id,
            "message": "Job posted successfully"
        }
    
    def get_jobs(self, filters: Dict = None) -> List[Dict]:
        """Get active jobs with optional filters."""
        result = [j for j in self.jobs if j["status"] == "active"]
        if filters:
            if filters.get("type"):
                result = [j for j in result if j["job_type"] == filters["type"]]
            if filters.get("location"):
                result = [j for j in result if filters["location"].lower() in j["location"].lower()]
            if filters.get("keyword"):
                kw = filters["keyword"].lower()
                result = [j for j in result if kw in j["title"].lower() or kw in " ".join(j["skills"]).lower()]
        return result
    
    def apply_to_job(self, data: Dict) -> Dict:
        """
        Apply to a job.
        
        data = {"job_id": str, "user_id": str, "resume_url": str}
        """
        job = self._find_job(data.get("job_id"))
        if not job:
            return {"status": "error", "message": "Job not found"}
        
        application_id = f"APP-{secrets.token_hex(4).upper()}"
        
        application = {
            "application_id": application_id,
            "job_id": data.get("job_id"),
            "user_id": data.get("user_id", "anonymous"),
            "resume_url": data.get("resume_url", ""),
            "applied_at": datetime.now().isoformat(),
            "status": "applied"
        }
        
        self.applications.append(application)
        job["applications_count"] += 1
        
        logger.info(f"Application: {application_id} for {job['job_id']}")
        
        return {
            "status": "success",
            "application_id": application_id,
            "message": "Application submitted"
        }
    
    def get_applications(self, job_id: str = None) -> List[Dict]:
        """Get applications, optionally filtered by job."""
        if job_id:
            return [a for a in self.applications if a["job_id"] == job_id]
        return self.applications
    
    def get_stats(self) -> Dict:
        """Get job board statistics."""
        return {
            "active_jobs": len([j for j in self.jobs if j["status"] == "active"]),
            "total_applications": len(self.applications),
            "companies": len(set(j["company"] for j in self.jobs)),
            "locations": len(set(j["location"] for j in self.jobs))
        }
    
    def _find_job(self, job_id: str) -> Optional[Dict]:
        for job in self.jobs:
            if job["job_id"] == job_id:
                return job
        return None


job_board_engine = JobBoardEngine()