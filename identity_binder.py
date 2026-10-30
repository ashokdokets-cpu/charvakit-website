# identity_binder.py
# Bind candidate identity to certificates so they can't be transferred,
# screenshotted, or used by someone else.

import hashlib
import hmac
import os
from typing import Dict


def _get_secret() -> bytes:
    return (
        os.getenv("READINESS_HMAC_KEY")
        or os.getenv("SECRET_KEY")
        or "dev-only-not-secret"
    ).encode()


def mask_email(email: str) -> str:
    """Mask an email for public display: p***a@example.com"""
    if not email or "@" not in email:
        return ""
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def email_fingerprint(email: str) -> str:
    """SHA-256 hash of email (for cross-reference, no plaintext leak)."""
    if not email:
        return ""
    return "sha256:" + hashlib.sha256(email.strip().lower().encode()).hexdigest()[:16]


def build_identity_block(
    candidate_name: str,
    candidate_email: str,
    attempt_num: int,
    attempt_max: int,
) -> Dict:
    """
    Build the identity + attempt metadata that goes into every certificate.

    Returns dict that gets embedded in certificate payload_json and
    displayed on the certificate page.
    """
    name = (candidate_name or "").strip()
    email = (candidate_email or "").strip().lower()

    return {
        "candidate_name": name,
        "candidate_email_masked": mask_email(email),
        "candidate_email_fingerprint": email_fingerprint(email),
        "attempt_number": int(attempt_num),
        "attempt_max": int(attempt_max),
        "first_attempt": int(attempt_num) == 1,
    }


def sign_identity_block(identity: Dict) -> str:
    """
    HMAC-sign the identity block so it can't be tampered with after issuance.
    Anyone with the secret can verify.
    """
    if not identity:
        return ""
    # Stable serialization (sorted keys, no whitespace)
    parts = [
        identity.get("candidate_name", ""),
        identity.get("candidate_email_masked", ""),
        identity.get("candidate_email_fingerprint", ""),
        str(identity.get("attempt_number", 0)),
    ]
    payload = "|".join(parts).encode()
    sig = hmac.new(_get_secret(), payload, hashlib.sha256).hexdigest()
    return sig[:16]


def verify_identity_block(identity: Dict, signature: str) -> bool:
    """Verify that the identity block signature matches."""
    expected = sign_identity_block(identity)
    return hmac.compare_digest(expected, signature or "")