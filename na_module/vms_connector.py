"""
Charvak North America - VMS Connector
Integrates with Fieldglass, Beeline, and Tier-1 Vendor Systems
"""
import os
import json
import httpx
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class VMSProvider(Enum):
    FIELDGLASS = "SAP Fieldglass"
    BEELINE = "Beeline"
    WAND = "WAND VMS"
    VNDLY = "Workday VNDLY"
    COUPA = "Coupa Contingent Workforce"
    PRO unlimited = "PRO Unlimited"
    CUSTOM = "Custom VMS"

class JobStatus(Enum):
    ACTIVE = "Active - Accepting Submissions"
    ON_HOLD = "On Hold"
    OFFERS_MADE = "Offers in Progress"
    FILLED = "Position Filled"
    CANCELLED = "Cancelled"
    EXPIRED = "Expired"

class VMSConnector:
    """Core VMS integration engine"""
    
    # VMS API configurations (to be filled with actual credentials)
    VMS_CONFIGS = {
        VMSProvider.FIELDGLASS: {
            "base_url": "https://api.fieldglass.com/v1",
            "auth_type": "oauth2",
            "rate_limit": "1000/hour"
        },
        VMSProvider.BEELINE: {
            "base_url": "https://api.beeline.com/v2",
            "auth_type": "api_key",
            "rate_limit": "500/hour"
        },
        VMSProvider.CUSTOM: {
            "base_url": os.getenv("CUSTOM_VMS_URL", ""),
            "auth_type": "custom",
            "rate_limit": "unlimited"
        }
    }
    
    def __init__(self):
        self.active_jobs = []
        self.submission_history = []
    
    def ingest_job_requirements(self, source: str, raw_data: Dict) -> Dict:
        """Ingest and standardize job requirements from any source"""
        
        # Standardize job format
        standardized_job = {
            "job_id": f"NA-JOB-{hash(str(raw_data))}",
            "source": source,
            "title": raw_data.get("title", "Unknown Role"),
            "client": raw_data.get("client", "Confidential"),
            "vms_provider": raw_data.get("vms_provider", "Direct"),
            "location": raw_data.get("location", "Remote"),
            "rate_range": {
                "min": raw_data.get("rate_min", 0),
                "max": raw_data.get("rate_max", 0),
                "type": raw_data.get("rate_type", "C2C")
            },
            "skills_required": raw_data.get("skills", []),
            "visa_restrictions": raw_data.get("visa_restrictions", []),
            "duration": raw_data.get("duration", "6 months"),
            "status": JobStatus.ACTIVE.value,
            "posted_date": raw_data.get("posted_date", datetime.now().isoformat()),
            "submission_deadline": raw_data.get("deadline", "ASAP"),
            "submission_limit": raw_data.get("submission_limit", 3),
            "interview_process": raw_data.get("interview_process", "Client Review → Technical → Offer"),
            "compliance_notes": raw_data.get("compliance_notes", "")
        }
        
        # Ghost job detection
        ghost_score = self._detect_ghost_job(standardized_job)
        standardized_job["ghost_score"] = ghost_score
        standardized_job["is_ghost"] = ghost_score > 0.7
        
        if not standardized_job["is_ghost"]:
            self.active_jobs.append(standardized_job)
        
        return standardized_job
    
    def _detect_ghost_job(self, job: Dict) -> float:
        """ML-based ghost job detection (simplified version)"""
        ghost_signals = 0
        total_signals = 5
        
        # No client name provided
        if job["client"] == "Confidential":
            ghost_signals += 1
        
        # Unusually wide rate range
        if job["rate_range"]["max"] > job["rate_range"]["min"] * 2:
            ghost_signals += 1
        
        # Posted > 45 days ago
        try:
            posted = datetime.fromisoformat(job["posted_date"])
            if (datetime.now() - posted).days > 45:
                ghost_signals += 1
        except:
            pass
        
        # No specific skills listed
        if not job["skills_required"] or len(job["skills_required"]) == 0:
            ghost_signals += 1
        
        # Vague job title
        vague_titles = ["developer", "engineer", "analyst", "consultant"]
        if job["title"].lower() in vague_titles:
            ghost_signals += 1
        
        return ghost_signals / total_signals
    
    def submit_candidate(self, job_id: str, candidate_data: Dict, 
                         vendor_id: str, work_auth_result: Dict) -> Dict:
        """Submit candidate to a job requirement"""
        
        if not work_auth_result.get("can_submit", False):
            return {
                "status": "rejected",
                "reason": "Work authorization check failed",
                "details": work_auth_result
            }
        
        submission = {
            "submission_id": f"SUB-{hash(str(candidate_data))}",
            "job_id": job_id,
            "candidate_id": candidate_data.get("candidate_id"),
            "vendor_id": vendor_id,
            "submitted_at": datetime.now().isoformat(),
            "status": "Submitted",
            "work_auth": work_auth_result,
            "timeline": [
                {"stage": "Submitted", "timestamp": datetime.now().isoformat()}
            ]
        }
        
        self.submission_history.append(submission)
        
        return {
            "status": "success",
            "submission_id": submission["submission_id"],
            "message": "Candidate submitted successfully",
            "next_step": "Awaiting client review (SLA: 48 hours)"
        }
    
    def get_submission_status(self, submission_id: str) -> Dict:
        """Get real-time submission status"""
        for sub in self.submission_history:
            if sub["submission_id"] == submission_id:
                return sub
        return {"status": "error", "message": "Submission not found"}
    
    def check_sla(self, submission_id: str) -> Dict:
        """Check SLA compliance and trigger alerts"""
        status = self.get_submission_status(submission_id)
        
        if status.get("status") == "error":
            return status
        
        submitted_time = datetime.fromisoformat(status["submitted_at"])
        hours_elapsed = (datetime.now() - submitted_time).total_seconds() / 3600
        
        sla_status = {
            "submission_id": submission_id,
            "hours_elapsed": round(hours_elapsed, 1),
            "sla_48hr": hours_elapsed <= 48,
            "action_required": False
        }
        
        # Auto-trigger for SLA breach
        if hours_elapsed > 48 and status["status"] == "Submitted":
            sla_status["action_required"] = True
            sla_status["recommended_action"] = "Escalate to client or release candidate for other matches"
        
        return sla_status
    
    def get_active_jobs(self, filters: Dict = None) -> List[Dict]:
        """Get filtered active jobs"""
        jobs = [j for j in self.active_jobs if not j.get("is_ghost", False)]
        
        if filters:
            if filters.get("visa_type"):
                jobs = [j for j in jobs if not j.get("visa_restrictions") or 
                       filters["visa_type"] not in j["visa_restrictions"]]
            if filters.get("skill"):
                skill_lower = filters["skill"].lower()
                jobs = [j for j in jobs if any(skill_lower in s.lower() for s in j.get("skills_required", []))]
            if filters.get("location"):
                loc_lower = filters["location"].lower()
                jobs = [j for j in jobs if loc_lower in j["location"].lower()]
        
        return jobs

# Initialize VMS connector
vms_connector = VMSConnector()

# Seed some sample jobs
sample_jobs = [
    {
        "title": "Senior Java Backend Developer",
        "client": "Fortune 500 Bank",
        "vms_provider": "SAP Fieldglass",
        "location": "New York, NY (Hybrid)",
        "rate_min": 65, "rate_max": 75, "rate_type": "C2C",
        "skills": ["Java", "Spring Boot", "Kafka", "Microservices", "AWS"],
        "visa_restrictions": [],
        "duration": "12 months",
        "submission_limit": 2
    },
    {
        "title": "Full Stack React Developer",
        "client": "Healthcare Tech Company",
        "vms_provider": "Beeline",
        "location": "Remote (US)",
        "rate_min": 55, "rate_max": 70, "rate_type": "C2C",
        "skills": ["React", "TypeScript", "Node.js", "GraphQL"],
        "visa_restrictions": ["CPT"],
        "duration": "6 months",
        "submission_limit": 3
    },
    {
        "title": "DevOps Engineer",
        "client": "Confidential",
        "vms_provider": "Direct Client",
        "location": "Austin, TX",
        "rate_min": 60, "rate_max": 80, "rate_type": "W2",
        "skills": ["AWS", "Kubernetes", "Terraform", "CI/CD"],
        "visa_restrictions": [],
        "duration": "12 months",
        "submission_limit": 2
    }
]

for job in sample_jobs:
    vms_connector.ingest_job_requirements("direct", job)

print(f"✅ VMS Connector initialized with {len(vms_connector.active_jobs)} active jobs")