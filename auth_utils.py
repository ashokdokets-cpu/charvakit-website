"""
Shared auth helpers for student isolation.
Session 116 Day 4.

Loads .env at import time so SECRET_KEY is always available.
Uses the dedicated charvak_student_auth_tokens table (created in migration).
Does NOT touch charvak_auth_tokens (that's used by employer/main-site login).
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import hashlib
import secrets

# Load .env BEFORE reading SECRET_KEY (safe if already loaded; override=False keeps prod values)
try:
    from dotenv import load_dotenv
    load_dotenv(".env", override=False)
except ImportError:
    pass  # dotenv not installed — rely on real env vars

import jwt
from fastapi import Request, HTTPException

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not set. Add SECRET_KEY=<64-hex> to your .env, "
        "or set it as an environment variable before starting the app."
    )

STUDENT_COOKIE = "charvak_auth_token"
STUDENT_TOKEN_TTL_MIN = 15
STUDENT_SESSION_TTL_DAYS = 7


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_student_magic_token() -> str:
    """Returns raw token (email to student). Caller hashes before storing."""
    return secrets.token_urlsafe(32)


def create_student_session_token(student_id: str, email: str, college_slug: str) -> str:
    payload = {
        "sub": student_id,
        "email": email,
        "college_slug": college_slug,
        "role": "student",
        "exp": datetime.now(timezone.utc) + timedelta(days=STUDENT_SESSION_TTL_DAYS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def get_student_from_session(request: Request) -> Optional[Dict]:
    token = request.cookies.get(STUDENT_COOKIE)
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("role") != "student":
            return None
        return {
            "student_id": payload["sub"],
            "email": payload["email"],
            "college_slug": payload["college_slug"],
        }
    except Exception:
        return None


def require_student(request: Request, expected_college_slug: str) -> Dict:
    student = get_student_from_session(request)
    if not student:
        raise HTTPException(status_code=401, detail="Login required")
    if student["college_slug"] != expected_college_slug:
        raise HTTPException(status_code=403, detail="Wrong college")
    return student


def require_cert_ownership(request: Request, cert_id: str) -> Dict:
    student = get_student_from_session(request)
    if not student:
        raise HTTPException(status_code=401, detail="Login required")
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT student_id FROM charvak_career_certifications WHERE cert_id = %s",
            (cert_id,),
        )
        row = cur.fetchone()
        if not row or row[0] != student["student_id"]:
            raise HTTPException(status_code=403, detail="Not your certificate")
    finally:
        cur.close()
        conn.close()
    return student
# ============================================================
# DAY 5: COLLEGE ADMIN AUTHENTICATION
# ============================================================

def create_admin_magic_token() -> str:
    return secrets.token_urlsafe(32)

def create_admin_session_token(admin_id: str, email: str, college_slug: str) -> str:
    payload = {
        "sub": admin_id,
        "email": email,
        "college_slug": college_slug,
        "role": "college_admin",
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def get_admin_from_session(request: Request) -> Optional[Dict]:
    token = request.cookies.get(STUDENT_COOKIE) # Reuse the same cookie name for simplicity
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("role") != "college_admin":
            return None
        return {
            "admin_id": payload["sub"],
            "email": payload["email"],
            "college_slug": payload["college_slug"],
            "role": "college_admin"
        }
    except Exception:
        return None
