"""
Charvak North America - Resume Processing Engine
Bulk resume ingestion, PII redaction, and compliance checking
"""
import re
import json
import hashlib
from typing import Dict, List, Tuple
from datetime import datetime

class PIIRedactor:
    """Automated PII redaction for candidate protection"""
    
    # PII patterns to redact
    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "address": r'\b\d{1,5}\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Court|Ct)\b',
    }
    
    def __init__(self):
        self.redaction_log = []
    
    def redact_text(self, text: str, candidate_id: str) -> Tuple[str, Dict]:
        """Redact PII from text and return redacted version + log"""
        redacted = text
        redactions = {}
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, redacted, re.IGNORECASE)
            if matches:
                redactions[pii_type] = len(matches)
                for match in matches:
                    redacted = redacted.replace(match, f"[REDACTED {pii_type.upper()}]")
        
        # Log the redaction
        log_entry = {
            "candidate_id": candidate_id,
            "timestamp": datetime.now().isoformat(),
            "redactions": redactions,
            "original_length": len(text),
            "redacted_length": len(redacted)
        }
        self.redaction_log.append(log_entry)
        
        return redacted, log_entry
    
    def generate_blind_profile(self, candidate_data: Dict) -> Dict:
        """Generate a dual-blind candidate profile"""
        
        # Extract only non-PII information
        blind_profile = {
            "candidate_id": hashlib.md5(candidate_data.get("email", "").encode()).hexdigest()[:8],
            "skills": candidate_data.get("skills", []),
            "total_experience_years": candidate_data.get("years_experience", 0),
            "education_level": self._extract_education(candidate_data),
            "visa_status": candidate_data.get("visa_type", "Not Specified"),
            "current_location": self._extract_location(candidate_data),
            "preferred_location": candidate_data.get("preferred_location", "Open"),
            "rate_expectation": candidate_data.get("rate", "Not Specified"),
            "availability": candidate_data.get("availability", "Immediate"),
            "top_skills": candidate_data.get("skills", [])[:5],
            "certifications": candidate_data.get("certifications", []),
        }
        
        return blind_profile
    
    def _extract_education(self, data: Dict) -> str:
        education = data.get("education", "")
        if "master" in education.lower(): return "Master's Degree"
        if "bachelor" in education.lower(): return "Bachelor's Degree"
        if "phd" in education.lower(): return "PhD"
        if "associate" in education.lower(): return "Associate's Degree"
        return "Not Specified"
    
    def _extract_location(self, data: Dict) -> str:
        location = data.get("location", "")
        # Only return city/state, not full address
        parts = location.split(",")
        if len(parts) >= 2:
            return f"{parts[0].strip()}, {parts[1].strip()}"
        return location

class ComplianceChecker:
    """North American compliance verification"""
    
    # EEOC compliance requirements
    EEOC_REQUIREMENTS = [
        "No discriminatory language in job description",
        "Equal opportunity employer statement included",
        "Reasonable accommodation notice present",
        "No age-restrictive terms (unless BFOQ)",
        "Gender-neutral language verified"
    ]
    
    # NYC Local Law 144 requirements (Automated Employment Decision Tools)
    NYC_LAW_144_REQUIREMENTS = [
        "Bias audit completed within last 12 months",
        "Bias audit summary publicly available",
        "Candidates notified of AI tool usage",
        "Alternative selection process available upon request",
        "Data retention policy documented",
        "Audit results published on company website"
    ]
    
    def __init__(self):
        self.compliance_reports = []
    
    def check_job_compliance(self, job_data: Dict) -> Dict:
        """Check job posting for EEOC compliance"""
        issues = []
        warnings = []
        
        title = job_data.get("title", "")
        description = job_data.get("description", "")
        
        # Check for discriminatory language
        age_restrictive = ["young", "fresh", "recent grad", "digital native", "max 5 years", "under 30"]
        for term in age_restrictive:
            if term in description.lower():
                issues.append(f"Age-restrictive term found: '{term}'")
        
        gender_biased = ["rockstar", "ninja", "guru", "aggressive", "dominant", "competitive"]
        for term in gender_biased:
            if term in description.lower():
                warnings.append(f"Potentially gender-biased term: '{term}'")
        
        # NYC-specific checks
        job_location = job_data.get("location", "")
        is_nyc = any(city in job_location.upper() for city in ["NY", "NEW YORK", "NYC"])
        
        result = {
            "job_id": job_data.get("job_id", "Unknown"),
            "eeoc_compliant": len(issues) == 0,
            "nyc_law_144_applicable": is_nyc,
            "issues": issues,
            "warnings": warnings,
            "checked_at": datetime.now().isoformat()
        }
        
        self.compliance_reports.append(result)
        return result
    
    def check_candidate_compliance(self, candidate_data: Dict) -> Dict:
        """Verify candidate submission meets compliance requirements"""
        
        work_auth = candidate_data.get("work_auth", {})
        visa_type = work_auth.get("visa_type", "Unknown")
        
        # Check for restricted visa types
        restricted_combinations = {
            "CPT": ["government", "defense"],
            "OPT": ["defense"],
            "H-1B": ["government"],
        }
        
        client_type = candidate_data.get("client_type", "corporate")
        restrictions = []
        
        for visa, restricted_clients in restricted_combinations.items():
            if visa in visa_type and client_type in restricted_clients:
                restrictions.append(f"{visa} not accepted for {client_type} contracts")
        
        return {
            "candidate_id": candidate_data.get("candidate_id", "Unknown"),
            "compliant": len(restrictions) == 0,
            "restrictions": restrictions,
            "checked_at": datetime.now().isoformat()
        }

class SubVendorManager:
    """Sub-vendor management and tracking"""
    
    def __init__(self):
        self.vendors = {}
        self.submissions = {}
    
    def register_vendor(self, vendor_data: Dict) -> Dict:
        """Register a new sub-vendor"""
        vendor_id = f"VEN-{hash(vendor_data.get('email', ''))}"
        
        self.vendors[vendor_id] = {
            "vendor_id": vendor_id,
            "name": vendor_data.get("name", "Unknown"),
            "tier": vendor_data.get("tier", "Tier-2"),
            "email": vendor_data.get("email"),
            "specialization": vendor_data.get("specialization", []),
            "active_candidates": 0,
            "successful_placements": 0,
            "registered_date": datetime.now().isoformat(),
            "status": "active"
        }
        
        return self.vendors[vendor_id]
    
    def track_submission(self, vendor_id: str, candidate_id: str, job_id: str) -> Dict:
        """Track a vendor's candidate submission"""
        if vendor_id not in self.vendors:
            return {"error": "Vendor not registered"}
        
        submission_key = f"{vendor_id}-{candidate_id}-{job_id}"
        self.submissions[submission_key] = {
            "vendor_id": vendor_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "submitted_at": datetime.now().isoformat(),
            "status": "submitted"
        }
        
        # Update vendor stats
        self.vendors[vendor_id]["active_candidates"] += 1
        
        return self.submissions[submission_key]
    
    def get_vendor_stats(self, vendor_id: str) -> Dict:
        """Get vendor performance statistics"""
        if vendor_id not in self.vendors:
            return {"error": "Vendor not found"}
        
        vendor_subs = {k: v for k, v in self.submissions.items() if v["vendor_id"] == vendor_id}
        
        return {
            "vendor": self.vendors[vendor_id],
            "total_submissions": len(vendor_subs),
            "active_submissions": len([s for s in vendor_subs.values() if s["status"] == "submitted"]),
            "placement_rate": self.vendors[vendor_id]["successful_placements"] / max(len(vendor_subs), 1) * 100
        }

# Initialize engines
pii_redactor = PIIRedactor()
compliance_checker = ComplianceChecker()
sub_vendor_manager = SubVendorManager()

print("✅ Resume Engine initialized")
print(f"   PII Redactor: {len(PIIRedactor.PII_PATTERNS)} patterns")
print(f"   Compliance: EEOC + NYC Law 144")
print(f"   Sub-Vendor Manager: Ready")