"""
Charvak North America - VMS Connector
Integrates with Fieldglass, Beeline, and Tier-1 Vendor Systems
(DB-backed - Session G/2)
"""
import os
import json
import logging
import secrets
import httpx
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger("charvakit.na.vms_connector")


class VMSProvider(Enum):
    FIELDGLASS = "SAP Fieldglass"
    BEELINE = "Beeline"
    WAND = "WAND VMS"
    VNDLY = "Workday VNDLY"
    COUPA = "Coupa Contingent Workforce"
    PRO_UNLIMITED = "PRO Unlimited"
    CUSTOM = "Custom VMS"


class JobStatus(Enum):
    ACTIVE = "Active - Accepting Submissions"
    ON_HOLD = "On Hold"
    OFFERS_MADE = "Offers in Progress"
    FILLED = "Position Filled"
    CANCELLED = "Cancelled"
    EXPIRED = "Expired"


class VMSConnector:
    """Core VMS integration engine (DB-backed)"""

    VMS_CONFIGS = {
        VMSProvider.FIELDGLASS: {
            "base_url": "https://api.fieldglass.com/v1",
            "auth_type": "oauth2",
            "rate_limit": "1000/hour",
        },
        VMSProvider.BEELINE: {
            "base_url": "https://api.beeline.com/v2",
            "auth_type": "api_key",
            "rate_limit": "500/hour",
        },
        VMSProvider.CUSTOM: {
            "base_url": os.getenv("CUSTOM_VMS_URL", ""),
            "auth_type": "custom",
            "rate_limit": "unlimited",
        },
    }

    def __init__(self):
        self._ensure_tables()
        logger.info("VMS Connector ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_na_vms_jobs (
                    job_id               TEXT PRIMARY KEY,
                    source               TEXT,
                    title                TEXT,
                    client               TEXT,
                    vms_provider         TEXT,
                    location             TEXT,
                    rate_range           JSONB DEFAULT '{}'::jsonb,
                    skills_required      JSONB DEFAULT '[]'::jsonb,
                    visa_restrictions    JSONB DEFAULT '[]'::jsonb,
                    duration             TEXT,
                    status               TEXT DEFAULT 'Active - Accepting Submissions',
                    posted_date          TEXT,
                    submission_deadline  TEXT,
                    submission_limit     INTEGER DEFAULT 3,
                    interview_process    TEXT,
                    compliance_notes     TEXT,
                    ghost_score          NUMERIC(3,2) DEFAULT 0,
                    is_ghost             BOOLEAN DEFAULT FALSE,
                    ingested_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_vms_jobs_status ON charvak_na_vms_jobs(status)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_vms_jobs_ghost  ON charvak_na_vms_jobs(is_ghost)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_vms_jobs_source ON charvak_na_vms_jobs(source)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_na_vms_submissions (
                    submission_id  TEXT PRIMARY KEY,
                    job_id         TEXT NOT NULL,
                    candidate_id   TEXT,
                    vendor_id      TEXT,
                    status         TEXT DEFAULT 'Submitted',
                    work_auth      JSONB DEFAULT '{}'::jsonb,
                    timeline       JSONB DEFAULT '[]'::jsonb,
                    submitted_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_vms_subs_job       ON charvak_na_vms_submissions(job_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_vms_subs_candidate ON charvak_na_vms_submissions(candidate_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_vms_subs_status    ON charvak_na_vms_submissions(status)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"vms_connector tables init failed: {e}")

    # ============================================================
    # INGESTION
    # ============================================================

    def ingest_job_requirements(self, source: str, raw_data: Dict) -> Dict:
        """Ingest and standardize job requirements from any source"""
        job_id = f"NA-JOB-{secrets.token_hex(4).upper()}"

        standardized_job = {
            "job_id": job_id,
            "source": source,
            "title": raw_data.get("title", "Unknown Role"),
            "client": raw_data.get("client", "Confidential"),
            "vms_provider": raw_data.get("vms_provider", "Direct"),
            "location": raw_data.get("location", "Remote"),
            "rate_range": {
                "min": raw_data.get("rate_min", 0),
                "max": raw_data.get("rate_max", 0),
                "type": raw_data.get("rate_type", "C2C"),
            },
            "skills_required": raw_data.get("skills", []),
            "visa_restrictions": raw_data.get("visa_restrictions", []),
            "duration": raw_data.get("duration", "6 months"),
            "status": JobStatus.ACTIVE.value,
            "posted_date": raw_data.get("posted_date", datetime.now().isoformat()),
            "submission_deadline": raw_data.get("deadline", "ASAP"),
            "submission_limit": raw_data.get("submission_limit", 3),
            "interview_process": raw_data.get("interview_process", "Client Review -> Technical -> Offer"),
            "compliance_notes": raw_data.get("compliance_notes", ""),
        }

        ghost_score = self._detect_ghost_job(standardized_job)
        standardized_job["ghost_score"] = ghost_score
        standardized_job["is_ghost"] = ghost_score > 0.7

        if not standardized_job["is_ghost"]:
            try:
                from database import db
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute('''
                    INSERT INTO charvak_na_vms_jobs (
                        job_id, source, title, client, vms_provider, location,
                        rate_range, skills_required, visa_restrictions, duration,
                        status, posted_date, submission_deadline, submission_limit,
                        interview_process, compliance_notes, ghost_score, is_ghost
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb,
                              %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    standardized_job["job_id"],
                    standardized_job["source"],
                    standardized_job["title"],
                    standardized_job["client"],
                    standardized_job["vms_provider"],
                    standardized_job["location"],
                    json.dumps(standardized_job["rate_range"]),
                    json.dumps(standardized_job["skills_required"]),
                    json.dumps(standardized_job["visa_restrictions"]),
                    standardized_job["duration"],
                    standardized_job["status"],
                    standardized_job["posted_date"],
                    standardized_job["submission_deadline"],
                    standardized_job["submission_limit"],
                    standardized_job["interview_process"],
                    standardized_job["compliance_notes"],
                    standardized_job["ghost_score"],
                    standardized_job["is_ghost"],
                ))
                conn.commit()
                cur.close(); conn.close()
            except Exception as e:
                logger.error(f"ingest_job_requirements write failed: {e}")

        return standardized_job

    def _detect_ghost_job(self, job: Dict) -> float:
        """ML-based ghost job detection (simplified version)"""
        ghost_signals = 0
        total_signals = 5

        if job["client"] == "Confidential":
            ghost_signals += 1
        if job["rate_range"]["max"] > job["rate_range"]["min"] * 2:
            ghost_signals += 1
        try:
            posted = datetime.fromisoformat(job["posted_date"])
            if (datetime.now() - posted).days > 45:
                ghost_signals += 1
        except Exception:
            pass
        if not job["skills_required"] or len(job["skills_required"]) == 0:
            ghost_signals += 1
        vague_titles = ["developer", "engineer", "analyst", "consultant"]
        if job["title"].lower() in vague_titles:
            ghost_signals += 1

        return ghost_signals / total_signals

    # ============================================================
    # SUBMISSIONS
    # ============================================================

    def submit_candidate(self, job_id: str, candidate_data: Dict,
                         vendor_id: str, work_auth_result: Dict) -> Dict:
        """Submit candidate to a job requirement"""
        if not work_auth_result.get("can_submit", False):
            return {
                "status": "rejected",
                "reason": "Work authorization check failed",
                "details": work_auth_result,
            }

        submission_id = f"SUB-{secrets.token_hex(4).upper()}"
        submitted_at = datetime.now().isoformat()
        timeline = [{"stage": "Submitted", "timestamp": submitted_at}]

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_na_vms_submissions (
                    submission_id, job_id, candidate_id, vendor_id, status,
                    work_auth, timeline
                ) VALUES (%s, %s, %s, %s, 'Submitted', %s::jsonb, %s::jsonb)
            ''', (
                submission_id,
                job_id,
                candidate_data.get("candidate_id"),
                vendor_id,
                json.dumps(work_auth_result),
                json.dumps(timeline),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"submit_candidate failed: {e}")
            return {"status": "error", "message": "Could not submit candidate"}

        return {
            "status": "success",
            "submission_id": submission_id,
            "message": "Candidate submitted successfully",
            "next_step": "Awaiting client review (SLA: 48 hours)",
        }

    def get_submission_status(self, submission_id: str) -> Dict:
        """Get real-time submission status"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT submission_id, job_id, candidate_id, vendor_id, submitted_at,
                       status, work_auth, timeline
                FROM charvak_na_vms_submissions WHERE submission_id = %s
            ''', (submission_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_submission_status failed: {e}")
            return {"status": "error", "message": "Submission not found"}

        if not row:
            return {"status": "error", "message": "Submission not found"}

        return {
            "submission_id": row[0],
            "job_id": row[1],
            "candidate_id": row[2],
            "vendor_id": row[3],
            "submitted_at": row[4].isoformat() if hasattr(row[4], "isoformat") else str(row[4]),
            "status": row[5],
            "work_auth": row[6] if isinstance(row[6], dict) else (json.loads(row[6]) if row[6] else {}),
            "timeline": row[7] if isinstance(row[7], list) else (json.loads(row[7]) if row[7] else []),
        }

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
            "action_required": False,
        }

        if hours_elapsed > 48 and status["status"] == "Submitted":
            sla_status["action_required"] = True
            sla_status["recommended_action"] = "Escalate to client or release candidate for other matches"

        return sla_status

    # ============================================================
    # QUERIES
    # ============================================================

    def get_active_jobs(self, filters: Dict = None) -> List[Dict]:
        """Get filtered active jobs"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT job_id, source, title, client, vms_provider, location,
                       rate_range, skills_required, visa_restrictions, duration,
                       status, posted_date, submission_deadline, submission_limit,
                       interview_process, compliance_notes, ghost_score, is_ghost
                FROM charvak_na_vms_jobs
                WHERE is_ghost = FALSE
                ORDER BY ingested_at DESC
            ''')
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_active_jobs failed: {e}")
            return []

        jobs = []
        for r in rows:
            jobs.append({
                "job_id": r[0],
                "source": r[1],
                "title": r[2],
                "client": r[3],
                "vms_provider": r[4],
                "location": r[5] or "",
                "rate_range": r[6] if isinstance(r[6], dict) else (json.loads(r[6]) if r[6] else {}),
                "skills_required": r[7] if isinstance(r[7], list) else (json.loads(r[7]) if r[7] else []),
                "visa_restrictions": r[8] if isinstance(r[8], list) else (json.loads(r[8]) if r[8] else []),
                "duration": r[9],
                "status": r[10],
                "posted_date": r[11],
                "submission_deadline": r[12],
                "submission_limit": r[13],
                "interview_process": r[14],
                "compliance_notes": r[15] or "",
                "ghost_score": float(r[16]) if r[16] is not None else 0,
                "is_ghost": bool(r[17]),
            })

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

# ============================================================
# DEMO DATA - loaded only when CHARVAK_LOAD_DEMO_JOBS=1
# ============================================================
if os.getenv("CHARVAK_LOAD_DEMO_JOBS", "0") == "1":
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
            "submission_limit": 2,
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
            "submission_limit": 3,
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
            "submission_limit": 2,
        },
    ]
    for job in sample_jobs:
        vms_connector.ingest_job_requirements("direct", job)
    logger.info("VMS Connector: loaded %d demo jobs (CHARVAK_LOAD_DEMO_JOBS=1)", len(sample_jobs))