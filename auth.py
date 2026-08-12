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


def hash_password(password: str, salt: str = None) -> str:
    """Hash password with SHA-256 + salt."""
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash."""
    try:
        salt, expected = stored_hash.split("$")
        actual = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
        return hmac.compare_digest(actual, expected)
    except:
        return False


def register_user(email: str, password: str, name: str, role: str = "candidate", phone: str = None):
    """Register a new user with hashed password."""
    if len(password) < 8:
        return {"status": "error", "message": "Password must be at least 8 characters"}
    if not any(c.isupper() for c in password):
        return {"status": "error", "message": "Password must contain an uppercase letter"}
    if not any(c.isdigit() for c in password):
        return {"status": "error", "message": "Password must contain a number"}
    
    hashed_password = hash_password(password)
    result = db.create_user(email, hashed_password, name, role, phone)
    
    if result["status"] == "success":
        token = secrets.token_hex(32)
        active_tokens[token] = {
            "user_id": result["user_id"],
            "email": email,
            "role": role,
            "expires": datetime.now() + timedelta(days=7),
            "created_at": datetime.now().isoformat()
        }
        result["token"] = token
    return result


def login_user(email: str, password: str):
    """Login with password verification."""
    user = db.get_user_by_email(email)
    if not user:
        return {"status": "error", "message": "Invalid email or password"}
    
    if not verify_password(password, user.get("password_hash", user.get("password", ""))):
        return {"status": "error", "message": "Invalid email or password"}
    
    token = secrets.token_hex(32)
    active_tokens[token] = {
        "user_id": user["user_id"],
        "email": email,
        "role": user["role"],
        "expires": datetime.now() + timedelta(days=7),
        "created_at": datetime.now().isoformat()
    }
    return {"status": "success", "token": token, "user": user}


def verify_token(token: str) -> Optional[dict]:
    """Verify auth token."""
    if token in active_tokens:
        session = active_tokens[token]
        if session["expires"] > datetime.now():
            return session
        else:
            del active_tokens[token]
    return None


def logout_user(token: str):
    """Logout and invalidate token."""
    if token in active_tokens:
        del active_tokens[token]
        return {"status": "success"}
    return {"status": "error", "message": "Invalid token"}


def logout_all_sessions(user_id: str):
    """Invalidate all sessions for a user."""
    tokens_to_remove = [t for t, s in active_tokens.items() if s.get("user_id") == user_id]
    for token in tokens_to_remove:
        del active_tokens[token]
    return {"status": "success", "sessions_invalidated": len(tokens_to_remove)}


def get_current_user(token: str) -> Optional[dict]:
    """Get current user from token."""
    session = verify_token(token)
    if session:
        return db.get_user(session["user_id"])
    return None


def get_active_session_count(user_id: str) -> int:
    """Get number of active sessions for a user."""
    return len([s for s in active_tokens.values() if s.get("user_id") == user_id])