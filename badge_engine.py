"""
Charvak Badge & Certification Engine
Handles verified badges, skill certifications, and shareable credentials
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets
import hashlib

logger = logging.getLogger("charvakit.badges")


class BadgeLevel:
    VERIFIED = "verified"
    PREMIUM = "premium"
    EXPERT = "expert"
    MASTER = "master"


class BadgeEngine:
    """Handles all badges and certifications."""
    
    def __init__(self):
        self.badges = []
        self.certifications = []
        logger.info("✅ Badge Engine ready")
    
    BADGE_TYPES = {
        "skill_twin": {"name": "Skill-Twin Verified", "levels": [BadgeLevel.VERIFIED, BadgeLevel.PREMIUM]},
        "micro_internship": {"name": "Micro-Internship Complete", "levels": [BadgeLevel.VERIFIED]},
        "background_check": {"name": "Background Verified", "levels": [BadgeLevel.VERIFIED, BadgeLevel.PREMIUM]},
        "course_completion": {"name": "Course Certificate", "levels": [BadgeLevel.VERIFIED]},
        "top_performer": {"name": "Top Performer", "levels": [BadgeLevel.EXPERT, BadgeLevel.MASTER]},
    }
    
    BADGE_COLORS = {
        BadgeLevel.VERIFIED: "#3ba591",
        BadgeLevel.PREMIUM: "#6366f1",
        BadgeLevel.EXPERT: "#f59e0b",
        BadgeLevel.MASTER: "#ef4444",
    }
    
    def issue_badge(self, data: Dict) -> Dict:
        """
        Issue a badge to a user.
        
        data = {
            "user_name": str,
            "user_email": str,
            "badge_type": str,
            "level": str,
            "score": int (optional),
            "skills": List[str] (optional)
        }
        """
        badge_id = f"BADGE-{secrets.token_hex(6).upper()}"
        badge_type = data.get("badge_type", "skill_twin")
        level = data.get("level", BadgeLevel.VERIFIED)
        
        badge_info = self.BADGE_TYPES.get(badge_type, self.BADGE_TYPES["skill_twin"])
        
        badge = {
            "badge_id": badge_id,
            "badge_name": badge_info["name"],
            "level": level,
            "color": self.BADGE_COLORS.get(level, "#3ba591"),
            "user_name": data.get("user_name"),
            "user_email": data.get("user_email"),
            "score": data.get("score"),
            "skills": data.get("skills", []),
            "badge_type": badge_type,
            "issued_at": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=365)).isoformat(),
            "verification_hash": hashlib.sha256(f"{badge_id}:{data.get('user_email')}".encode()).hexdigest()[:16],
            "share_url": f"https://charvakit.com/badge?ref={badge_id}",
            "linkedin_url": f"https://www.linkedin.com/profile/add?startTask=CERTIFICATION_NAME&name={badge_info['name']}&organizationName=Charvak+IT+Consulting&issueYear={datetime.now().year}&certId={badge_id}"
        }
        
        self.badges.append(badge)
        logger.info(f"Badge issued: {badge_id} | {badge_info['name']} → {data.get('user_name')}")
        
        return {
            "status": "success",
            "badge": badge,
            "message": f"{badge_info['name']} badge issued!",
            "share_text": f"I just earned the {badge_info['name']} ({level}) from Charvak IT Consulting! 🏆"
        }
    
    def verify_badge(self, badge_id: str) -> Dict:
        """Verify a badge is authentic."""
        for badge in self.badges:
            if badge["badge_id"] == badge_id:
                is_valid = datetime.fromisoformat(badge["valid_until"]) > datetime.now()
                return {
                    "status": "success",
                    "verified": is_valid,
                    "badge": badge if is_valid else None,
                    "message": "Badge verified" if is_valid else "Badge expired"
                }
        return {"status": "error", "verified": False, "message": "Badge not found"}
    
    def get_user_badges(self, email: str) -> Dict:
        """Get all badges for a user."""
        user_badges = [
            b for b in self.badges 
            if b["user_email"] == email and datetime.fromisoformat(b["valid_until"]) > datetime.now()
        ]
        return {
            "status": "success",
            "badges": user_badges,
            "count": len(user_badges),
            "display": [
                {
                    "name": b["badge_name"],
                    "level": b["level"],
                    "color": b["color"],
                    "badge_id": b["badge_id"],
                    "share_url": b["share_url"]
                }
                for b in user_badges
            ]
        }
    
    def revoke_badge(self, badge_id: str) -> Dict:
        """Revoke a badge."""
        for badge in self.badges:
            if badge["badge_id"] == badge_id:
                badge["valid_until"] = datetime.now().isoformat()
                logger.info(f"Badge revoked: {badge_id}")
                return {"status": "success", "message": "Badge revoked"}
        return {"status": "error", "message": "Badge not found"}
    
    def get_stats(self) -> Dict:
        """Get badge statistics."""
        total = len(self.badges)
        active = len([b for b in self.badges if datetime.fromisoformat(b["valid_until"]) > datetime.now()])
        
        return {
            "status": "success",
            "stats": {
                "total_badges_issued": total,
                "active_badges": active,
                "badge_types": list(self.BADGE_TYPES.keys()),
                "users_badged": len(set(b["user_email"] for b in self.badges))
            }
        }


badge_engine = BadgeEngine()