# multi_account_detector.py
# Session 104a: Detect multi-account abuse via IP + email prefix cross-reference.
#
# Prevents: one user creating 10 accounts, each getting 3 attempts = 30 total.

import hashlib
from typing import Dict


def hash_ip(ip_address: str) -> str:
    """Stable hash of IP (privacy-safe)."""
    if not ip_address:
        return ""
    return hashlib.sha256(ip_address.strip().encode()).hexdigest()[:16]


def email_prefix(email: str) -> str:
    """Extract normalized prefix from email (priya123@x.com -> priya)."""
    if not email or "@" not in email:
        return ""
    local = email.split("@")[0].lower()
    # Strip trailing digits
    stripped = local.rstrip("0123456789")
    return stripped or local


def record_signup(email: str, ip_address: str, user_agent: str = "") -> Dict:
    """
    Record a signup signal for abuse detection.
    Called on user registration (or first assessment start).
    Idempotent: same email+IP is recorded once.
    """
    email = (email or "").strip().lower()
    if not email:
        return {"status": "error", "message": "email required"}

    ip_hash = hash_ip(ip_address)
    prefix = email_prefix(email)

    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()

        # Ensure table exists (self-healing)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charvak_account_signals (
                signal_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                ip_hash TEXT,
                email_prefix TEXT,
                user_agent TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(email, ip_hash)
            )
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_as_ip
            ON charvak_account_signals (ip_hash)
            WHERE ip_hash IS NOT NULL
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_as_prefix
            ON charvak_account_signals (email_prefix)
            WHERE email_prefix IS NOT NULL
        """)

        signal_id = "SIG-" + hashlib.sha256((email + "|" + ip_hash).encode()).hexdigest()[:12].upper()

        cur.execute("""
            INSERT INTO charvak_account_signals
                (signal_id, email, ip_hash, email_prefix, user_agent)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email, ip_hash) DO NOTHING
        """, (signal_id, email, ip_hash, prefix, (user_agent or "")[:200]))

        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "signal_id": signal_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def detect_abuse(email: str, ip_address: str = "") -> Dict:
    """
    Check if this email is likely a multi-account.

    Returns:
        {
            "flagged": bool,
            "severity": "clean" | "low" | "medium" | "high",
            "signals": [...],
            "accounts_from_ip": int,
            "accounts_from_prefix": int,
        }
    """
    email = (email or "").strip().lower()
    if not email:
        return {
            "flagged": False, "severity": "clean",
            "signals": [], "accounts_from_ip": 0, "accounts_from_prefix": 0,
        }

    ip_hash = hash_ip(ip_address)
    prefix = email_prefix(email)

    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()

        # Ensure table exists
        cur.execute("""
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'charvak_account_signals'
        """)
        if not cur.fetchone():
            cur.close()
            conn.close()
            return {
                "flagged": False, "severity": "clean",
                "signals": [], "accounts_from_ip": 0, "accounts_from_prefix": 0,
            }

        # Count accounts from this IP
        ip_count = 0
        if ip_hash:
            cur.execute("""
                SELECT COUNT(DISTINCT email) FROM charvak_account_signals
                WHERE ip_hash = %s
            """, (ip_hash,))
            row = cur.fetchone()
            ip_count = int(row[0]) if row and row[0] else 0

        # Count accounts from this prefix
        prefix_count = 0
        if prefix:
            cur.execute("""
                SELECT COUNT(DISTINCT email) FROM charvak_account_signals
                WHERE email_prefix = %s
            """, (prefix,))
            row = cur.fetchone()
            prefix_count = int(row[0]) if row and row[0] else 0

        cur.close()
        conn.close()

        # Compute severity
        signals = []
        if ip_count >= 5:
            signals.append(f"5+ accounts from same IP ({ip_count} total)")
        elif ip_count >= 3:
            signals.append(f"3+ accounts from same IP ({ip_count} total)")

        if prefix_count >= 3:
            signals.append(f"3+ accounts share email prefix '{prefix}'")

        if len(signals) >= 2:
            severity = "high"
        elif len(signals) == 1:
            severity = "medium"
        elif ip_count >= 2 or prefix_count >= 2:
            severity = "low"
        else:
            severity = "clean"

        return {
            "flagged": severity in ("medium", "high"),
            "severity": severity,
            "signals": signals,
            "accounts_from_ip": ip_count,
            "accounts_from_prefix": prefix_count,
        }
    except Exception as e:
        return {
            "flagged": False, "severity": "clean",
            "signals": [f"detection error: {e}"],
            "accounts_from_ip": 0, "accounts_from_prefix": 0,
        }