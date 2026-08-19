"""
Charvak Micro-Internship Global Extension
Country, currency, timezone, remote/onsite, mentor, team projects
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.microglobal")


class MicroInternshipGlobal:
    """Global features for Micro-Internship Engine."""
    
    def __init__(self):
        self.mentors = []
        self.team_projects = []
        self.location_preferences = []
        logger.info("Global Micro-Internship Extension ready")
    
    # 1. GLOBAL PROJECT POSTING (with country/currency/remote)
    def post_global_project(self, data: Dict) -> Dict:
        """
        Post project with global fields.
        data = {title, country, currency, mode (remote/onsite/hybrid),
                timezone, stipend, hours_per_week, mentor_required}
        """
        project_id = f"GPROJ-{secrets.token_hex(4).upper()}"
        country = data.get("country", "India")
        currency = "₹" if country == "India" else data.get("currency", "$")
        
        project = {
            "project_id": project_id,
            "title": data.get("title"),
            "country": country,
            "currency": currency,
            "mode": data.get("mode", "remote"),
            "timezone": data.get("timezone", "Asia/Kolkata" if country == "India" else "UTC"),
            "stipend": float(data.get("stipend", 0)),
            "hours_per_week": data.get("hours_per_week", 20),
            "mentor_required": data.get("mentor_required", True),
            "team_size": int(data.get("team_size", 1)),
            "created_at": datetime.now().isoformat()
        }
        
        self.team_projects.append(project) if project["team_size"] > 1 else None
        
        return {
            "status": "success",
            "project_id": project_id,
            "project": project,
            "message": f"Global project posted! ({country}, {currency}, {project['mode']})"
        }
    
    # 2. ASSIGN MENTOR
    def assign_mentor(self, data: Dict) -> Dict:
        mentor_id = f"MENTOR-{secrets.token_hex(4).upper()}"
        mentor = {
            "mentor_id": mentor_id,
            "name": data.get("name"),
            "email": data.get("email"),
            "expertise": data.get("expertise", []),
            "timezone": data.get("timezone", "UTC"),
            "assigned_projects": []
        }
        self.mentors.append(mentor)
        return {"status": "success", "mentor_id": mentor_id, "message": "Mentor added!"}
    
    # 3. FILTER BY LOCATION/COUNTRY
    def filter_projects(self, filters: Dict = None) -> Dict:
        """Filter global projects by country, mode, timezone."""
        projects = self.team_projects
        if filters:
            if filters.get("country"):
                projects = [p for p in projects if p.get("country") == filters["country"]]
            if filters.get("mode"):
                projects = [p for p in projects if p.get("mode") == filters["mode"]]
            if filters.get("team_size_min"):
                projects = [p for p in projects if p.get("team_size", 1) >= int(filters["team_size_min"])]
        
        return {
            "status": "success",
            "projects": projects,
            "count": len(projects),
            "countries": list(set(p.get("country", "India") for p in self.team_projects)),
            "modes": list(set(p.get("mode", "remote") for p in self.team_projects))
        }
    
    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "stats": {
                "total_mentors": len(self.mentors),
                "global_projects": len(self.team_projects),
                "team_projects": len([p for p in self.team_projects if p.get("team_size", 1) > 1])
            }
        }


micro_internship_global = MicroInternshipGlobal()