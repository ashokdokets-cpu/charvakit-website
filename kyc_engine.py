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
        self._ensure_tables()
        logger.info(f"KYC Engine ready (DB-backed) | Mode: {KYC_MODE.upper()}")

    def _ensure_tables(self):
        """Idempotent table creation for KYC tables."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_kyc_verifications (
                    verification_id      TEXT PRIMARY KEY,
                    user_name            TEXT,
                    user_email           TEXT NOT NULL,
                    user_phone           TEXT,
                    verification_type    TEXT NOT NULL DEFAULT 'identity',
                    country              TEXT DEFAULT 'India',
                    documents_requested  JSONB DEFAULT '[]'::jsonb,
                    documents_submitted  JSONB DEFAULT '[]'::jsonb,
                    status               TEXT NOT NULL DEFAULT 'pending',
                    price_inr            INTEGER DEFAULT 499,
                    price_usd            INTEGER DEFAULT 6,
                    payment_status       TEXT DEFAULT 'pending',
                    payment_order_id     TEXT,
                    assigned_to          TEXT,
                    results              JSONB DEFAULT '{}'::jsonb,
                    notes                TEXT DEFAULT '',
                    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at         TIMESTAMP,
                    valid_until          TIMESTAMP
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_kyc_partners (
                    partner_id              TEXT PRIMARY KEY,
                    agency_name             TEXT NOT NULL,
                    contact_person          TEXT,
                    email                   TEXT NOT NULL,
                    phone                   TEXT,
                    services                JSONB DEFAULT '[]'::jsonb,
                    coverage                TEXT DEFAULT '',
                    status                  TEXT NOT NULL DEFAULT 'pending_review',
                    verifications_completed INTEGER DEFAULT 0,
                    revenue_earned          NUMERIC(12,2) DEFAULT 0,
                    rating                  NUMERIC(3,1),
                    registered_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approved_at             TIMESTAMP
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_kyc_verified_users (
                    email              TEXT PRIMARY KEY,
                    name               TEXT,
                    verification_id    TEXT,
                    verification_type  TEXT,
                    verified_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    valid_until        TIMESTAMP,
                    badge_id           TEXT UNIQUE
                )
            ''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"kyc tables init failed: {e}")


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
        """Start a new verification request."""
        verification_id = f"VERIFY-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        verification_type = user_data.get("verification_type", VerificationType.IDENTITY)
        country = user_data.get("country", "India")
        docs_required = self._get_required_docs(verification_type, country)
        price_inr = self.PRICING.get(verification_type, {}).get("inr", 499)
        price_usd = self.PRICING.get(verification_type, {}).get("usd", 6)
        valid_until = datetime.now() + timedelta(days=365)
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_kyc_verifications
                    (verification_id, user_name, user_email, user_phone,
                     verification_type, country, documents_requested,
                     documents_submitted, status, price_inr, price_usd,
                     payment_status, results, notes, valid_until)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, '[]'::jsonb,
                        'pending', %s, %s, 'pending', '{}'::jsonb, %s, %s)
            ''', (verification_id, user_data.get("name"), user_data.get("email"),
                  user_data.get("phone"), verification_type, country,
                  json.dumps(docs_required), price_inr, price_usd,
                  user_data.get("notes", ""), valid_until))
            conn.commit()
            cur.close(); conn.close()
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
                "documents_required": docs_required,
                "price_inr": price_inr,
                "valid_until": valid_until.isoformat()
            }
        except Exception as e:
            logger.error(f"initiate_verification failed: {e}")
            return {"status": "error", "message": str(e)}


    def submit_documents(self, verification_id: str, documents: List[Dict]) -> Dict:
        """Submit documents for verification."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_kyc_verifications
                SET documents_submitted = %s::jsonb,
                    status = 'documents_submitted',
                    updated_at = CURRENT_TIMESTAMP
                WHERE verification_id = %s
                RETURNING status
            ''', (json.dumps(documents), verification_id))
            row = cur.fetchone()
            conn.commit()
            cur.close(); conn.close()
            if not row:
                return {"status": "error", "message": "Verification ID not found"}
            logger.info(f"Documents submitted for {verification_id}: {len(documents)} files")
            return {
                "status": "success",
                "verification_id": verification_id,
                "message": f"{len(documents)} documents submitted successfully",
                "verification_status": row[0],
                "estimated_completion": (datetime.now() + timedelta(hours=48)).isoformat()
            }
        except Exception as e:
            logger.error(f"submit_documents failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_verification_status(self, verification_id: str) -> Dict:
        """Check the status of a verification."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT verification_id, user_name, user_email, user_phone,
                       verification_type, country, documents_requested,
                       documents_submitted, status, price_inr, price_usd,
                       payment_status, payment_order_id, assigned_to, results,
                       notes, created_at, updated_at, completed_at, valid_until
                FROM charvak_kyc_verifications WHERE verification_id = %s
            ''', (verification_id,))
            r = cur.fetchone()
            cur.close(); conn.close()
            if not r:
                return {"status": "error", "message": "Verification ID not found"}
            return {"status": "success", "verification": {
                "verification_id": r[0], "user_name": r[1], "user_email": r[2],
                "user_phone": r[3], "verification_type": r[4], "country": r[5],
                "documents_requested": r[6] if isinstance(r[6], list) else json.loads(r[6] or "[]"),
                "documents_submitted": r[7] if isinstance(r[7], list) else json.loads(r[7] or "[]"),
                "status": r[8], "price_inr": r[9], "price_usd": r[10],
                "payment_status": r[11], "payment_order_id": r[12],
                "assigned_to": r[13],
                "results": r[14] if isinstance(r[14], dict) else (json.loads(r[14]) if r[14] else {}),
                "notes": r[15] or "",
                "created_at": r[16].isoformat() if r[16] else None,
                "updated_at": r[17].isoformat() if r[17] else None,
                "completed_at": r[18].isoformat() if r[18] else None,
                "valid_until": r[19].isoformat() if r[19] else None,
            }}
        except Exception as e:
            logger.error(f"get_verification_status failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_user_verifications(self, email: str) -> Dict:
        """Get all verifications for a user."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT verification_id, user_name, user_email, user_phone,
                       verification_type, country, documents_requested,
                       documents_submitted, status, price_inr, price_usd,
                       payment_status, payment_order_id, assigned_to, results,
                       notes, created_at, updated_at, completed_at, valid_until
                FROM charvak_kyc_verifications
                WHERE user_email = %s
                ORDER BY created_at DESC
            ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
            verifications = []
            has_valid = False
            now = datetime.now()
            for r in rows:
                v = {
                    "verification_id": r[0], "user_name": r[1], "user_email": r[2],
                    "user_phone": r[3], "verification_type": r[4], "country": r[5],
                    "documents_requested": r[6] if isinstance(r[6], list) else json.loads(r[6] or "[]"),
                    "documents_submitted": r[7] if isinstance(r[7], list) else json.loads(r[7] or "[]"),
                    "status": r[8], "price_inr": r[9], "price_usd": r[10],
                    "payment_status": r[11], "payment_order_id": r[12],
                    "assigned_to": r[13],
                    "results": r[14] if isinstance(r[14], dict) else (json.loads(r[14]) if r[14] else {}),
                    "notes": r[15] or "",
                    "created_at": r[16].isoformat() if r[16] else None,
                    "updated_at": r[17].isoformat() if r[17] else None,
                    "completed_at": r[18].isoformat() if r[18] else None,
                    "valid_until": r[19].isoformat() if r[19] else None,
                }
                verifications.append(v)
                if v["status"] == "verified" and r[19] and r[19] > now:
                    has_valid = True
            return {
                "status": "success",
                "verifications": verifications,
                "count": len(verifications),
                "has_valid_verification": has_valid,
            }
        except Exception as e:
            logger.error(f"get_user_verifications failed: {e}")
            return {"status": "error", "message": str(e), "verifications": [], "count": 0}


    def review_verification(self, verification_id: str, result: Dict) -> Dict:
        """Admin/Partner reviews a verification."""
        new_status_val = result.get("status", "rejected")
        findings = result.get("findings", {})
        checked_by = result.get("checked_by")
        notes = result.get("notes", "")
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            if new_status_val == "verified":
                cur.execute('''
                    UPDATE charvak_kyc_verifications
                    SET status = 'verified',
                        results = %s::jsonb,
                        assigned_to = %s,
                        notes = COALESCE(NULLIF(%s, ''), notes),
                        updated_at = CURRENT_TIMESTAMP,
                        completed_at = CURRENT_TIMESTAMP,
                        valid_until = %s
                    WHERE verification_id = %s
                    RETURNING user_name, user_email, verification_type
                ''', (json.dumps(findings), checked_by, notes,
                      datetime.now() + timedelta(days=365), verification_id))
            else:
                cur.execute('''
                    UPDATE charvak_kyc_verifications
                    SET status = %s,
                        results = %s::jsonb,
                        assigned_to = %s,
                        notes = COALESCE(NULLIF(%s, ''), notes),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE verification_id = %s
                    RETURNING user_name, user_email, verification_type
                ''', (new_status_val, json.dumps(findings), checked_by,
                      notes, verification_id))
            row = cur.fetchone()
            if not row:
                conn.rollback()
                cur.close(); conn.close()
                return {"status": "error", "message": "Verification ID not found"}
            # If verified, add to verified_users (upsert)
            if new_status_val == "verified":
                user_name, user_email, vtype = row
                badge_id = f"BADGE-{secrets.token_hex(4).upper()}"
                cur.execute('''
                    INSERT INTO charvak_kyc_verified_users
                        (email, name, verification_id, verification_type, valid_until, badge_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (email) DO UPDATE
                        SET name = EXCLUDED.name,
                            verification_id = EXCLUDED.verification_id,
                            verification_type = EXCLUDED.verification_type,
                            verified_at = CURRENT_TIMESTAMP,
                            valid_until = EXCLUDED.valid_until,
                            badge_id = EXCLUDED.badge_id
                ''', (user_email, user_name, verification_id, vtype,
                      datetime.now() + timedelta(days=365), badge_id))
            conn.commit()
            cur.close(); conn.close()
            if new_status_val == "verified":
                logger.info(f"Verification approved: {verification_id}")
            else:
                logger.info(f"Verification rejected: {verification_id}")
            return {
                "status": "success",
                "verification_id": verification_id,
                "result": new_status_val,
                "message": f"Verification {new_status_val}",
            }
        except Exception as e:
            logger.error(f"review_verification failed: {e}")
            return {"status": "error", "message": str(e)}


    # ============================================================
    # VERIFIED USER MANAGEMENT
    # ============================================================
    
    def _add_verified_user(self, verification: Dict):
        """Add user to verified users (upsert)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            badge_id = f"BADGE-{secrets.token_hex(4).upper()}"
            cur.execute('''
                INSERT INTO charvak_kyc_verified_users
                    (email, name, verification_id, verification_type, valid_until, badge_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE
                    SET name = EXCLUDED.name,
                        verification_id = EXCLUDED.verification_id,
                        verification_type = EXCLUDED.verification_type,
                        verified_at = CURRENT_TIMESTAMP,
                        valid_until = EXCLUDED.valid_until,
                        badge_id = EXCLUDED.badge_id
            ''', (verification["user_email"], verification["user_name"],
                  verification["verification_id"], verification["verification_type"],
                  verification["valid_until"], badge_id))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"_add_verified_user failed: {e}")


    def is_user_verified(self, email: str) -> Dict:
        """Check if a user is verified."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT email, name, verification_id, verification_type,
                       verified_at, valid_until, badge_id
                FROM charvak_kyc_verified_users
                WHERE email = %s AND valid_until > CURRENT_TIMESTAMP
            ''', (email,))
            r = cur.fetchone()
            cur.close(); conn.close()
            if not r:
                return {"status": "success", "verified": False}
            return {"status": "success", "verified": True, "badge": {
                "email": r[0], "name": r[1], "verification_id": r[2],
                "verification_type": r[3],
                "verified_at": r[4].isoformat() if r[4] else None,
                "valid_until": r[5].isoformat() if r[5] else None,
                "badge_id": r[6],
            }}
        except Exception as e:
            logger.error(f"is_user_verified failed: {e}")
            return {"status": "error", "message": str(e), "verified": False}


    def get_verified_badge(self, email: str) -> Dict:
        """Get verified badge details."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT email, name, verification_id, verification_type,
                       verified_at, valid_until, badge_id
                FROM charvak_kyc_verified_users WHERE email = %s
            ''', (email,))
            r = cur.fetchone()
            cur.close(); conn.close()
            if not r:
                return {"status": "error", "message": "No verified badge found"}
            badge = {
                "email": r[0], "name": r[1], "verification_id": r[2],
                "verification_type": r[3],
                "verified_at": r[4].isoformat() if r[4] else None,
                "valid_until": r[5].isoformat() if r[5] else None,
                "badge_id": r[6],
                "share_url": f"https://charvakit.com/badge?ref={r[6]}",
                "linkedin_share": f"https://www.linkedin.com/profile/add?certId={r[6]}",
            }
            return {"status": "success", "badge": badge}
        except Exception as e:
            logger.error(f"get_verified_badge failed: {e}")
            return {"status": "error", "message": str(e)}


    # ============================================================
    # PARTNER MANAGEMENT
    # ============================================================
    
    def register_partner(self, partner_data: Dict) -> Dict:
        """Register a verification partner."""
        partner_id = f"PARTNER-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_kyc_partners
                    (partner_id, agency_name, contact_person, email, phone,
                     services, coverage, status)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, 'pending_review')
            ''', (partner_id, partner_data.get("agency_name"),
                  partner_data.get("contact_person"), partner_data.get("email"),
                  partner_data.get("phone"),
                  json.dumps(partner_data.get("services", [])),
                  partner_data.get("coverage", "")))
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"New partner registered: {partner_id} - {partner_data.get('agency_name')}")
            return {
                "status": "success",
                "partner_id": partner_id,
                "message": "Partner application submitted! We will review and contact you within 48 hours.",
                "next_steps": [
                    "Our team will review your application",
                    "You'll receive an onboarding email with API access",
                    "Start receiving verification requests from our career pipeline",
                ],
            }
        except Exception as e:
            logger.error(f"register_partner failed: {e}")
            return {"status": "error", "message": str(e)}


    def approve_partner(self, partner_id: str) -> Dict:
        """Admin approves a partner."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_kyc_partners
                SET status = 'approved', approved_at = CURRENT_TIMESTAMP
                WHERE partner_id = %s
                RETURNING agency_name
            ''', (partner_id,))
            row = cur.fetchone()
            conn.commit()
            cur.close(); conn.close()
            if not row:
                return {"status": "error", "message": "Partner not found"}
            return {
                "status": "success",
                "partner_id": partner_id,
                "agency_name": row[0],
                "message": f"Partner {row[0]} approved",
            }
        except Exception as e:
            logger.error(f"approve_partner failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_partners(self, status: str = None) -> Dict:
        """Get verification partners, optionally filtered by status."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            if status:
                cur.execute('''
                    SELECT partner_id, agency_name, contact_person, email, phone,
                           services, coverage, status, verifications_completed,
                           revenue_earned, rating, registered_at, approved_at
                    FROM charvak_kyc_partners WHERE status = %s
                    ORDER BY registered_at DESC
                ''', (status,))
            else:
                cur.execute('''
                    SELECT partner_id, agency_name, contact_person, email, phone,
                           services, coverage, status, verifications_completed,
                           revenue_earned, rating, registered_at, approved_at
                    FROM charvak_kyc_partners
                    ORDER BY registered_at DESC
                ''')
            rows = cur.fetchall()
            cur.close(); conn.close()
            partners = []
            for r in rows:
                partners.append({
                    "partner_id": r[0], "agency_name": r[1],
                    "contact_person": r[2], "email": r[3], "phone": r[4],
                    "services": r[5] if isinstance(r[5], list) else json.loads(r[5] or "[]"),
                    "coverage": r[6] or "",
                    "status": r[7], "verifications_completed": r[8] or 0,
                    "revenue_earned": float(r[9] or 0),
                    "rating": float(r[10]) if r[10] else None,
                    "registered_at": r[11].isoformat() if r[11] else None,
                    "approved_at": r[12].isoformat() if r[12] else None,
                })
            return {"status": "success", "partners": partners, "count": len(partners)}
        except Exception as e:
            logger.error(f"get_partners failed: {e}")
            return {"status": "error", "message": str(e), "partners": [], "count": 0}


    def assign_verification_to_partner(self, verification_id: str, partner_id: str) -> Dict:
        """Assign a verification to a partner for processing."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            # Verify partner exists and is approved
            cur.execute('''
                SELECT agency_name FROM charvak_kyc_partners
                WHERE partner_id = %s AND status = 'approved'
            ''', (partner_id,))
            partner_row = cur.fetchone()
            if not partner_row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Partner not found or not approved"}
            # Assign verification
            cur.execute('''
                UPDATE charvak_kyc_verifications
                SET assigned_to = %s,
                    status = 'in_progress',
                    updated_at = CURRENT_TIMESTAMP
                WHERE verification_id = %s
                RETURNING verification_id
            ''', (partner_id, verification_id))
            v_row = cur.fetchone()
            if not v_row:
                conn.rollback()
                cur.close(); conn.close()
                return {"status": "error", "message": "Verification ID not found"}
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"Verification {verification_id} assigned to {partner_id}")
            return {
                "status": "success",
                "verification_id": verification_id,
                "partner_id": partner_id,
                "partner_name": partner_row[0],
                "message": f"Verification assigned to {partner_row[0]}",
            }
        except Exception as e:
            logger.error(f"assign_verification_to_partner failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_stats(self) -> Dict:
        """Get KYC system statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM charvak_kyc_verifications")
            total = cur.fetchone()[0] or 0
            cur.execute('''
                SELECT COUNT(*) FROM charvak_kyc_verifications
                WHERE status IN ('pending','in_progress','documents_requested','documents_submitted','under_review')
            ''')
            pending = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_kyc_verifications WHERE status = 'verified'")
            verified = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_kyc_verifications WHERE status = 'rejected'")
            rejected = cur.fetchone()[0] or 0
            cur.execute('''
                SELECT COALESCE(SUM(price_inr), 0) FROM charvak_kyc_verifications
                WHERE payment_status = 'completed'
            ''')
            total_revenue = int(cur.fetchone()[0] or 0)
            cur.execute("SELECT COUNT(*) FROM charvak_kyc_partners WHERE status = 'approved'")
            active_partners = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_kyc_verified_users WHERE valid_until > CURRENT_TIMESTAMP")
            active_verified_users = cur.fetchone()[0] or 0
            cur.close(); conn.close()
            return {
                "status": "success",
                "stats": {
                    "total_verifications": total,
                    "pending": pending,
                    "verified": verified,
                    "rejected": rejected,
                    "total_revenue_inr": total_revenue,
                    "active_partners": active_partners,
                    "active_verified_users": active_verified_users,
                },
            }
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": str(e)}


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
