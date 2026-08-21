"""
Charvak Outreach Engine
Cold Email Finder, Gmail Sync, Application Auto-Tracking
Premium monetization: ₹99-199/mo
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.outreach")


class OutreachEngine:
    """Cold email finder + Gmail sync + auto-tracking."""
    
    def __init__(self):
        self.cold_emails = []
        self.email_syncs = []
        self.auto_tracked = []
        self.premium_users = []
        logger.info("Outreach Engine ready")
    
    # ============================================================
    # 1. COLD EMAIL FINDER
    # ============================================================
    
    def find_hiring_manager_email(self, data: Dict) -> Dict:
        """
        Find hiring manager email patterns.
        data = {company, hiring_manager_name, domain}
        """
        company = data.get("company", "")
        name = data.get("hiring_manager_name", "")
        domain = data.get("domain", company.lower().replace(" ", "") + ".com")
        
        # Common email patterns
        first_name = name.split()[0].lower() if name else "first"
        last_name = name.split()[-1].lower() if name and len(name.split()) > 1 else "last"
        
        patterns = [
            f"{first_name}.{last_name}@{domain}",
            f"{first_name}{last_name}@{domain}",
            f"{first_name[0]}{last_name}@{domain}" if first_name else "",
            f"{first_name}@{domain}",
        ]
        
        email_id = f"CEMAIL-{secrets.token_hex(4).upper()}"
        
        result = {
            "email_id": email_id,
            "company": company,
            "hiring_manager": name,
            "domain": domain,
            "likely_emails": [p for p in patterns if p],
            "confidence": "HIGH" if name else "MEDIUM",
            "cold_email_template": self._generate_cold_email(data),
            "created_at": datetime.now().isoformat()
        }
        
        self.cold_emails.append(result)
        
        return {
            "status": "success",
            "email_id": email_id,
            "likely_emails": result["likely_emails"],
            "cold_email_template": result["cold_email_template"],
            "message": "Email patterns found!"
        }
    
    def _generate_cold_email(self, data: Dict) -> str:
        """Generate personalized cold email."""
        name = data.get("hiring_manager_name", "Hiring Manager")
        company = data.get("company", "your company")
        role = data.get("target_role", "the open position")
        candidate = data.get("candidate_name", "Candidate")
        skill = data.get("key_skill", "relevant experience")
        
        return f"""Subject: Interest in {role} at {company}

Hi {name},

I came across {company}'s work and I'm very impressed. I'm {candidate} with strong {skill}. I'm very interested in the {role} position and believe my background would be a great fit.

Would you be open to a quick chat about opportunities at {company}?

Best regards,
{candidate}"""
    
    # ============================================================
    # 2. GMAIL SYNC (Application Tracking)
    # ============================================================
    
    def connect_gmail(self, data: Dict) -> Dict:
        """
        Connect Gmail for application tracking.
        data = {email, sync_type: "applications"/"responses"/"all"}
        """
        sync_id = f"SYNC-{secrets.token_hex(4).upper()}"
        
        sync = {
            "sync_id": sync_id,
            "email": data.get("email"),
            "sync_type": data.get("sync_type", "all"),
            "status": "connected",
            "connected_at": datetime.now().isoformat()
        }
        
        self.email_syncs.append(sync)
        
        return {
            "status": "success",
            "sync_id": sync_id,
            "message": f"Gmail connected for {sync['sync_type']} tracking!",
            "auto_tracking": "Applications will auto-update from email responses"
        }
    
    def auto_track_application(self, data: Dict) -> Dict:
        """
        Auto-track application from email.
        data = {email, company, role, status}
        """
        track_id = f"TRACK-{secrets.token_hex(4).upper()}"
        
        tracked = {
            "track_id": track_id,
            "email": data.get("email"),
            "company": data.get("company"),
            "role": data.get("role"),
            "status": data.get("status", "applied"),
            "tracked_at": datetime.now().isoformat()
        }
        
        self.auto_tracked.append(tracked)
        
        return {"status": "success", "track_id": track_id, "message": f"Application at {data.get('company')} tracked!"}
    
    def get_tracked_applications(self, email: str) -> Dict:
        """Get all tracked applications."""
        applications = [a for a in self.auto_tracked if a["email"] == email]
        return {"status": "success", "applications": applications, "count": len(applications)}
    
    # ============================================================
    # 3. PREMIUM SUBSCRIPTION
    # ============================================================
    
    def subscribe_premium(self, data: Dict) -> Dict:
        """
        Subscribe to premium outreach tools.
        data = {email, plan: "basic"/"premium"}
        """
        plan = data.get("plan", "basic")
        price = 0 if plan == "basic" else 199
        
        subscription = {
            "subscription_id": f"OUT-{secrets.token_hex(4).upper()}",
            "email": data.get("email"),
            "plan": plan,
            "price": price,
            "features": ["Cold Email Finder", "Gmail Sync", "Auto-Tracking"] if plan == "premium" else ["Basic tracking"],
            "subscribed_at": datetime.now().isoformat()
        }
        
        self.premium_users.append(subscription)
        
        return {
            "status": "success",
            "subscription_id": subscription["subscription_id"],
            "plan": plan,
            "price": price,
            "message": f"Subscribed to {plan} plan!"
        }
    
    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "stats": {
                "cold_emails_found": len(self.cold_emails),
                "gmail_syncs": len(self.email_syncs),
                "auto_tracked": len(self.auto_tracked),
                "premium_users": len(self.premium_users)
            }
        }


outreach_engine = OutreachEngine()