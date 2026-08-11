"""
Charvak KYC & Verification Engine
Handles identity verification, background checks, and partner onboarding
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets
import hashlib

logger = logging.getLogger("charvakit.kyc")

# ============================================================
# CONFIGURATION
# ============================================================
KYC_MODE = os.getenv("KYC_MODE", "test")  # "test" or "live"
DIGILOCKER_CLIENT_ID = os.getenv("DIGILOCKER_CLIENT_ID", "")
DIGILOCKER_CLIENT_SECRET = os.getenv("DIGILOCKER_CLIENT_SECRET", "")


class VerificationStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DOCUMENTS_REQUESTED = "documents_requested"
    DOCUMENTS_SUBMITTED = "documents_submitted"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class VerificationType:
    IDENTITY = "identity"
    EDUCATION = "education"
    EMPLOYMENT = "employment"
    CRIMINAL = "criminal"
    CREDIT = "credit"
    COMPLETE = "complete"


class KYC_Engine:
    """Handles all KYC and background verification workflows."""
    
    def __init__(self):
        self.mode = KYC_MODE
        self.verifications = []
        self.partners = []
        self.verified_users = []
        
        if self.mode == "live":
            logger.info("✅ KYC Engine: LIVE mode")
        else:
            logger.info("⚠️ KYC Engine: TEST mode — simulated verifications")
    
    # ============================================================
    # VERIFICATION PRICING
    # ============================================================
    
    PRICING = {
        VerificationType.IDENTITY: {"inr": 499, "usd": 6, "name": "Identity Verification"},
        VerificationType.EDUCATION: {"inr": 799, "usd": 10, "name": "Education Verification"},
        VerificationType.EMPLOYMENT: {"inr": 999, "usd": 12, "name": "Employment Verification"},
        VerificationType.CRIMINAL: {"inr": 1499, "usd": 18, "name": "Criminal Record Check"},
        VerificationType.CREDIT: {"inr": 1299, "usd": 16, "name": "Credit & Financial Check"},
        VerificationType.COMPLETE: {"inr": 3999, "usd": 49, "name": "Complete Global Package"},
    }
    
    # ============================================================
    # VERIFICATION WORKFLOW
    # ============================================================
    
    def initiate_verification(self, user_data: Dict) -> Dict:
        """
        Start a new verification request.
        
        user_data = {
            "name": str,
            "email": str,
            "phone": str,
            "verification_type": str,  # identity/education/employment/criminal/credit/complete
            "country": str,
            "documents": List[str],  # Optional: list of document types to verify
            "notes": str
        }
        """
        verification_id = f"VERIFY-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        verification_type = user_data.get("verification_type", VerificationType.IDENTITY)
        
        record = {
            "verification_id": verification_id,
            "user_name": user_data.get("name"),
            "user_email": user_data.get("email"),
            "user_phone": user_data.get("phone"),
            "verification_type": verification_type,
            "country": user_data.get("country", "India"),
            "documents_requested": self._get_required_docs(verification_type, user_data.get("country", "India")),
            "documents_submitted": [],
            "status": VerificationStatus.PENDING,
            "price_inr": self.PRICING.get(verification_type, {}).get("inr", 499),
            "price_usd": self.PRICING.get(verification_type, {}).get("usd", 6),
            "payment_status": "pending",
            "payment_order_id": None,
            "assigned_to": None,
            "results": {},
            "notes": user_data.get("notes", ""),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None,
            "valid_until": (datetime.now() + timedelta(days=365)).isoformat()
        }
        
        self.verifications.append(record)
        logger.info(f"Verification initiated: {verification_id} for {user_data.get('name')} - {verification_type}")
        
        return {
            "status": "success",
            "verification_id": verification_id,
            "message": f"Verification initiated for {verification_type}. Our team will contact you within 24 hours.",
            "next_steps": [
                "Check your email for document submission instructions",
                "Upload required documents via the secure portal link",
                "Verification typically takes 24-72 hours"
            ],
            "documents_required": record["documents_requested"],
            "price_inr": record["price_inr"],
            "valid_until": record["valid_until"]
        }
    
    def submit_documents(self, verification_id: str, documents: List[Dict]) -> Dict:
        """
        Submit documents for verification.
        
        documents = [
            {"type": "aadhaar", "file_url": "/uploads/doc1.pdf"},
            {"type": "pan", "file_url": "/uploads/doc2.pdf"}
        ]
        """
        for v in self.verifications:
            if v["verification_id"] == verification_id:
                v["documents_submitted"] = documents
                v["status"] = VerificationStatus.DOCUMENTS_SUBMITTED
                v["updated_at"] = datetime.now().isoformat()
                logger.info(f"Documents submitted for {verification_id}: {len(documents)} files")
                return {
                    "status": "success",
                    "verification_id": verification_id,
                    "message": f"{len(documents)} documents submitted successfully",
                    "status": v["status"],
                    "estimated_completion": (datetime.now() + timedelta(hours=48)).isoformat()
                }
        
        return {"status": "error", "message": "Verification ID not found"}
    
    def get_verification_status(self, verification_id: str) -> Dict:
        """Check the status of a verification."""
        for v in self.verifications:
            if v["verification_id"] == verification_id:
                return {
                    "status": "success",
                    "verification": v
                }
        return {"status": "error", "message": "Verification ID not found"}
    
    def get_user_verifications(self, email: str) -> Dict:
        """Get all verifications for a user."""
        user_verifications = [v for v in self.verifications if v.get("user_email") == email]
        return {
            "status": "success",
            "verifications": user_verifications,
            "count": len(user_verifications),
            "has_valid_verification": any(
                v["status"] == VerificationStatus.VERIFIED and 
                datetime.fromisoformat(v["valid_until"]) > datetime.now()
                for v in user_verifications
            )
        }
    
    def review_verification(self, verification_id: str, result: Dict) -> Dict:
        """
        Admin/Partner reviews a verification.
        
        result = {
            "status": "verified" or "rejected",
            "checked_by": "partner_id",
            "findings": {...},
            "notes": str
        }
        """
        for v in self.verifications:
            if v["verification_id"] == verification_id:
                v["status"] = result.get("status", VerificationStatus.REJECTED)
                v["results"] = result.get("findings", {})
                v["assigned_to"] = result.get("checked_by")
                v["notes"] = result.get("notes", v["notes"])
                v["updated_at"] = datetime.now().isoformat()
                
                if v["status"] == VerificationStatus.VERIFIED:
                    v["completed_at"] = datetime.now().isoformat()
                    v["valid_until"] = (datetime.now() + timedelta(days=365)).isoformat()
                    self._add_verified_user(v)
                    logger.info(f"✅ Verification approved: {verification_id}")
                else:
                    logger.info(f"❌ Verification rejected: {verification_id}")
                
                return {
                    "status": "success",
                    "verification_id": verification_id,
                    "result": v["status"],
                    "message": f"Verification {v['status']}"
                }
        
        return {"status": "error", "message": "Verification ID not found"}
    
    # ============================================================
    # VERIFIED USER MANAGEMENT
    # ============================================================
    
    def _add_verified_user(self, verification: Dict):
        """Add user to verified users list."""
        self.verified_users.append({
            "name": verification["user_name"],
            "email": verification["user_email"],
            "verification_id": verification["verification_id"],
            "verification_type": verification["verification_type"],
            "verified_at": datetime.now().isoformat(),
            "valid_until": verification["valid_until"],
            "badge_id": f"BADGE-{secrets.token_hex(4).upper()}"
        })
    
    def is_user_verified(self, email: str) -> Dict:
        """Check if a user is verified."""
        for user in self.verified_users:
            if user["email"] == email and datetime.fromisoformat(user["valid_until"]) > datetime.now():
                return {"status": "success", "verified": True, "badge": user}
        return {"status": "success", "verified": False}
    
    def get_verified_badge(self, email: str) -> Dict:
        """Get verified badge details."""
        for user in self.verified_users:
            if user["email"] == email:
                return {
                    "status": "success",
                    "badge": {
                        **user,
                        "share_url": f"https://charvakit.com/badge?ref={user['badge_id']}",
                        "linkedin_share": f"https://www.linkedin.com/profile/add?certId={user['badge_id']}"
                    }
                }
        return {"status": "error", "message": "No verified badge found"}
    
    # ============================================================
    # PARTNER MANAGEMENT
    # ============================================================
    
    def register_partner(self, partner_data: Dict) -> Dict:
        """
        Register a verification partner.
        
        partner_data = {
            "agency_name": str,
            "contact_person": str,
            "email": str,
            "phone": str,
            "services": List[str],
            "coverage": str
        }
        """
        partner_id = f"PARTNER-{secrets.token_hex(4).upper()}"
        
        partner = {
            "partner_id": partner_id,
            "agency_name": partner_data.get("agency_name"),
            "contact_person": partner_data.get("contact_person"),
            "email": partner_data.get("email"),
            "phone": partner_data.get("phone"),
            "services": partner_data.get("services", []),
            "coverage": partner_data.get("coverage", ""),
            "status": "pending_review",
            "verifications_completed": 0,
            "revenue_earned": 0,
            "rating": None,
            "registered_at": datetime.now().isoformat(),
            "approved_at": None
        }
        
        self.partners.append(partner)
        logger.info(f"New partner registered: {partner_id} - {partner_data.get('agency_name')}")
        
        return {
            "status": "success",
            "partner_id": partner_id,
            "message": "Partner application submitted! We will review and contact you within 48 hours.",
            "next_steps": [
                "Our team will review your application",
                "You'll receive an onboarding email with API access",
                "Start receiving verification requests from our career pipeline"
            ]
        }
    
    def approve_partner(self, partner_id: str) -> Dict:
        """Admin approves a partner."""
        for partner in self.partners:
            if partner["partner_id"] == partner_id:
                partner["status"] = "active"
                partner["approved_at"] = datetime.now().isoformat()
                return {"status": "success", "message": f"Partner {partner_id} approved"}
        return {"status": "error", "message": "Partner not found"}
    
    def get_partners(self, status: str = None) -> Dict:
        """Get all partners, optionally filtered by status."""
        if status:
            filtered = [p for p in self.partners if p["status"] == status]
        else:
            filtered = self.partners
        
        return {
            "status": "success",
            "partners": filtered,
            "count": len(filtered),
            "active_count": len([p for p in self.partners if p["status"] == "active"])
        }
    
    def assign_verification_to_partner(self, verification_id: str, partner_id: str) -> Dict:
        """Assign a verification job to a partner."""
        for v in self.verifications:
            if v["verification_id"] == verification_id:
                for p in self.partners:
                    if p["partner_id"] == partner_id and p["status"] == "active":
                        v["assigned_to"] = partner_id
                        v["status"] = VerificationStatus.UNDER_REVIEW
                        v["updated_at"] = datetime.now().isoformat()
                        p["verifications_completed"] += 1
                        return {
                            "status": "success",
                            "message": f"Verification {verification_id} assigned to {p['agency_name']}"
                        }
                return {"status": "error", "message": "Partner not found or not active"}
        return {"status": "error", "message": "Verification ID not found"}
    
    # ============================================================
    # DASHBOARD & STATS
    # ============================================================
    
    def get_stats(self) -> Dict:
        """Get KYC system statistics."""
        total = len(self.verifications)
        pending = len([v for v in self.verifications if v["status"] in [VerificationStatus.PENDING, VerificationStatus.IN_PROGRESS]])
        verified = len([v for v in self.verifications if v["status"] == VerificationStatus.VERIFIED])
        rejected = len([v for v in self.verifications if v["status"] == VerificationStatus.REJECTED])
        total_revenue = sum(v["price_inr"] for v in self.verifications if v.get("payment_status") == "completed")
        
        return {
            "status": "success",
            "stats": {
                "total_verifications": total,
                "pending": pending,
                "verified": verified,
                "rejected": rejected,
                "total_revenue_inr": total_revenue,
                "active_partners": len([p for p in self.partners if p["status"] == "active"]),
                "verified_users": len(self.verified_users)
            }
        }
    
    # ============================================================
    # HELPERS
    # ============================================================
    
    def _get_required_docs(self, verification_type: str, country: str) -> List[str]:
        """Get required documents based on verification type and country."""
        docs = {
            VerificationType.IDENTITY: {
                "India": ["Aadhaar Card", "PAN Card", "Passport"],
                "USA": ["Social Security Card", "Passport", "Driver's License"],
                "default": ["Government ID", "Passport", "Utility Bill"]
            },
            VerificationType.EDUCATION: {
                "default": ["Degree Certificate", "Transcripts", "Institution Name & Dates"]
            },
            VerificationType.EMPLOYMENT: {
                "default": ["Offer Letter", "Relieving Letter", "Salary Slips (last 3 months)"]
            },
            VerificationType.CRIMINAL: {
                "India": ["Aadhaar Card", "Address Proof"],
                "USA": ["FBI Background Check Consent Form", "SSN"],
                "default": ["National ID", "Police Clearance Application"]
            },
            VerificationType.CREDIT: {
                "India": ["PAN Card", "CIBIL Consent Form"],
                "USA": ["SSN", "Credit Check Authorization"],
                "default": ["National ID", "Credit Bureau Authorization"]
            },
            VerificationType.COMPLETE: {
                "default": ["All documents from Identity + Education + Employment checks"]
            }
        }
        
        country_docs = docs.get(verification_type, {}).get(country)
        if not country_docs:
            country_docs = docs.get(verification_type, {}).get("default", ["Government ID", "Passport"])
        
        return country_docs


# ============================================================
# SINGLETON
# ============================================================
kyc_engine = KYC_Engine()