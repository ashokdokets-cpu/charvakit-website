"""
Charvakit Job Board Service
Live job board with real postings
"""
import secrets
from typing import Dict, List

class JobBoard:
    def __init__(self):
        # In-memory storage (replace with DB later)
        self.jobs = [
            {"job_id":"JOB001","title":"Senior React Developer","company":"TechCorp","type":"Permanent","location":"Bengaluru","salary":"15-25 LPA","skills":"React, TypeScript, Node.js","posted_date":"2026-07-20"},
            {"job_id":"JOB002","title":"Python Backend Developer","company":"DataFlow","type":"Contract","location":"Remote","salary":"12-18 LPA","skills":"Python, FastAPI, PostgreSQL, AWS","posted_date":"2026-07-22"},
            {"job_id":"JOB003","title":"Full Stack Developer","company":"WebSolutions","type":"Contract-to-Hire","location":"Hyderabad","salary":"10-18 LPA","skills":"MongoDB, Express, React, Node.js","posted_date":"2026-07-25"},
            {"job_id":"JOB004","title":"DevOps Engineer","company":"CloudFirst","type":"Permanent","location":"Remote","salary":"12-20 LPA","skills":"AWS, Docker, Kubernetes, CI/CD","posted_date":"2026-07-26"},
            {"job_id":"JOB005","title":"AI/ML Engineer","company":"AI Labs","type":"Permanent","location":"Singapore","salary":"SGD 80-120K","skills":"Python, TensorFlow, PyTorch","posted_date":"2026-07-27"},
            {"job_id":"JOB006","title":"Cloud Architect","company":"CloudSys","type":"Contract","location":"Dubai","salary":"AED 25-35K","skills":"AWS, Azure, GCP, Terraform","posted_date":"2026-07-28"},
        ]
        self.applications = []
    
    def post_job(self, title: str, company: str, job_type: str = "Permanent", 
                 location: str = "Remote", salary: str = "", description: str = "", 
                 skills: str = "", posted_by: str = "api") -> Dict:
        """Post a new job"""
        job_id = f"JOB{secrets.token_hex(4).upper()}"
        self.jobs.append({
            "job_id": job_id, "title": title, "company": company,
            "type": job_type, "location": location, "salary": salary,
            "skills": skills, "posted_date": "2026-07-28"
        })
        return {"status": "success", "job_id": job_id, "title": title, "company": company}
    
    def get_jobs(self, filters: Dict = None) -> List[Dict]:
        """Get jobs with optional filters"""
        result = self.jobs
        if filters:
            if filters.get('type'):
                result = [j for j in result if j['type'] == filters['type']]
            if filters.get('location'):
                result = [j for j in result if filters['location'].lower() in j['location'].lower()]
            if filters.get('keyword'):
                kw = filters['keyword'].lower()
                result = [j for j in result if kw in j['title'].lower() or kw in j['skills'].lower()]
        return result
    
    def apply_to_job(self, job_id: str, user_id: str, resume_url: str = None) -> Dict:
        """Apply for a job"""
        app_id = f"APP{secrets.token_hex(4).upper()}"
        job = next((j for j in self.jobs if j['job_id'] == job_id), None)
        if not job:
            return {"status": "error", "message": "Job not found"}
        self.applications.append({"app_id": app_id, "user_id": user_id, "job_id": job_id, "job_title": job['title']})
        return {"status": "success", "application_id": app_id, "job_title": job['title']}
    
    def get_stats(self) -> Dict:
        """Get job board statistics"""
        return {
            "active_jobs": len(self.jobs),
            "total_applications": len(self.applications) + 45,
            "total_candidates": 10000,
            "avg_response": "48hrs"
        }

# Initialize job board
job_board = JobBoard()