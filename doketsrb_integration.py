"""
Charvak ↔ DoketsRB Integration Engine
Deep links, cross-promotion, bundle pricing
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.doketsrb")


class DoketsRBIntegration:
    """Integration layer between Charvak and DoketsRB."""
    
    DOKETSRB_URL = "https://doketsrb.com"
    
    FEATURES = {
        "resume_builder": {"name": "AI Resume Builder", "url": f"{DOKETSRB_URL}/resume-builder", "free": True},
        "cover_letter": {"name": "Cover Letter Generator", "url": f"{DOKETSRB_URL}/cover-letter", "free": True},
        "linkedin_optimizer": {"name": "LinkedIn Profile Optimizer", "url": f"{DOKETSRB_URL}/linkedin", "free": True},
        "jd_parser": {"name": "JD Parser (ATS Tailor)", "url": f"{DOKETSRB_URL}/jd-parser", "free": True},
        "chrome_extension": {"name": "Chrome Extension", "url": f"{DOKETSRB_URL}/extension", "free": True},
    }
    
    BUNDLES = {
        "basic": {"name": "Basic", "price": 0, "includes": ["Charvak Free", "DoketsRB Free"]},
        "pro": {"name": "Pro Bundle", "price": 149, "includes": ["Charvak AI Assessment", "DoketsRB Premium"]},
        "enterprise": {"name": "Enterprise", "price": 999, "includes": ["Everything", "White-label", "API access"]},
    }
    
    def __init__(self):
        self.bundle_subscriptions = []
        logger.info("DoketsRB Integration ready")
    
    def get_deep_links(self) -> Dict:
        """Get all DoketsRB feature links for cross-promotion."""
        return {
            "status": "success",
            "doketsrb_url": self.DOKETSRB_URL,
            "features": self.FEATURES,
            "message": "DoketsRB features ready for integration"
        }
    
    def get_promotional_banner(self, context: str = "career") -> Dict:
        """
        Get promotional banner for Charvak pages.
        context: "resume" / "career" / "job" / "student"
        """
        banners = {
            "resume": {
                "title": "Need a resume? Try DoketsRB (Free)",
                "features": ["AI Resume Builder", "Cover Letter Generator", "LinkedIn Optimizer", "JD Parser"],
                "cta": "Build Your Resume →",
                "url": self.DOKETSRB_URL
            },
            "career": {
                "title": "Boost Your Career with DoketsRB",
                "features": ["ATS-Friendly Templates", "1-Click Apply", "LinkedIn Chrome Extension"],
                "cta": "Try DoketsRB Free →",
                "url": self.DOKETSRB_URL
            },
            "student": {
                "title": "Students: Build Your First Resume",
                "features": ["Free Templates", "AI Suggestions", "Cover Letter Generator"],
                "cta": "Start Free →",
                "url": self.DOKETSRB_URL
            }
        }
        
        banner = banners.get(context, banners["career"])
        return {"status": "success", "banner": banner}
    
    def subscribe_bundle(self, data: Dict) -> Dict:
        """
        Subscribe to Charvak + DoketsRB bundle.
        data = {email, bundle: "basic"/"pro"/"enterprise"}
        """
        bundle_key = data.get("bundle", "basic")
        bundle = self.BUNDLES.get(bundle_key, self.BUNDLES["basic"])
        
        subscription = {
            "subscription_id": f"BNDL-{secrets.token_hex(4).upper()}",
            "email": data.get("email"),
            "bundle": bundle_key,
            "bundle_name": bundle["name"],
            "price": bundle["price"],
            "includes": bundle["includes"],
            "subscribed_at": datetime.now().isoformat()
        }
        
        self.bundle_subscriptions.append(subscription)
        
        return {
            "status": "success",
            "subscription_id": subscription["subscription_id"],
            "bundle": bundle["name"],
            "price": bundle["price"],
            "message": f"Subscribed to {bundle['name']} bundle!"
        }
    
    def get_bundles(self) -> Dict:
        """Get all bundle options."""
        return {"status": "success", "bundles": self.BUNDLES}
    
    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "stats": {
                "total_bundle_subscriptions": len(self.bundle_subscriptions),
                "features_available": len(self.FEATURES)
            }
        }


doketsrb_integration = DoketsRBIntegration()