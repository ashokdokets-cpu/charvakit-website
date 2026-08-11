"""
Charvak Referral & Affiliate Engine
Handles referral tracking, bounty rewards, and affiliate commissions
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.referral")

REFERRAL_MODE = os.getenv("REFERRAL_MODE", "test")
DEFAULT_BOUNTY_INR = 500
DEFAULT_AFFILIATE_COMMISSION = 10  # percent


class ReferralStatus:
    PENDING = "pending"
    CLICKED = "clicked"
    SIGNED_UP = "signed_up"
    CONVERTED = "converted"
    PAID = "paid"
    EXPIRED = "expired"


class ReferralEngine:
    """Handles all referral and affiliate tracking."""
    
    def __init__(self):
        self.mode = REFERRAL_MODE
        self.referrals = []
        self.affiliates = []
        self.bounty_pool = []
        logger.info(f"✅ Referral Engine: {'LIVE' if self.mode == 'live' else 'TEST'} mode")
    
    # ============================================================
    # REFERRAL LINKS
    # ============================================================
    
    def create_referral_link(self, user_data: Dict) -> Dict:
        """
        Generate a unique referral link for a user.
        
        user_data = {
            "name": str,
            "email": str,
            "user_type": "candidate" or "employer" or "partner"
        }
        """
        referral_code = f"REF-{secrets.token_hex(4).upper()}"
        referral_link = f"https://charvakit.com/ref/{referral_code}"
        
        referral = {
            "referral_code": referral_code,
            "referral_link": referral_link,
            "referrer_name": user_data.get("name"),
            "referrer_email": user_data.get("email"),
            "user_type": user_data.get("user_type", "candidate"),
            "clicks": 0,
            "signups": 0,
            "conversions": 0,
            "total_earned": 0,
            "bounties": [],
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=365)).isoformat()
        }
        
        self.referrals.append(referral)
        logger.info(f"Referral link created: {referral_code} for {user_data.get('name')}")
        
        return {
            "status": "success",
            "referral_code": referral_code,
            "referral_link": referral_link,
            "share_text": f"Join Charvak IT Consulting and get hired! Use my referral: {referral_link}",
            "share_links": {
                "whatsapp": f"https://wa.me/?text=Join+Charvak+IT+Consulting!+Use+my+referral:+{referral_link}",
                "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={referral_link}",
                "twitter": f"https://twitter.com/intent/tweet?text=Join+Charvak+IT+Consulting!&url={referral_link}",
                "email": f"mailto:?subject=Join Charvak IT Consulting&body=Use my referral link: {referral_link}"
            }
        }
    
    def track_click(self, referral_code: str, source: str = "direct") -> Dict:
        """Track a referral link click."""
        for ref in self.referrals:
            if ref["referral_code"] == referral_code:
                ref["clicks"] += 1
                logger.info(f"Referral click: {referral_code} from {source}")
                return {"status": "success", "message": "Click tracked"}
        return {"status": "error", "message": "Invalid referral code"}
    
    def track_signup(self, referral_code: str, new_user_email: str) -> Dict:
        """Track a signup from a referral."""
        for ref in self.referrals:
            if ref["referral_code"] == referral_code:
                ref["signups"] += 1
                bounty_id = f"BOUNTY-{secrets.token_hex(4).upper()}"
                bounty = {
                    "bounty_id": bounty_id,
                    "referral_code": referral_code,
                    "referrer_email": ref["referrer_email"],
                    "new_user_email": new_user_email,
                    "amount_inr": DEFAULT_BOUNTY_INR,
                    "status": ReferralStatus.SIGNED_UP,
                    "created_at": datetime.now().isoformat(),
                    "paid_at": None
                }
                self.bounty_pool.append(bounty)
                ref["bounties"].append(bounty_id)
                
                logger.info(f"Signup from referral: {referral_code} → {new_user_email}")
                
                return {
                    "status": "success",
                    "bounty_id": bounty_id,
                    "message": f"Signup tracked! Bounty of ₹{DEFAULT_BOUNTY_INR} will be credited upon conversion."
                }
        return {"status": "error", "message": "Invalid referral code"}
    
    def mark_conversion(self, bounty_id: str) -> Dict:
        """Mark a referral as converted (placed/paid)."""
        for bounty in self.bounty_pool:
            if bounty["bounty_id"] == bounty_id:
                bounty["status"] = ReferralStatus.CONVERTED
                for ref in self.referrals:
                    if ref["referral_code"] == bounty["referral_code"]:
                        ref["conversions"] += 1
                        ref["total_earned"] += bounty["amount_inr"]
                
                logger.info(f"✅ Referral converted: {bounty_id}")
                
                return {
                    "status": "success",
                    "bounty_id": bounty_id,
                    "amount": bounty["amount_inr"],
                    "message": f"Referral converted! ₹{bounty['amount_inr']} bounty earned."
                }
        return {"status": "error", "message": "Bounty not found"}
    
    def pay_bounty(self, bounty_id: str) -> Dict:
        """Mark a bounty as paid."""
        for bounty in self.bounty_pool:
            if bounty["bounty_id"] == bounty_id:
                bounty["status"] = ReferralStatus.PAID
                bounty["paid_at"] = datetime.now().isoformat()
                
                logger.info(f"💰 Bounty paid: {bounty_id} | ₹{bounty['amount_inr']}")
                
                return {
                    "status": "success",
                    "bounty_id": bounty_id,
                    "amount_paid": bounty["amount_inr"],
                    "paid_to": bounty["referrer_email"],
                    "message": "Bounty paid successfully"
                }
        return {"status": "error", "message": "Bounty not found"}
    
    # ============================================================
    # AFFILIATE PROGRAM
    # ============================================================
    
    def register_affiliate(self, affiliate_data: Dict) -> Dict:
        """
        Register as an affiliate partner.
        
        affiliate_data = {
            "name": str,
            "email": str,
            "website": str,
            "platform": str
        }
        """
        affiliate_id = f"AFF-{secrets.token_hex(4).upper()}"
        
        affiliate = {
            "affiliate_id": affiliate_id,
            "name": affiliate_data.get("name"),
            "email": affiliate_data.get("email"),
            "website": affiliate_data.get("website", ""),
            "platform": affiliate_data.get("platform", ""),
            "commission_percent": DEFAULT_AFFILIATE_COMMISSION,
            "total_clicks": 0,
            "total_conversions": 0,
            "total_earned": 0,
            "status": "active",
            "referral_code": f"REF-{secrets.token_hex(4).upper()}",
            "created_at": datetime.now().isoformat()
        }
        
        affiliate["referral_link"] = f"https://charvakit.com/ref/{affiliate['referral_code']}"
        self.affiliates.append(affiliate)
        
        logger.info(f"Affiliate registered: {affiliate_id} - {affiliate_data.get('name')}")
        
        return {
            "status": "success",
            "affiliate_id": affiliate_id,
            "referral_link": affiliate["referral_link"],
            "commission": f"{DEFAULT_AFFILIATE_COMMISSION}%",
            "message": "Affiliate registered successfully!"
        }
    
    # ============================================================
    # DASHBOARD
    # ============================================================
    
    def get_referrer_stats(self, email: str) -> Dict:
        """Get stats for a specific referrer."""
        for ref in self.referrals:
            if ref["referrer_email"] == email:
                user_bounties = [b for b in self.bounty_pool if b["referral_code"] == ref["referral_code"]]
                return {
                    "status": "success",
                    "referral": ref,
                    "bounties": user_bounties,
                    "pending_bounties": len([b for b in user_bounties if b["status"] == ReferralStatus.SIGNED_UP]),
                    "converted_bounties": len([b for b in user_bounties if b["status"] == ReferralStatus.CONVERTED]),
                    "paid_bounties": len([b for b in user_bounties if b["status"] == ReferralStatus.PAID])
                }
        return {"status": "error", "message": "No referral found for this email"}
    
    def get_stats(self) -> Dict:
        """Get referral system statistics."""
        total_bounties = len(self.bounty_pool)
        pending = len([b for b in self.bounty_pool if b["status"] == ReferralStatus.SIGNED_UP])
        converted = len([b for b in self.bounty_pool if b["status"] == ReferralStatus.CONVERTED])
        paid = len([b for b in self.bounty_pool if b["status"] == ReferralStatus.PAID])
        total_payout = sum(b["amount_inr"] for b in self.bounty_pool if b["status"] == ReferralStatus.PAID)
        
        return {
            "status": "success",
            "stats": {
                "total_referrers": len(self.referrals),
                "total_affiliates": len(self.affiliates),
                "total_bounties": total_bounties,
                "pending_bounties": pending,
                "converted_bounties": converted,
                "paid_bounties": paid,
                "total_payout_inr": total_payout,
                "default_bounty": DEFAULT_BOUNTY_INR
            }
        }
    
    def get_leaderboard(self, limit: int = 10) -> Dict:
        """Get top referrers leaderboard."""
        sorted_refs = sorted(self.referrals, key=lambda r: r["total_earned"], reverse=True)[:limit]
        return {
            "status": "success",
            "leaderboard": [
                {
                    "rank": i + 1,
                    "name": ref["referrer_name"],
                    "conversions": ref["conversions"],
                    "earned": ref["total_earned"]
                }
                for i, ref in enumerate(sorted_refs) if ref["conversions"] > 0
            ]
        }


# ============================================================
# SINGLETON
# ============================================================
referral_engine = ReferralEngine()