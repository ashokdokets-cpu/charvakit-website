"""
Charvak North America - Work Authorization Engine
Handles visa classification, compliance verification, and eligibility checks
"""
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class VisaType(Enum):
    US_CITIZEN = "US Citizen"
    GREEN_CARD = "Green Card (Permanent Resident)"
    H1B = "H-1B (Specialty Occupation)"
    H1B_TRANSFER = "H-1B Transfer"
    H4_EAD = "H-4 EAD"
    OPT = "OPT (F-1 Student)"
    OPT_STEM = "OPT STEM Extension"
    CPT = "CPT (Curricular Practical Training)"
    L1A = "L-1A (Intracompany Transfer)"
    L1B = "L-1B (Specialized Knowledge)"
    TN = "TN (USMCA/NAFTA Professional)"
    E3 = "E-3 (Australian Specialty)"
    O1 = "O-1 (Extraordinary Ability)"
    J1 = "J-1 (Exchange Visitor)"
    EAD_OTHER = "EAD (Other Category)"
    TPS = "Temporary Protected Status"
    ASYLUM = "Asylum Pending/Approved"
    DACA = "DACA"
    OTHER = "Other"

class WorkAuthStatus(Enum):
    VERIFIED = "Verified - Ready to Submit"
    PENDING_DOCS = "Pending - Documentation Required"
    EXPIRING = "Expiring Soon (within 90 days)"
    EXPIRED = "Expired - Cannot Submit"
    RESTRICTED = "Restricted - Client-Specific Only"
    NEEDS_REVIEW = "Needs Legal Review"

class ComplianceCheck(Enum):
    LCA_REQUIRED = "LCA (Labor Condition Application) Required"
    LCA_NOT_REQUIRED = "LCA Not Required"
    EXPORT_LICENSE = "Export License May Be Required"
    ITAR_RESTRICTED = "ITAR Restricted - US Citizens/GC Only"
    GOVT_CLEARANCE = "Government Clearance Required"
    STATE_RESTRICTIONS = "State-Level Restrictions Apply"
    EEOC_COMPLIANT = "EEOC Compliant"
    NYC_LAW_144 = "NYC Local Law 144 Compliant"

class WorkAuthorizationEngine:
    """Core work authorization verification system"""
    
    # Visa validity periods
    VISA_VALIDITY = {
        VisaType.US_CITIZEN: None,  # Permanent
        VisaType.GREEN_CARD: None,  # Permanent
        VisaType.H1B: 3,  # 3 years, renewable
        VisaType.H1B_TRANSFER: 3,
        VisaType.H4_EAD: 2,
        VisaType.OPT: 1,  # 1 year
        VisaType.OPT_STEM: 2,  # 2 years extension
        VisaType.CPT: 1,
        VisaType.L1A: 7,
        VisaType.L1B: 5,
        VisaType.TN: 3,
        VisaType.E3: 2,
        VisaType.O1: 3,
        VisaType.J1: 5,
        VisaType.EAD_OTHER: 2,
        VisaType.TPS: 1.5,
        VisaType.ASYLUM: None,
        VisaType.DACA: 2,
    }
    
    # Client restrictions mapping
    CLIENT_RESTRICTIONS = {
        "government": [
            VisaType.US_CITIZEN,
            VisaType.GREEN_CARD
        ],
        "defense": [
            VisaType.US_CITIZEN
        ],
        "healthcare": [
            VisaType.US_CITIZEN,
            VisaType.GREEN_CARD,
            VisaType.H1B,
            VisaType.H1B_TRANSFER,
            VisaType.OPT,
            VisaType.OPT_STEM,
            VisaType.EAD_OTHER,
            VisaType.TN,
        ],
        "corporate": None,  # All visa types accepted
        "startup": None,
    }
    
    def __init__(self):
        self.verified_candidates = {}
    
    def classify_visa(self, visa_input: str) -> VisaType:
        """Auto-classify visa type from raw input"""
        visa_lower = visa_input.lower().strip()
        
        classifications = {
            "citizen": VisaType.US_CITIZEN,
            "us citizen": VisaType.US_CITIZEN,
            "green card": VisaType.GREEN_CARD,
            "gc": VisaType.GREEN_CARD,
            "permanent resident": VisaType.GREEN_CARD,
            "h1b": VisaType.H1B,
            "h-1b": VisaType.H1B,
            "h1b transfer": VisaType.H1B_TRANSFER,
            "h-1b transfer": VisaType.H1B_TRANSFER,
            "h4 ead": VisaType.H4_EAD,
            "h-4 ead": VisaType.H4_EAD,
            "opt": VisaType.OPT,
            "opt stem": VisaType.OPT_STEM,
            "cpt": VisaType.CPT,
            "l1a": VisaType.L1A,
            "l-1a": VisaType.L1A,
            "l1b": VisaType.L1B,
            "l-1b": VisaType.L1B,
            "tn": VisaType.TN,
            "tn visa": VisaType.TN,
            "e3": VisaType.E3,
            "e-3": VisaType.E3,
            "o1": VisaType.O1,
            "o-1": VisaType.O1,
            "j1": VisaType.J1,
            "j-1": VisaType.J1,
            "ead": VisaType.EAD_OTHER,
            "tps": VisaType.TPS,
            "asylum": VisaType.ASYLUM,
            "daca": VisaType.DACA,
        }
        
        for key, visa_type in classifications.items():
            if key in visa_lower:
                return visa_type
        
        return VisaType.OTHER
    
    def check_work_auth_status(self, visa_type: VisaType, 
                                 visa_expiry: Optional[str] = None,
                                 documents_verified: bool = False) -> Dict:
        """Check current work authorization status"""
        
        # Permanent statuses
        if visa_type in [VisaType.US_CITIZEN, VisaType.GREEN_CARD, VisaType.ASYLUM]:
            return {
                "status": WorkAuthStatus.VERIFIED.value,
                "can_submit": True,
                "restrictions": [],
                "required_docs": ["Government ID"],
                "notes": "Permanent work authorization - no expiry"
            }
        
        # Check expiry for temporary visas
        if visa_expiry:
            try:
                expiry_date = datetime.strptime(visa_expiry, "%Y-%m-%d")
                days_remaining = (expiry_date - datetime.now()).days
                
                if days_remaining <= 0:
                    return {
                        "status": WorkAuthStatus.EXPIRED.value,
                        "can_submit": False,
                        "restrictions": ["Cannot submit - visa expired"],
                        "required_docs": ["Renewal notice or new visa"],
                        "notes": f"Visa expired {abs(days_remaining)} days ago"
                    }
                
                if days_remaining <= 90:
                    return {
                        "status": WorkAuthStatus.EXPIRING.value,
                        "can_submit": True,
                        "restrictions": ["Client must be informed of upcoming expiry"],
                        "required_docs": self._get_required_docs(visa_type),
                        "notes": f"Visa expires in {days_remaining} days"
                    }
            except:
                pass
        
        if not documents_verified:
            return {
                "status": WorkAuthStatus.PENDING_DOCS.value,
                "can_submit": False,
                "restrictions": ["Documents pending verification"],
                "required_docs": self._get_required_docs(visa_type),
                "notes": "Upload and verify all required documents"
            }
        
        return {
            "status": WorkAuthStatus.VERIFIED.value,
            "can_submit": True,
            "restrictions": [],
            "required_docs": self._get_required_docs(visa_type),
            "notes": "Ready for submission"
        }
    
    def _get_required_docs(self, visa_type: VisaType) -> List[str]:
        """Get required documentation list by visa type"""
        doc_map = {
            VisaType.US_CITIZEN: ["US Passport or Birth Certificate", "Government ID"],
            VisaType.GREEN_CARD: ["Green Card (Front/Back)", "Government ID"],
            VisaType.H1B: ["H-1B Approval Notice (I-797)", "I-94", "Passport", "Visa Stamp", "LCA Copy"],
            VisaType.H1B_TRANSFER: ["H-1B Transfer Receipt Notice", "Previous I-797", "I-94", "Passport"],
            VisaType.OPT: ["OPT EAD Card", "I-20", "I-94", "Passport"],
            VisaType.OPT_STEM: ["STEM OPT EAD Card", "I-20", "I-94", "Passport"],
            VisaType.CPT: ["CPT I-20", "I-94", "Passport"],
            VisaType.EAD_OTHER: ["EAD Card", "I-94", "Passport", "Approval Notice"],
            VisaType.TN: ["TN Support Letter", "I-94", "Passport"],
            VisaType.L1A: ["L-1A Approval Notice", "I-94", "Passport"],
            VisaType.L1B: ["L-1B Approval Notice", "I-94", "Passport"],
            VisaType.H4_EAD: ["H-4 EAD Card", "Spouse H-1B Approval", "I-94", "Passport"],
        }
        return doc_map.get(visa_type, ["Passport", "Work Authorization Document", "I-94"])
    
    def check_client_compatibility(self, visa_type: VisaType, 
                                     client_type: str) -> Dict:
        """Check if visa type is compatible with client requirements"""
        allowed_visas = self.CLIENT_RESTRICTIONS.get(client_type.lower())
        
        if allowed_visas is None:
            return {"compatible": True, "notes": "All visa types accepted"}
        
        if visa_type in allowed_visas:
            return {"compatible": True, "notes": f"Visa type accepted for {client_type} clients"}
        
        return {
            "compatible": False,
            "notes": f"{visa_type.value} not accepted for {client_type} contracts",
            "alternatives": [v.value for v in allowed_visas]
        }
    
    def get_compliance_requirements(self, visa_type: VisaType, 
                                      job_location: str = None) -> List[str]:
        """Get compliance requirements for submission"""
        requirements = []
        
        if visa_type in [VisaType.H1B, VisaType.H1B_TRANSFER]:
            requirements.append(ComplianceCheck.LCA_REQUIRED.value)
        
        if visa_type in [VisaType.US_CITIZEN, VisaType.GREEN_CARD]:
            requirements.append(ComplianceCheck.LCA_NOT_REQUIRED.value)
        
        if job_location and "NY" in job_location.upper():
            requirements.append(ComplianceCheck.NYC_LAW_144.value)
        
        requirements.append(ComplianceCheck.EEOC_COMPLIANT.value)
        
        return requirements
    
    def verify_candidate(self, candidate_id: str, visa_type: VisaType,
                         visa_expiry: str = None, documents_verified: bool = False,
                         client_type: str = "corporate") -> Dict:
        """Complete candidate work authorization verification"""
        
        auth_status = self.check_work_auth_status(visa_type, visa_expiry, documents_verified)
        compatibility = self.check_client_compatibility(visa_type, client_type)
        compliance = self.get_compliance_requirements(visa_type)
        
        result = {
            "candidate_id": candidate_id,
            "visa_type": visa_type.value,
            "visa_validity_years": self.VISA_VALIDITY.get(visa_type, "Unknown"),
            "auth_status": auth_status["status"],
            "can_submit": auth_status["can_submit"] and compatibility["compatible"],
            "compatibility": compatibility,
            "required_documents": auth_status["required_docs"],
            "compliance_requirements": compliance,
            "restrictions": auth_status["restrictions"],
            "verified_at": datetime.now().isoformat()
        }
        
        self.verified_candidates[candidate_id] = result
        return result

# Initialize engine
work_auth_engine = WorkAuthorizationEngine()