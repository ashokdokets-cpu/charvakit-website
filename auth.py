"""
Charvakit Authentication Module
Secure JWT-based auth with hashed passwords
"""
import hashlib
import secrets
import hmac
from datetime import datetime, timedelta
from typing import Optional
from database import db

active_tokens = {}


def _ensure_auth_tokens_table():
    """Create charvak_auth_tokens if missing. Idempotent."""
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charvak_auth_tokens (
                token        TEXT PRIMARY KEY,
                user_id      TEXT,
                email        TEXT NOT NULL,
                role         TEXT,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at   TIMESTAMP NOT NULL
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_auth_tokens_email ON charvak_auth_tokens (email)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_auth_tokens_expires ON charvak_auth_tokens (expires_at)")
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        print(f"auth._ensure_auth_tokens_table failed (non-fatal): {e}")


def _persist_token(token, user_id, email, role, expires_at):
    """Write token to DB. Idempotent on conflict."""
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO charvak_auth_tokens (token, user_id, email, role, expires_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (token) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                email = EXCLUDED.email,
                role = EXCLUDED.role,
                expires_at = EXCLUDED.expires_at
        """, (token, user_id, email, role, expires_at))
        conn.commit()
        cur.close(); conn.close()
        return True
    except Exception as e:
        print(f"auth._persist_token failed (non-fatal): {e}")
        return False


def _load_token_from_db(token):
    """Return token dict from DB if valid, else None."""
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, email, role, created_at, expires_at
            FROM charvak_auth_tokens
            WHERE token = %s AND expires_at > NOW()
        """, (token,))
        row = cur.fetchone()
        cur.close(); conn.close()
        if not row:
            return None
        return {
            "user_id": row[0],
            "email": row[1],
            "role": row[2],
            "created_at": row[3].isoformat() if row[3] else None,
            "expires": row[4],
        }
    except Exception as e:
        print(f"auth._load_token_from_db failed (non-fatal): {e}")
        return None


def _delete_token_from_db(token):
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM charvak_auth_tokens WHERE token = %s", (token,))
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        print(f"auth._delete_token_from_db failed (non-fatal): {e}")


def _delete_tokens_for_email(email):
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM charvak_auth_tokens WHERE email = %s", (email,))
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        print(f"auth._delete_tokens_for_email failed (non-fatal): {e}")


# Ensure table exists on module load
_ensure_auth_tokens_table()


def hash_password(password: str, salt: str = None) -> str:
    """Hash password with SHA-256 + salt."""
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash."""
    try:
        if "$" in stored_hash:
            salt, expected = stored_hash.split("$")
            actual = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
            return hmac.compare_digest(actual, expected)
        else:
            # Direct SHA-256 (old format)
            direct_hash = hashlib.sha256(password.encode()).hexdigest()
            return hmac.compare_digest(direct_hash, stored_hash)
    except:
        return False


def register_user(email: str, password: str, name: str, role: str = "candidate", phone: str = None):
    """Register a new user with hashed password."""
    # Password strength enforcement (12+ chars, mixed case, digit)
    if len(password) < 12:
        return {"status": "error", "message": "Password must be at least 12 characters"}
    if not any(c.isupper() for c in password):
        return {"status": "error", "message": "Password must contain an uppercase letter"}
    if not any(c.islower() for c in password):
        return {"status": "error", "message": "Password must contain a lowercase letter"}
    if not any(c.isdigit() for c in password):
        return {"status": "error", "message": "Password must contain a number"}
    # Reject obvious weak patterns
    lower = password.lower()
    common_weak = ["password", "123456", "qwerty", "admin", "letmein", "welcome"]
    if any(weak in lower for weak in common_weak):
        return {"status": "error", "message": "Password contains a common weak pattern. Please choose a stronger password."}

    hashed_password = hash_password(password)
    result = db.create_user(email, hashed_password, name, role, phone)

    if result["status"] == "success":
        token = secrets.token_hex(32)
        expires_at = datetime.now() + timedelta(days=7)
        active_tokens[token] = {
            "user_id": result["user_id"],
            "email": email,
            "role": role,
            "expires": expires_at,
            "created_at": datetime.now().isoformat()
        }
        _persist_token(token, result["user_id"], email, role, expires_at)
        result["token"] = token
    return result


def login_user(email: str, password: str):
    """Login with password verification."""
    user = db.get_user_by_email(email)
    if not user:
        return {"status": "error", "message": "Invalid email or password"}

    stored_hash = user.get("password_hash", user.get("password", ""))
    if not verify_password(password, stored_hash):
        return {"status": "error", "message": "Invalid email or password"}

    token = secrets.token_hex(32)
    expires_at = datetime.now() + timedelta(days=7)
    role = user.get("role", "candidate")
    active_tokens[token] = {
        "user_id": user["user_id"],
        "email": email,
        "role": role,
        "expires": expires_at,
        "created_at": datetime.now().isoformat()
    }
    _persist_token(token, user["user_id"], email, role, expires_at)
    return {"status": "success", "token": token, "user": user}


def verify_token(token: str) -> Optional[dict]:
    """Verify auth token. Checks memory cache, then DB."""
    if token in active_tokens:
        token_data = active_tokens[token]
        if datetime.now() < token_data["expires"]:
            return token_data
        else:
            del active_tokens[token]
            _delete_token_from_db(token)
            return None
    # Cache miss — check DB (survives process restarts)
    db_data = _load_token_from_db(token)
    if db_data:
        # Repopulate cache
        active_tokens[token] = db_data
        return db_data
    return None


def get_current_user(token: str) -> Optional[dict]:
    """Get current user from token."""
    token_data = verify_token(token)
    if token_data:
        return db.get_user_by_email(token_data["email"])
    return None


def logout_user(token: str):
    """Logout user."""
    _delete_token_from_db(token)
    if token in active_tokens:
        del active_tokens[token]
        return {"status": "success", "message": "Logged out"}
    return {"status": "success", "message": "Logged out"}


def logout_all_sessions(email: str):
    """Logout all sessions for a user."""
    tokens_to_remove = [t for t, data in active_tokens.items() if data["email"] == email]
    for token in tokens_to_remove:
        del active_tokens[token]
    _delete_tokens_for_email(email)
    return {"status": "success", "message": f"Logged out {len(tokens_to_remove)} sessions"}