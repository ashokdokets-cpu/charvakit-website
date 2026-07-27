"""
Charvakit Authentication Module
JWT-based auth for candidates and employers
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from database import db

# Simple token-based auth (can upgrade to JWT later)
active_tokens = {}

def register_user(email: str, password: str, name: str, role: str = "candidate", phone: str = None):
    """Register a new user"""
    if len(password) < 6:
        return {"status": "error", "message": "Password must be at least 6 characters"}
    
    result = db.create_user(email, password, name, role, phone)
    if result["status"] == "success":
        token = secrets.token_hex(32)
        active_tokens[token] = {
            "user_id": result["user_id"],
            "email": email,
            "role": role,
            "expires": datetime.now() + timedelta(days=30)
        }
        result["token"] = token
    return result

def login_user(email: str, password: str):
    """Login and return auth token"""
    user = db.authenticate_user(email, password)
    if user:
        token = secrets.token_hex(32)
        active_tokens[token] = {
            "user_id": user["user_id"],
            "email": email,
            "role": user["role"],
            "expires": datetime.now() + timedelta(days=30)
        }
        return {"status": "success", "token": token, "user": user}
    return {"status": "error", "message": "Invalid email or password"}

def verify_token(token: str) -> Optional[dict]:
    """Verify auth token"""
    if token in active_tokens:
        session = active_tokens[token]
        if session["expires"] > datetime.now():
            return session
        else:
            del active_tokens[token]
    return None

def logout_user(token: str):
    """Logout and invalidate token"""
    if token in active_tokens:
        del active_tokens[token]
        return {"status": "success"}
    return {"status": "error", "message": "Invalid token"}

def get_current_user(token: str) -> Optional[dict]:
    """Get current user from token"""
    session = verify_token(token)
    if session:
        return db.get_user(session["user_id"])
    return None