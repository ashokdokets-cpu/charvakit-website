"""
Charvak North America - Resume Processing Engine
Bulk resume ingestion, PII redaction, and compliance checking
(DB-backed - Session G/4)
"""
import json
import hashlib
import logging
import re
import secrets
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger("charvakit.na.resume")


class PIIRedactor:
    """Automated PII redaction for candidate protection (log DB-backed)"""

    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "address": r'\b\d{1,5}\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Court|Ct)\b',
    }

    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_na_redaction_log (
                    log_id           TEXT PRIMARY KEY,
                    candidate_id     TEXT,
                    redactions       JSONB DEFAULT '{}'::jsonb,
                    original_length  INTEGER DEFAULT 0,
                    redacted_length  INTEGER DEFAULT 0,
                    redacted_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_redact_candidate ON charvak_na_redaction_log(candidate_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_redact_time      ON charvak_na_redaction_log(redacted_at)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"pii_redactor tables init failed: {e}")

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

        log_entry = {
            "candidate_id": candidate_id,
            "timestamp": datetime.now().isoformat(),
            "redactions": redactions,
            "original_length": len(text),
            "redacted_length": len(redacted),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            log_id = f"REDACT-{secrets.token_hex(4).upper()}"
            cur.execute('''
                INSERT INTO charvak_na_redaction_log
                    (log_id, candidate_id, redactions, original_length, redacted_length)
                VALUES (%s, %s, %s::jsonb, %s, %s)
            ''', (log_id, candidate_id, json.dumps(redactions),
                  log_entry["original_length"], log_entry["redacted_length"]))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"redact_text write failed: {e}")

        return redacted, log_entry

    def generate_blind_profile(self, candidate_data: Dict) -> Dict:
        """Generate a dual-blind candidate profile"""
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
        parts = location.split(",")
        if len(parts) >= 2:
            return f"{parts[0].strip()}, {parts[1].strip()}"
        return location


class ComplianceChecker:
    """North American compliance verification (reports DB-backed)"""

    EEOC_REQUIREMENTS = [
        "No discriminatory language in job description",
        "Equal opportunity employer statement included",
        "Reasonable accommodation notice present",
        "No age-restrictive terms (unless BFOQ)",
        "Gender-neutral language verified",
    ]

    NYC_LAW_144_REQUIREMENTS = [
        "Bias audit completed within last 12 months",
        "Bias audit summary publicly available",
        "Candidates notified of AI tool usage",
        "Alternative selection process available upon request",
        "Data retention policy documented",
        "Audit results published on company website",
    ]

    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_na_compliance_reports (
                    report_id              TEXT PRIMARY KEY,
                    report_type            TEXT NOT NULL,
                    job_id                 TEXT,
                    candidate_id           TEXT,
                    eeoc_compliant         BOOLEAN,
                    nyc_law_144_applicable BOOLEAN,
                    issues                 JSONB DEFAULT '[]'::jsonb,
                    warnings               JSONB DEFAULT '[]'::jsonb,
                    restrictions           JSONB DEFAULT '[]'::jsonb,
                    checked_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_comp_type      ON charvak_na_compliance_reports(report_type)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_comp_job       ON charvak_na_compliance_reports(job_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_comp_candidate ON charvak_na_compliance_reports(candidate_id)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"compliance_checker tables init failed: {e}")

    def check_job_compliance(self, job_data: Dict) -> Dict:
        """Check job posting for EEOC compliance"""
        issues = []
        warnings = []

        description = job_data.get("description", "")

        age_restrictive = ["young", "fresh", "recent grad", "digital native", "max 5 years", "under 30"]
        for term in age_restrictive:
            if term in description.lower():
                issues.append(f"Age-restrictive term found: '{term}'")

        gender_biased = ["rockstar", "ninja", "guru", "aggressive", "dominant", "competitive"]
        for term in gender_biased:
            if term in description.lower():
                warnings.append(f"Potentially gender-biased term: '{term}'")

        job_location = job_data.get("location", "")
        is_nyc = any(city in job_location.upper() for city in ["NY", "NEW YORK", "NYC"])

        result = {
            "job_id": job_data.get("job_id", "Unknown"),
            "eeoc_compliant": len(issues) == 0,
            "nyc_law_144_applicable": is_nyc,
            "issues": issues,
            "warnings": warnings,
            "checked_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            report_id = f"COMP-{secrets.token_hex(4).upper()}"
            cur.execute('''
                INSERT INTO charvak_na_compliance_reports
                    (report_id, report_type, job_id, eeoc_compliant, nyc_law_144_applicable,
                     issues, warnings)
                VALUES (%s, 'job', %s, %s, %s, %s::jsonb, %s::jsonb)
            ''', (report_id, result["job_id"], result["eeoc_compliant"],
                  result["nyc_law_144_applicable"], json.dumps(issues), json.dumps(warnings)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"check_job_compliance write failed: {e}")

        return result

    def check_candidate_compliance(self, candidate_data: Dict) -> Dict:
        """Verify candidate submission meets compliance requirements"""
        work_auth = candidate_data.get("work_auth", {})
        visa_type = work_auth.get("visa_type", "Unknown")

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

        result = {
            "candidate_id": candidate_data.get("candidate_id", "Unknown"),
            "compliant": len(restrictions) == 0,
            "restrictions": restrictions,
            "checked_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            report_id = f"COMP-{secrets.token_hex(4).upper()}"
            cur.execute('''
                INSERT INTO charvak_na_compliance_reports
                    (report_id, report_type, candidate_id, restrictions)
                VALUES (%s, 'candidate', %s, %s::jsonb)
            ''', (report_id, result["candidate_id"], json.dumps(restrictions)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"check_candidate_compliance write failed: {e}")

        return result


class SubVendorManager:
    """Sub-vendor management and tracking (DB-backed)"""

    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_na_sub_vendors (
                    vendor_id              TEXT PRIMARY KEY,
                    name                   TEXT,
                    tier                   TEXT DEFAULT 'Tier-2',
                    email                  TEXT,
                    specialization         JSONB DEFAULT '[]'::jsonb,
                    active_candidates      INTEGER DEFAULT 0,
                    successful_placements  INTEGER DEFAULT 0,
                    status                 TEXT DEFAULT 'active',
                    registered_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_vendors_email  ON charvak_na_sub_vendors(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_vendors_status ON charvak_na_sub_vendors(status)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_na_sub_vendor_submissions (
                    submission_key  TEXT PRIMARY KEY,
                    vendor_id       TEXT NOT NULL,
                    candidate_id    TEXT,
                    job_id          TEXT,
                    status          TEXT DEFAULT 'submitted',
                    submitted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_vendor_subs_vendor    ON charvak_na_sub_vendor_submissions(vendor_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_vendor_subs_candidate ON charvak_na_sub_vendor_submissions(candidate_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_vendor_subs_status    ON charvak_na_sub_vendor_submissions(status)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"sub_vendor_manager tables init failed: {e}")

    def register_vendor(self, vendor_data: Dict) -> Dict:
        """Register a new sub-vendor"""
        vendor_id = f"VEN-{secrets.token_hex(4).upper()}"
        vendor = {
            "vendor_id": vendor_id,
            "name": vendor_data.get("name", "Unknown"),
            "tier": vendor_data.get("tier", "Tier-2"),
            "email": vendor_data.get("email"),
            "specialization": vendor_data.get("specialization", []),
            "active_candidates": 0,
            "successful_placements": 0,
            "registered_date": datetime.now().isoformat(),
            "status": "active",
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_na_sub_vendors
                    (vendor_id, name, tier, email, specialization,
                     active_candidates, successful_placements, status)
                VALUES (%s, %s, %s, %s, %s::jsonb, 0, 0, 'active')
            ''', (vendor_id, vendor["name"], vendor["tier"], vendor["email"],
                  json.dumps(vendor["specialization"])))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"register_vendor failed: {e}")

        return vendor

    def track_submission(self, vendor_id: str, candidate_id: str, job_id: str) -> Dict:
        """Track a vendor's candidate submission"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT 1 FROM charvak_na_sub_vendors WHERE vendor_id = %s', (vendor_id,))
            if cur.fetchone() is None:
                cur.close(); conn.close()
                return {"error": "Vendor not registered"}

            submission_key = f"{vendor_id}-{candidate_id}-{job_id}"
            submitted_at = datetime.now().isoformat()

            cur.execute('''
                INSERT INTO charvak_na_sub_vendor_submissions
                    (submission_key, vendor_id, candidate_id, job_id, status)
                VALUES (%s, %s, %s, %s, 'submitted')
                ON CONFLICT (submission_key) DO NOTHING
                RETURNING submission_key
            ''', (submission_key, vendor_id, candidate_id, job_id))
            inserted_row = cur.fetchone()
            is_new_submission = inserted_row is not None

            # K/5 fix: only bump counter on genuinely new submissions
            if is_new_submission:
                cur.execute('''
                    UPDATE charvak_na_sub_vendors
                    SET active_candidates = active_candidates + 1
                    WHERE vendor_id = %s
                ''', (vendor_id,))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"track_submission failed: {e}")
            return {"error": "Could not track submission"}

        return {
            "vendor_id": vendor_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "submitted_at": submitted_at,
            "status": "submitted",
        }

    def get_vendor_stats(self, vendor_id: str) -> Dict:
        """Get vendor performance statistics"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('''
                SELECT vendor_id, name, tier, email, specialization,
                       active_candidates, successful_placements, status, registered_date
                FROM charvak_na_sub_vendors WHERE vendor_id = %s
            ''', (vendor_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"error": "Vendor not found"}

            vendor = {
                "vendor_id": row[0],
                "name": row[1],
                "tier": row[2],
                "email": row[3],
                "specialization": row[4] if isinstance(row[4], list) else (json.loads(row[4]) if row[4] else []),
                "active_candidates": row[5],
                "successful_placements": row[6],
                "status": row[7],
                "registered_date": row[8].isoformat() if hasattr(row[8], "isoformat") else str(row[8]),
            }

            cur.execute('SELECT COUNT(*) FROM charvak_na_sub_vendor_submissions WHERE vendor_id = %s', (vendor_id,))
            total_submissions = int(cur.fetchone()[0] or 0)

            cur.execute('''SELECT COUNT(*) FROM charvak_na_sub_vendor_submissions
                           WHERE vendor_id = %s AND status = 'submitted' ''', (vendor_id,))
            active_submissions = int(cur.fetchone()[0] or 0)

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_vendor_stats failed: {e}")
            return {"error": "Could not load vendor stats"}

        return {
            "vendor": vendor,
            "total_submissions": total_submissions,
            "active_submissions": active_submissions,
            "placement_rate": vendor["successful_placements"] / max(total_submissions, 1) * 100,
        }


# Initialize engines
pii_redactor = PIIRedactor()
compliance_checker = ComplianceChecker()
sub_vendor_manager = SubVendorManager()

logger.info("Resume Engine initialized (DB-backed) | %d PII patterns | EEOC + NYC Law 144",
            len(PIIRedactor.PII_PATTERNS))