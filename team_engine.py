"""
Charvak Team Engine
Multi-user team accounts with role-based access
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.team")


class TeamRole:
    ADMIN = "admin"
    RECRUITER = "recruiter"
    VIEWER = "viewer"


class TeamEngine:
    """Handles team accounts and member management."""
    
    def __init__(self):
        self.teams = []
        self.members = []
        logger.info("✅ Team Engine ready")
    
    def create_team(self, data: Dict) -> Dict:
        """
        Create a team.
        data = {"company_name": str, "admin_email": str, "admin_name": str}
        """
        team_id = f"TEAM-{secrets.token_hex(4).upper()}"
        
        team = {
            "team_id": team_id,
            "company_name": data.get("company_name"),
            "admin_email": data.get("admin_email"),
            "admin_name": data.get("admin_name"),
            "created_at": datetime.now().isoformat(),
            "member_count": 1
        }
        
        self.teams.append(team)
        self.members.append({
            "member_id": f"MEM-{secrets.token_hex(4).upper()}",
            "team_id": team_id,
            "name": data.get("admin_name"),
            "email": data.get("admin_email"),
            "role": TeamRole.ADMIN,
            "joined_at": datetime.now().isoformat()
        })
        
        return {
            "status": "success",
            "team_id": team_id,
            "message": "Team created! Invite your first member.",
            "invite_link": f"https://charvakit.com/team/join/{team_id}"
        }
    
    def invite_member(self, data: Dict) -> Dict:
        """
        Invite a team member.
        data = {"team_id": str, "name": str, "email": str, "role": str}
        """
        team = self._find_team(data.get("team_id"))
        if not team:
            return {"status": "error", "message": "Team not found"}
        
        member_id = f"MEM-{secrets.token_hex(4).upper()}"
        
        member = {
            "member_id": member_id,
            "team_id": data.get("team_id"),
            "name": data.get("name"),
            "email": data.get("email"),
            "role": data.get("role", TeamRole.RECRUITER),
            "joined_at": datetime.now().isoformat()
        }
        
        self.members.append(member)
        team["member_count"] += 1
        
        return {
            "status": "success",
            "member_id": member_id,
            "message": f"{data.get('name')} invited to {team['company_name']}!"
        }
    
    def get_team(self, team_id: str) -> Dict:
        """Get team with members."""
        team = self._find_team(team_id)
        if not team:
            return {"status": "error", "message": "Team not found"}
        
        team_members = [m for m in self.members if m["team_id"] == team_id]
        
        return {
            "status": "success",
            "team": team,
            "members": team_members,
            "roles": [TeamRole.ADMIN, TeamRole.RECRUITER, TeamRole.VIEWER]
        }
    
    def update_member_role(self, member_id: str, new_role: str) -> Dict:
        """Update member's role."""
        for member in self.members:
            if member["member_id"] == member_id:
                member["role"] = new_role
                return {"status": "success", "message": f"Role updated to {new_role}"}
        return {"status": "error", "message": "Member not found"}
    
    def remove_member(self, member_id: str) -> Dict:
        """Remove a member from team."""
        for member in self.members:
            if member["member_id"] == member_id:
                team = self._find_team(member["team_id"])
                if team:
                    team["member_count"] -= 1
                self.members.remove(member)
                return {"status": "success", "message": "Member removed"}
        return {"status": "error", "message": "Member not found"}
    
    def get_stats(self) -> Dict:
        """Get team statistics."""
        return {
            "status": "success",
            "stats": {
                "total_teams": len(self.teams),
                "total_members": len(self.members),
                "admins": len([m for m in self.members if m["role"] == TeamRole.ADMIN]),
                "recruiters": len([m for m in self.members if m["role"] == TeamRole.RECRUITER]),
                "viewers": len([m for m in self.members if m["role"] == TeamRole.VIEWER])
            }
        }
    
    def _find_team(self, team_id: str) -> Optional[Dict]:
        for team in self.teams:
            if team["team_id"] == team_id:
                return team
        return None


team_engine = TeamEngine()