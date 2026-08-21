"""
Charvak Profile & Network Engine
Unified Master Profile + Advanced Networking
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.profilenetwork")


class ProfileNetworkEngine:
    """Unified profile + advanced networking."""
    
    def __init__(self):
        self.master_profiles = []
        self.alumni_connections = []
        self.referral_matches = []
        self.network_tracker = []
        logger.info("Profile & Network Engine ready")
    
    # ============================================================
    # MASTER PROFILE (Unified)
    # ============================================================
    
    def create_master_profile(self, data: Dict) -> Dict:
        """
        Create unified master profile.
        Pulls from candidate_engine and adds unified view.
        """
        profile_id = f"MP-{secrets.token_hex(4).upper()}"
        
        # Try to get existing candidate data
        from candidate_engine import candidate_engine
        existing = candidate_engine.get_candidate_by_email(data.get("email"))
        
        master_profile = {
            "profile_id": profile_id,
            "email": data.get("email"),
            "candidate_data": existing or {},
            "assessments": [],
            "applications": [],
            "courses": [],
            "network": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.master_profiles.append(master_profile)
        
        return {
            "status": "success",
            "profile_id": profile_id,
            "message": "Master profile created! All your data in one place.",
            "profile": master_profile
        }
    
    def update_master_profile(self, email: str, update_data: Dict) -> Dict:
        """Update master profile with any new data."""
        profile = self._find_profile(email)
        if not profile:
            return {"status": "error", "message": "Profile not found"}
        
        profile.update(update_data)
        profile["updated_at"] = datetime.now().isoformat()
        
        return {"status": "success", "message": "Profile updated", "profile": profile}
    
    def get_master_profile(self, email: str) -> Dict:
        """Get unified master profile."""
        profile = self._find_profile(email)
        if not profile:
            return {"status": "error", "message": "Profile not found"}
        return {"status": "success", "profile": profile}
    
    # ============================================================
    # ALUMNI NETWORK
    # ============================================================
    
    def add_alumni_connection(self, data: Dict) -> Dict:
        """
        Add alumni connection.
        data = {university, name, email, company, role}
        """
        connection_id = f"ALUM-{secrets.token_hex(4).upper()}"
        
        connection = {
            "connection_id": connection_id,
            "university": data.get("university"),
            "name": data.get("name"),
            "email": data.get("email"),
            "company": data.get("company"),
            "role": data.get("role"),
            "created_at": datetime.now().isoformat()
        }
        
        self.alumni_connections.append(connection)
        
        return {"status": "success", "connection_id": connection_id, "message": "Alumni connection added!"}
    
    def find_alumni(self, university: str = None, company: str = None) -> Dict:
        """Find alumni by university or company."""
        alumni = self.alumni_connections
        
        if university:
            alumni = [a for a in alumni if a["university"] == university]
        if company:
            alumni = [a for a in alumni if a["company"] == company]
        
        return {"status": "success", "alumni": alumni, "count": len(alumni)}
    
    # ============================================================
    # REFERRAL MATCHMAKING
    # ============================================================
    
    def find_referral_match(self, data: Dict) -> Dict:
        """
        Find who can refer you at a company.
        data = {target_company, candidate_email}
        """
        target_company = data.get("target_company", "")
        
        matches = [
            a for a in self.alumni_connections 
            if a["company"] == target_company
        ]
        
        return {
            "status": "success",
            "target_company": target_company,
            "matches": matches,
            "count": len(matches),
            "message": f"Found {len(matches)} potential referrers at {target_company}!" if matches else f"No referrers found at {target_company}"
        }
    
    # ============================================================
    # NETWORK TRACKER
    # ============================================================
    
    def track_connection(self, data: Dict) -> Dict:
        """
        Track a LinkedIn connection.
        data = {email, connection_name, company, status}
        """
        track_id = f"NET-{secrets.token_hex(4).upper()}"
        
        connection = {
            "track_id": track_id,
            "email": data.get("email"),
            "connection_name": data.get("connection_name"),
            "company": data.get("company"),
            "status": data.get("status", "pending"),
            "tracked_at": datetime.now().isoformat()
        }
        
        self.network_tracker.append(connection)
        
        return {"status": "success", "track_id": track_id, "message": "Connection tracked!"}
    
    def get_network(self, email: str) -> Dict:
        """Get user's network."""
        connections = [c for c in self.network_tracker if c["email"] == email]
        return {"status": "success", "connections": connections, "count": len(connections)}
    
    # ============================================================
    # AUTO-OUTREACH TEMPLATES
    # ============================================================
    
    def generate_outreach_template(self, data: Dict) -> Dict:
        """
        Generate personalized outreach message.
        data = {connection_name, company, role, candidate_name, university}
        """
        template = f"""Hi {data.get('connection_name')},

I came across your profile and noticed you work at {data.get('company')} as {data.get('role')}. I'm {data.get('candidate_name')} from {data.get('university', 'the same university')} and I'm very interested in opportunities at {data.get('company')}.

Would you be open to a quick chat about your experience there?

Best regards,
{data.get('candidate_name')}"""
        
        return {
            "status": "success",
            "template": template,
            "message": "Outreach template generated!"
        }
    
    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "stats": {
                "master_profiles": len(self.master_profiles),
                "alumni_connections": len(self.alumni_connections),
                "network_tracked": len(self.network_tracker),
                "referral_matches": len(self.referral_matches)
            }
        }
    
    def _find_profile(self, email: str):
        for profile in self.master_profiles:
            if profile["email"] == email:
                return profile
        return None


profile_network_engine = ProfileNetworkEngine()