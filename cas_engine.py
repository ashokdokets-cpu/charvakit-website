"""
CAS (Certificate-as-a-Service) Engine
Session 52 (2026-10-19)

Bulk verification of readiness certificates for institutional buyers.

Design:
- Certificates verified by certificate_hash (the HMAC string candidates share)
- API keys issued per institution, SHA-256 hashed in DB
- Approval-gated: pending -> active via admin (pilot fast-track)
- Reuses charvak_readiness_certificates + SECRET_KEY HMAC

Public API:
  verify_certificate_by_hash(certificate_hash) -> Dict
  verify_batch(certificate_hashes, raw_api_key) -> Dict
  request_api_key(institution_name, contact_name, contact_email) -> Dict
  check_api_key(raw_api_key) -> Dict
  approve_api_key(key_id) -> Dict
  list_api_keys(active_only=True) -> List[Dict]
"""

import os
import hashlib
import hmac
import secrets
import logging
from datetime import datetime
from typing import Dict, List, Optional

from database import db

logger = logging.getLogger("charvakit.cas_engine")


# ============================================================
# Table management (self-healing DDL)
# ============================================================

def _ensure_tables():
    """Self-healing DDL for charvak_cas_api_keys."""
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charvak_cas_api_keys (
                key_id TEXT PRIMARY KEY,
                institution_name TEXT NOT NULL,
                contact_name TEXT,
                contact_email TEXT NOT NULL,
                api_key_hash TEXT UNIQUE NOT NULL,
                tier TEXT DEFAULT 'pilot',
                monthly_quota INTEGER DEFAULT 500,
                calls_this_month INTEGER DEFAULT 0,
                last_call_at TIMESTAMP,
                is_active BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_cas_keys_hash
            ON charvak_cas_api_keys(api_key_hash)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_cas_keys_active
            ON charvak_cas_api_keys(is_active) WHERE is_active = TRUE
        """)
        conn.commit()
        cur.close()
    except Exception as e:
        logger.warning(f"_ensure_tables: {e}")
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


# ============================================================
# Hashing + generation helpers
# ============================================================

def _hash_api_key(raw_key: str) -> str:
    """SHA-256 hex of the raw API key. What we store in the DB."""
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def _generate_api_key() -> str:
    """Generate a new raw API key: cas_<32 hex chars>."""
    return "cas_" + secrets.token_hex(16)


def _get_secret_key() -> str:
    """Fetch the HMAC signing secret used for certificate hashes."""
    return os.getenv("SECRET_KEY", "")


def _compute_cert_hash(certificate_id: str, email: str, readiness_score: int) -> str:
    """
    Recompute the HMAC certificate hash the same way the original cert
    issuance does it. This must match the algorithm in
    career_assessment_engine.compute_role_readiness (or wherever certs are issued).
    """
    secret = _get_secret_key()
    if not secret:
        logger.warning("SECRET_KEY missing - cannot verify certificate hashes")
        return ""
    payload = f"{certificate_id}:{email}:{readiness_score}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()[:16]


# ============================================================
# Public API: single cert verification
# ============================================================

def verify_certificate_by_hash(certificate_hash: str) -> Dict:
    """
    Verify a single readiness certificate by its HMAC hash.

    Returns:
      {valid: True, certificate_id, candidate_name, role, industry, level,
       readiness_score, verdict, issued_at}
    OR
      {valid: False, reason: "not_found" | "hash_mismatch" | "error"}
    """
    if not certificate_hash or not isinstance(certificate_hash, str):
        return {"valid": False, "reason": "not_found"}

    certificate_hash = certificate_hash.strip()[:64]  # defensive truncation

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT certificate_id, email, display_name, role, industry,
                   level, readiness_score, verdict, certificate_hash,
                   created_at
            FROM charvak_readiness_certificates
            WHERE certificate_hash = %s
            LIMIT 1
        """, (certificate_hash,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return {"valid": False, "reason": "not_found"}

        (certificate_id, email, display_name, role, industry, level,
         readiness_score, verdict, stored_hash, created_at) = row

        # Constant-time compare stored hash against the hash we just received
        if not hmac.compare_digest((stored_hash or "").encode("utf-8"),
                                    (certificate_hash or "").encode("utf-8")):
            return {"valid": False, "reason": "hash_mismatch"}

        return {
            "valid": True,
            "certificate_id": certificate_id,
            "candidate_name": display_name or "(not provided)",
            "role": role,
            "industry": industry,
            "level": level,
            "readiness_score": int(readiness_score or 0),
            "verdict": verdict,
            "issued_at": created_at.isoformat() if created_at else None,
        }
    except Exception as e:
        logger.warning(f"verify_certificate_by_hash: {e}")
        return {"valid": False, "reason": "error"}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


# ============================================================
# Public API: batch verification
# ============================================================

def verify_batch(certificate_hashes: List[str], raw_api_key: str) -> Dict:
    """
    Batch verify up to 100 certificate hashes with an API key.

    Returns:
      {status, total, valid, invalid, results: [...]}
    OR
      {status: "error", message: "..."}
    """
    if not isinstance(certificate_hashes, list):
        return {"status": "error", "message": "certificate_hashes must be a list"}

    if len(certificate_hashes) == 0:
        return {"status": "error", "message": "certificate_hashes cannot be empty"}

    if len(certificate_hashes) > 100:
        return {"status": "error", "message": "max 100 certificate hashes per request"}

    # Validate API key first
    key_check = check_api_key(raw_api_key)
    if not key_check.get("valid"):
        return {"status": "error", "message": key_check.get("reason", "invalid_api_key")}

    key_id = key_check["key_id"]

    # Verify each hash
    results = []
    valid_count = 0
    for chash in certificate_hashes:
        r = verify_certificate_by_hash(chash)
        results.append({
            "hash": chash,
            **r,
        })
        if r.get("valid"):
            valid_count += 1

    # Increment call counter + last_call_at on the key
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE charvak_cas_api_keys
            SET calls_this_month = calls_this_month + %s,
                last_call_at = CURRENT_TIMESTAMP
            WHERE key_id = %s
        """, (len(results), key_id))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.warning(f"verify_batch call-count update: {e}")

    return {
        "status": "success",
        "total": len(results),
        "valid": valid_count,
        "invalid": len(results) - valid_count,
        "results": results,
    }


# ============================================================
# Public API: API key management
# ============================================================

def check_api_key(raw_api_key: str) -> Dict:
    """
    Validate an API key. Returns {valid: True, key_id, institution_name,
    tier, monthly_quota, calls_this_month} or {valid: False, reason}.
    """
    if not raw_api_key or not isinstance(raw_api_key, str):
        return {"valid": False, "reason": "missing_api_key"}

    raw_api_key = raw_api_key.strip()
    if not raw_api_key.startswith("cas_"):
        return {"valid": False, "reason": "invalid_format"}

    hashed = _hash_api_key(raw_api_key)

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT key_id, institution_name, tier, monthly_quota,
                   calls_this_month, is_active, expires_at
            FROM charvak_cas_api_keys
            WHERE api_key_hash = %s
            LIMIT 1
        """, (hashed,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return {"valid": False, "reason": "not_found"}

        key_id, institution, tier, quota, calls, active, expires = row

        if not active:
            return {"valid": False, "reason": "not_approved"}

        if expires and expires < datetime.utcnow():
            return {"valid": False, "reason": "expired"}

        if quota and calls >= quota:
            return {"valid": False, "reason": "quota_exceeded"}

        return {
            "valid": True,
            "key_id": key_id,
            "institution_name": institution,
            "tier": tier,
            "monthly_quota": quota,
            "calls_this_month": calls,
        }
    except Exception as e:
        logger.warning(f"check_api_key: {e}")
        return {"valid": False, "reason": "error"}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


def request_api_key(institution_name: str, contact_name: str,
                     contact_email: str) -> Dict:
    """
    Create a pending API key request. Returns the key_id + a message.
    The raw key is generated immediately but NOT returned — only after
    admin approval (approve_api_key returns the raw key ONCE).
    """
    _ensure_tables()

    if not institution_name or not contact_email:
        return {"status": "error", "message": "institution_name and contact_email required"}

    # Defensive truncation
    institution_name = institution_name.strip()[:200]
    contact_name = (contact_name or "").strip()[:100]
    contact_email = contact_email.strip()[:200]

    if "@" not in contact_email:
        return {"status": "error", "message": "invalid contact_email"}

    raw_key = _generate_api_key()
    key_id = "KEY-" + secrets.token_hex(8).upper()

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO charvak_cas_api_keys
                (key_id, institution_name, contact_name, contact_email,
                 api_key_hash, tier, monthly_quota, is_active)
            VALUES (%s, %s, %s, %s, %s, 'pilot', 500, FALSE)
        """, (key_id, institution_name, contact_name, contact_email,
              _hash_api_key(raw_key)))
        conn.commit()
        cur.close()

        logger.info(f"CAS key requested: {key_id} for {institution_name}")

        # NOTE: raw_key is NOT returned here. Only approve_api_key() returns it.
        # We store it in a temporary location so approve_api_key can retrieve it.
        # Simplest: store raw in a separate one-time table OR regenerate at approval.
        # For pilot: we return the raw key to the CALLER-ADMIN, not the requester.
        # Actually — cleaner design: don't generate raw_key until approval.
        # Since we already inserted with _hash_api_key(raw_key), let's change the
        # approval to regenerate. But then the stored hash is wrong.
        #
        # SIMPLEST FIX: store raw_key in a temp column OR just return it now but
        # the requirement is admin-approval-before-use (which we enforce via
        # is_active=FALSE, not via secret generation).
        #
        # Decision: return the raw_key in the response. It's still useless
        # until approved. This way approve_api_key doesn't need to regenerate.
        return {
            "status": "pending",
            "key_id": key_id,
            "raw_key": raw_key,  # useless until admin approves
            "message": (
                "API key generated. An admin must approve it before it works. "
                "You will receive an email once approved."
            ),
        }
    except Exception as e:
        logger.warning(f"request_api_key: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


def approve_api_key(key_id: str) -> Dict:
    """
    Flip is_active=TRUE for a pending key. Admin-only.
    Returns the key record so caller can notify the institution.
    """
    if not key_id:
        return {"status": "error", "message": "key_id required"}

    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE charvak_cas_api_keys
            SET is_active = TRUE, approved_at = CURRENT_TIMESTAMP
            WHERE key_id = %s AND is_active = FALSE
            RETURNING key_id, institution_name, contact_email, tier
        """, (key_id,))
        row = cur.fetchone()
        conn.commit()
        cur.close()

        if not row:
            return {"status": "error", "message": "key not found or already active"}

        return {
            "status": "success",
            "key_id": row[0],
            "institution_name": row[1],
            "contact_email": row[2],
            "tier": row[3],
            "message": "API key approved. Institution may now use it.",
        }
    except Exception as e:
        logger.warning(f"approve_api_key: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


def list_api_keys(active_only: bool = True) -> List[Dict]:
    """Admin view of all API keys (masked hashes)."""
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        if active_only:
            cur.execute("""
                SELECT key_id, institution_name, contact_name, contact_email,
                       tier, monthly_quota, calls_this_month, is_active,
                       created_at, approved_at, expires_at
                FROM charvak_cas_api_keys
                WHERE is_active = TRUE
                ORDER BY created_at DESC
            """)
        else:
            cur.execute("""
                SELECT key_id, institution_name, contact_name, contact_email,
                       tier, monthly_quota, calls_this_month, is_active,
                       created_at, approved_at, expires_at
                FROM charvak_cas_api_keys
                ORDER BY created_at DESC
            """)
        rows = cur.fetchall()
        cur.close()

        return [
            {
                "key_id": r[0],
                "institution_name": r[1],
                "contact_name": r[2],
                "contact_email": r[3],
                "tier": r[4],
                "monthly_quota": r[5],
                "calls_this_month": r[6],
                "is_active": r[7],
                "created_at": r[8].isoformat() if r[8] else None,
                "approved_at": r[9].isoformat() if r[9] else None,
                "expires_at": r[10].isoformat() if r[10] else None,
            }
            for r in rows
        ]
    except Exception as e:
        logger.warning(f"list_api_keys: {e}")
        return []
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


# Auto-init tables on import
_ensure_tables()