"""
Charvak Career Engine V2
Global job board features: alerts, saved jobs, salary insights,
interview scheduling, recommendations, company follow, offers, withdrawal
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.careerv2")


class CareerV2Engine:
    """Advanced career features."""
    
    def __init__(self):
        self.job_alerts = []
        self.saved_jobs = []
        self.followed_companies = []
        self.salary_data = []
        self.interviews = []
        self.offers = []
        logger.info("Career V2 Engine ready — 6 modules")
    
    # 1. JOB ALERTS
    def create_job_alert(self, data: Dict) -> Dict:
        alert_id = f"ALERT-{secrets.token_hex(4).upper()}"
        alert = {
            "alert_id": alert_id,
            "email": data.get("email"),
            "keywords": data.get("keywords", []),
            "location": data.get("location", ""),
            "frequency": data.get("frequency", "daily"),
            "created_at": datetime.now().isoformat()
        }
        self.job_alerts.append(alert)
        return {"status": "success", "alert_id": alert_id, "message": "Job alert created!"}
    
    def get_alerts(self, email: str) -> Dict:
        alerts = [a for a in self.job_alerts if a["email"] == email]
        return {"status": "success", "alerts": alerts, "count": len(alerts)}
    
    # 2. SAVED JOBS
    def save_job(self, data: Dict) -> Dict:
        save_id = f"SAVE-{secrets.token_hex(4).upper()}"
        saved = {
            "save_id": save_id,
            "email": data.get("email"),
            "job_id": data.get("job_id"),
            "saved_at": datetime.now().isoformat()
        }
        self.saved_jobs.append(saved)
        return {"status": "success", "save_id": save_id, "message": "Job saved!"}
    
    def get_saved_jobs(self, email: str) -> Dict:
        saved = [s for s in self.saved_jobs if s["email"] == email]
        return {"status": "success", "saved_jobs": saved, "count": len(saved)}
    
    # 3. COMPANY FOLLOW
    def follow_company(self, data: Dict) -> Dict:
        follow_id = f"FOLLOW-{secrets.token_hex(4).upper()}"
        follow = {
            "follow_id": follow_id,
            "email": data.get("email"),
            "company": data.get("company"),
            "followed_at": datetime.now().isoformat()
        }
        self.followed_companies.append(follow)
        return {"status": "success", "message": f"Following {data.get('company')}!"}
    
    # 4. SALARY INSIGHTS
    def add_salary(self, data: Dict) -> Dict:
        salary_id = f"SAL-{secrets.token_hex(4).upper()}"
        salary = {
            "salary_id": salary_id,
            "role": data.get("role"),
            "company": data.get("company", "Anonymous"),
            "amount": float(data.get("amount", 0)),
            "location": data.get("location", ""),
            "recorded_at": datetime.now().isoformat()
        }
        self.salary_data.append(salary)
        return {"status": "success", "message": "Salary added anonymously"}
    
    def get_salary_insights(self, role: str = None) -> Dict:
        data = self.salary_data
        if role:
            data = [s for s in data if role.lower() in s["role"].lower()]
        amounts = [s["amount"] for s in data if s["amount"] > 0]
        return {
            "status": "success",
            "count": len(data),
            "average": round(sum(amounts) / len(amounts), 2) if amounts else 0,
            "min": min(amounts) if amounts else 0,
            "max": max(amounts) if amounts else 0
        }
    
    # 5. INTERVIEW SCHEDULING
    def schedule_interview(self, data: Dict) -> Dict:
        interview_id = f"INT-{secrets.token_hex(4).upper()}"
        interview = {
            "interview_id": interview_id,
            "candidate_email": data.get("candidate_email"),
            "employer": data.get("employer"),
            "role": data.get("role"),
            "date": data.get("date"),
            "platform": data.get("platform", "Zoom"),
            "status": "scheduled"
        }
        self.interviews.append(interview)
        return {"status": "success", "interview_id": interview_id, "message": "Interview scheduled!"}
    
    def get_interviews(self, email: str) -> Dict:
        interviews = [i for i in self.interviews if i["candidate_email"] == email]
        return {"status": "success", "interviews": interviews, "count": len(interviews)}
    
    # 6. OFFER MANAGEMENT
    def add_offer(self, data: Dict) -> Dict:
        offer_id = f"OFFER-{secrets.token_hex(4).upper()}"
        offer = {
            "offer_id": offer_id,
            "candidate_email": data.get("candidate_email"),
            "company": data.get("company"),
            "role": data.get("role"),
            "salary": float(data.get("salary", 0)),
            "status": "received"
        }
        self.offers.append(offer)
        return {"status": "success", "offer_id": offer_id, "message": "Offer added!"}
    
    def get_offers(self, email: str) -> Dict:
        offers = [o for o in self.offers if o["candidate_email"] == email]
        return {"status": "success", "offers": offers, "count": len(offers)}
    
    # 7. WITHDRAW APPLICATION
    def withdraw_application(self, application_id: str) -> Dict:
        from job_board_engine import job_board_engine
        for app in job_board_engine.applications:
            if app["application_id"] == application_id:
                app["status"] = "withdrawn"
                return {"status": "success", "message": "Application withdrawn"}
        return {"status": "error", "message": "Application not found"}
    
    # 8. JOB RECOMMENDATIONS
    def get_job_recommendations(self, email: str, skills: List[str] = None) -> Dict:
        from job_board_engine import job_board_engine
        jobs = job_board_engine.get_jobs()
        recommendations = jobs[:5] if jobs else [
            {"title": "Python Developer", "match": 95},
            {"title": "React Developer", "match": 88},
            {"title": "DevOps Engineer", "match": 82}
        ]
        return {"status": "success", "recommendations": recommendations, "count": len(recommendations)}
    
    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "stats": {
                "job_alerts": len(self.job_alerts),
                "saved_jobs": len(self.saved_jobs),
                "followed_companies": len(self.followed_companies),
                "salary_records": len(self.salary_data),
                "interviews": len(self.interviews),
                "offers": len(self.offers)
            }
        }


career_v2_engine = CareerV2Engine()