"""
Charvak Micro-Internship Engine
Complete end-to-end system: Post → Screen → Assign → Track → Pay
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.microinternship")


class ProjectStatus:
    OPEN = "open"
    IN_REVIEW = "in_review"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ApplicationStatus:
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    ASSIGNED = "assigned"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class MicroInternshipEngine:
    """Complete micro-internship management system."""
    
    def __init__(self):
        self.projects = []
        self.applications = []
        self.clients = []
        self.interns = []
        logger.info("✅ Micro-Internship Engine ready")
    
    # ============================================================
    # CLIENT MANAGEMENT
    # ============================================================
    
    def register_client(self, data: Dict) -> Dict:
        """Register a client company."""
        client_id = f"CLIENT-{secrets.token_hex(4).upper()}"
        
        client = {
            "client_id": client_id,
            "company_name": data.get("company_name"),
            "contact_email": data.get("contact_email"),
            "contact_name": data.get("contact_name"),
            "industry": data.get("industry", ""),
            "company_size": data.get("company_size", ""),
            "created_at": datetime.now().isoformat(),
            "total_projects": 0,
            "active_projects": 0,
            "total_spend": 0
        }
        
        self.clients.append(client)
        logger.info(f"Client registered: {client_id} - {data.get('company_name')}")
        
        return {
            "status": "success",
            "client_id": client_id,
            "message": "Client registered successfully"
        }
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        """Get client by ID."""
        for client in self.clients:
            if client["client_id"] == client_id:
                return client
        return None
    
    def get_client_dashboard(self, client_id: str) -> Dict:
        """Get full client dashboard with all projects and applications."""
        client = self.get_client(client_id)
        if not client:
            return {"status": "error", "message": "Client not found"}
        
        client_projects = [p for p in self.projects if p["client_id"] == client_id]
        project_ids = [p["project_id"] for p in client_projects]
        client_applications = [a for a in self.applications if a["project_id"] in project_ids]
        
        return {
            "status": "success",
            "client": client,
            "projects": client_projects,
            "applications": client_applications,
            "stats": {
                "total_projects": len(client_projects),
                "active_projects": len([p for p in client_projects if p["status"] in [ProjectStatus.ASSIGNED, ProjectStatus.IN_PROGRESS]]),
                "total_applications": len(client_applications),
                "total_spend": client["total_spend"],
                "hired_count": len([p for p in client_projects if p["status"] == ProjectStatus.COMPLETED])
            }
        }
    
    # ============================================================
    # PROJECT MANAGEMENT
    # ============================================================
    
    def post_project(self, data: Dict) -> Dict:
        """
        Post a new micro-internship project.
        
        data = {
            "title": str,
            "category": str,
            "difficulty": str,
            "duration_weeks": int,
            "budget_inr": float,
            "skills_required": List[str],
            "description": str,
            "client_id": str,
            "company_name": str,
            "contact_email": str,
            "escrow_required": bool
        }
        """
        project_id = f"PROJ-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        
        project = {
            "project_id": project_id,
            "title": data.get("title"),
            "category": data.get("category", "Web Development"),
            "difficulty": data.get("difficulty", "Intermediate"),
            "duration_weeks": int(data.get("duration_weeks", 2)),
            "budget_inr": float(data.get("budget_inr", 5000)),
            "budget_usd": round(float(data.get("budget_inr", 5000)) / 83, 2),
            "skills_required": data.get("skills_required", []),
            "description": data.get("description", ""),
            "client_id": data.get("client_id"),
            "company_name": data.get("company_name"),
            "contact_email": data.get("contact_email"),
            "escrow_required": data.get("escrow_required", True),
            "escrow_id": None,
            "assigned_intern": None,
            "status": ProjectStatus.OPEN,
            "applications_count": 0,
            "created_at": datetime.now().isoformat(),
            "deadline": (datetime.now() + timedelta(weeks=int(data.get("duration_weeks", 2)))).isoformat(),
            "milestones": self._generate_milestones(int(data.get("duration_weeks", 2)), float(data.get("budget_inr", 5000)))
        }
        
        self.projects.append(project)
        
        # Update client stats
        for client in self.clients:
            if client["client_id"] == data.get("client_id"):
                client["total_projects"] += 1
        
        logger.info(f"Project posted: {project_id} - {data.get('title')} by {data.get('company_name')}")
        
        return {
            "status": "success",
            "project_id": project_id,
            "message": "Project posted successfully! Candidates can now apply.",
            "project_url": f"https://charvakit.com/micro-internship/{project_id}",
            "escrow": {
                "required": project["escrow_required"],
                "amount": project["budget_inr"],
                "status": "pending_deposit" if project["escrow_required"] else "not_required"
            }
        }
    
    def get_project(self, project_id: str) -> Dict:
        """Get project details."""
        for project in self.projects:
            if project["project_id"] == project_id:
                return {"status": "success", "project": project}
        return {"status": "error", "message": "Project not found"}
    
    def get_open_projects(self, filters: Dict = None) -> Dict:
        """Get all open projects for candidate browsing."""
        open_projects = [p for p in self.projects if p["status"] == ProjectStatus.OPEN]
        
        if filters:
            if filters.get("category"):
                open_projects = [p for p in open_projects if p["category"] == filters["category"]]
            if filters.get("difficulty"):
                open_projects = [p for p in open_projects if p["difficulty"] == filters["difficulty"]]
            if filters.get("max_budget"):
                open_projects = [p for p in open_projects if p["budget_inr"] <= filters["max_budget"]]
            if filters.get("skill"):
                open_projects = [p for p in open_projects if filters["skill"].lower() in " ".join(p["skills_required"]).lower()]
        
        return {
            "status": "success",
            "projects": open_projects,
            "count": len(open_projects),
            "categories": list(set(p["category"] for p in self.projects)),
            "total_budget": sum(p["budget_inr"] for p in open_projects)
        }
    
    def _generate_milestones(self, weeks: int, budget: float) -> List[Dict]:
        """Generate project milestones."""
        milestones = []
        if weeks == 1:
            milestones = [
                {"name": "Project Kickoff", "week": 1, "payment": round(budget * 0.3, 2)},
                {"name": "Final Delivery", "week": 1, "payment": round(budget * 0.7, 2)}
            ]
        elif weeks == 2:
            milestones = [
                {"name": "Project Kickoff", "week": 1, "payment": round(budget * 0.2, 2)},
                {"name": "Mid-Project Review", "week": 1, "payment": round(budget * 0.3, 2)},
                {"name": "Final Delivery", "week": 2, "payment": round(budget * 0.5, 2)}
            ]
        else:
            milestones = [
                {"name": "Project Kickoff", "week": 1, "payment": round(budget * 0.15, 2)},
                {"name": "Progress Checkpoint", "week": weeks // 2, "payment": round(budget * 0.25, 2)},
                {"name": "Final Review", "week": weeks - 1, "payment": round(budget * 0.25, 2)},
                {"name": "Project Completion", "week": weeks, "payment": round(budget * 0.35, 2)}
            ]
        return milestones
    
    # ============================================================
    # APPLICATION MANAGEMENT
    # ============================================================
    
    def apply_to_project(self, data: Dict) -> Dict:
        """
        Candidate applies to a project.
        
        data = {
            "project_id": str,
            "candidate_name": str,
            "candidate_email": str,
            "skills": List[str],
            "portfolio_url": str,
            "why_interested": str
        }
        """
        project = self._find_project(data.get("project_id"))
        if not project:
            return {"status": "error", "message": "Project not found"}
        
        if project["status"] != ProjectStatus.OPEN:
            return {"status": "error", "message": "Project is no longer accepting applications"}
        
        application_id = f"APP-{secrets.token_hex(4).upper()}"
        
        application = {
            "application_id": application_id,
            "project_id": data.get("project_id"),
            "candidate_name": data.get("candidate_name"),
            "candidate_email": data.get("candidate_email"),
            "skills": data.get("skills", []),
            "portfolio_url": data.get("portfolio_url", ""),
            "why_interested": data.get("why_interested", ""),
            "status": ApplicationStatus.APPLIED,
            "ai_score": self._calculate_ai_score(data.get("skills", []), project["skills_required"]),
            "applied_at": datetime.now().isoformat(),
            "assigned_at": None,
            "submitted_at": None,
            "approved_at": None
        }
        
        self.applications.append(application)
        project["applications_count"] += 1
        
        logger.info(f"Application received: {application_id} for {project['project_id']} from {data.get('candidate_name')}")
        
        return {
            "status": "success",
            "application_id": application_id,
            "ai_match_score": application["ai_score"],
            "message": "Application submitted! The client will review your profile."
        }
    
    def _calculate_ai_score(self, candidate_skills: List[str], required_skills: List[str]) -> int:
        """Calculate AI match score between candidate and project."""
        if not required_skills:
            return 70  # Default score if no skills specified
        
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        required_skills_lower = [s.lower() for s in required_skills]
        
        matches = 0
        for req_skill in required_skills_lower:
            for cand_skill in candidate_skills_lower:
                if req_skill in cand_skill or cand_skill in req_skill:
                    matches += 1
                    break
        
        score = int((matches / len(required_skills_lower)) * 100)
        return min(score, 100)
    
    def get_project_applications(self, project_id: str) -> Dict:
        """Get all applications for a project."""
        applications = [a for a in self.applications if a["project_id"] == project_id]
        # Sort by AI score descending
        applications.sort(key=lambda a: a["ai_score"], reverse=True)
        
        return {
            "status": "success",
            "applications": applications,
            "count": len(applications),
            "shortlisted": [a for a in applications if a["status"] == ApplicationStatus.SHORTLISTED],
            "average_score": sum(a["ai_score"] for a in applications) / len(applications) if applications else 0
        }
    
    # ============================================================
    # ASSIGNMENT & TRACKING
    # ============================================================
    
    def assign_intern(self, project_id: str, application_id: str) -> Dict:
        """Assign a candidate to a project."""
        project = self._find_project(project_id)
        if not project:
            return {"status": "error", "message": "Project not found"}
        
        application = self._find_application(application_id)
        if not application:
            return {"status": "error", "message": "Application not found"}
        
        project["assigned_intern"] = {
            "name": application["candidate_name"],
            "email": application["candidate_email"],
            "application_id": application_id
        }
        project["status"] = ProjectStatus.ASSIGNED
        application["status"] = ApplicationStatus.ASSIGNED
        application["assigned_at"] = datetime.now().isoformat()
        
        logger.info(f"Intern assigned: {application['candidate_name']} → {project_id}")
        
        return {
            "status": "success",
            "message": f"{application['candidate_name']} assigned to {project['title']}",
            "next_step": "Project started. Intern can begin work.",
            "escrow_required": project["escrow_required"],
            "escrow_amount": project["budget_inr"]
        }
    
    def submit_work(self, project_id: str, submission_data: Dict) -> Dict:
        """Intern submits work for review."""
        project = self._find_project(project_id)
        if not project:
            return {"status": "error", "message": "Project not found"}
        
        project["status"] = ProjectStatus.SUBMITTED
        project["submission"] = {
            "deliverables": submission_data.get("deliverables", ""),
            "submitted_at": datetime.now().isoformat(),
            "notes": submission_data.get("notes", "")
        }
        
        for app in self.applications:
            if app["project_id"] == project_id and app["status"] == ApplicationStatus.ASSIGNED:
                app["status"] = ApplicationStatus.SUBMITTED
                app["submitted_at"] = datetime.now().isoformat()
        
        logger.info(f"Work submitted for {project_id}")
        
        return {
            "status": "success",
            "message": "Work submitted! Client will review.",
            "review_deadline": (datetime.now() + timedelta(days=3)).isoformat(),
            "escrow_release": "Payment will be released upon client approval"
        }
    
    def approve_work(self, project_id: str, approval_data: Dict) -> Dict:
        """Client approves work and payment is released."""
        project = self._find_project(project_id)
        if not project:
            return {"status": "error", "message": "Project not found"}
        
        project["status"] = ProjectStatus.COMPLETED
        project["completed_at"] = datetime.now().isoformat()
        project["feedback"] = approval_data.get("feedback", "")
        project["rating"] = approval_data.get("rating", 5)
        
        for app in self.applications:
            if app["project_id"] == project_id and app["status"] == ApplicationStatus.SUBMITTED:
                app["status"] = ApplicationStatus.APPROVED
                app["approved_at"] = datetime.now().isoformat()
        
        # Update client stats
        for client in self.clients:
            if client["client_id"] == project["client_id"]:
                client["total_spend"] += project["budget_inr"]
                client["active_projects"] -= 1 if client["active_projects"] > 0 else 0
        
        logger.info(f"✅ Project completed: {project_id} | Payment released: ₹{project['budget_inr']}")
        
        return {
            "status": "success",
            "message": "Project completed! Payment released from escrow.",
            "amount_released": project["budget_inr"],
            "intern_name": project["assigned_intern"]["name"] if project["assigned_intern"] else "Unknown",
            "conversion_ready": True,
            "next_step": "You can now offer the intern a full-time position"
        }
    
    # ============================================================
    # HELPERS
    # ============================================================
    
    def _find_project(self, project_id: str) -> Optional[Dict]:
        for project in self.projects:
            if project["project_id"] == project_id:
                return project
        return None
    
    def _find_application(self, application_id: str) -> Optional[Dict]:
        for app in self.applications:
            if app["application_id"] == application_id:
                return app
        return None
    
    def get_stats(self) -> Dict:
        """Get system statistics."""
        return {
            "status": "success",
            "stats": {
                "total_projects": len(self.projects),
                "open_projects": len([p for p in self.projects if p["status"] == ProjectStatus.OPEN]),
                "completed_projects": len([p for p in self.projects if p["status"] == ProjectStatus.COMPLETED]),
                "total_applications": len(self.applications),
                "total_clients": len(self.clients),
                "total_value_inr": sum(p["budget_inr"] for p in self.projects),
                "total_paid_inr": sum(p["budget_inr"] for p in self.projects if p["status"] == ProjectStatus.COMPLETED)
            }
        }


# ============================================================
# SINGLETON
# ============================================================
micro_internship_engine = MicroInternshipEngine()