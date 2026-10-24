"""
google_oauth_engine.py
Session 82 — Google OAuth 2.0 flow for Charvak.
"""

# Load environment (matches database.py pattern)
from dotenv import load_dotenv as _load_dotenv
_load_dotenv(".env.local", override=True)
_load_dotenv()


import os
import json
import hmac
import hashlib
import secrets
import logging
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Dict

logger = logging.getLogger("charvakit.google_oauth")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def _get_config() -> Dict:
    return {
        "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "https://www.charvakit.com/api/auth/google/callback"),
    }


def is_configured() -> bool:
    cfg = _get_config()
    return bool(
        cfg["client_id"]
        and cfg["client_id"].endswith(".apps.googleusercontent.com")
        and cfg["client_secret"]
        and cfg["client_secret"].startswith("GOCSPX-")
    )


def _state_secret() -> str:
    return os.getenv("READINESS_HMAC_KEY") or os.getenv("SECRET_KEY") or "charvak-dev-oauth-state-secret"


def generate_state(next_url: str = "/") -> str:
    nonce = secrets.token_hex(8)
    expires_at = int(datetime.now().timestamp()) + 600
    payload = f"{nonce}|{expires_at}|{next_url[:200]}"
    sig = hmac.new(_state_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{payload}|{sig}"


def verify_state(state: str) -> Dict:
    if not state:
        raise ValueError("Missing state")
    parts = state.split("|")
    if len(parts) != 4:
        raise ValueError("Malformed state")
    nonce, expires_at_str, next_url, provided_sig = parts
    try:
        expires_at = int(expires_at_str)
    except ValueError:
        raise ValueError("Malformed expiry")
    if expires_at < int(datetime.now().timestamp()):
        raise ValueError("State expired")
    payload = f"{nonce}|{expires_at_str}|{next_url}"
    expected_sig = hmac.new(_state_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    if not hmac.compare_digest(provided_sig, expected_sig):
        raise ValueError("Invalid signature")
    return {"next_url": next_url}


def build_authorization_url(next_url: str = "/") -> str:
    cfg = _get_config()
    if not cfg["client_id"]:
        raise ValueError("GOOGLE_OAUTH_CLIENT_ID not configured")
    params = {
        "client_id": cfg["client_id"],
        "redirect_uri": cfg["redirect_uri"],
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": generate_state(next_url),
        "prompt": "select_account",
    }
    return GOOGLE_AUTH_URL + "?" + urllib.parse.urlencode(params)


def exchange_code_for_token(code: str) -> Dict:
    cfg = _get_config()
    if not cfg["client_id"] or not cfg["client_secret"]:
        raise ValueError("Google OAuth not configured")
    data = urllib.parse.urlencode({
        "code": code,
        "client_id": cfg["client_id"],
        "client_secret": cfg["client_secret"],
        "redirect_uri": cfg["redirect_uri"],
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request(
        GOOGLE_TOKEN_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            token_data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode() if hasattr(e, "read") else str(e)
        logger.error(f"Google token HTTP error: {e.code} {err_body}")
        raise ValueError(f"Token exchange failed: {err_body[:200]}")
    except Exception as e:
        logger.error(f"Google token exchange failed: {e}")
        raise ValueError(f"Token exchange failed: {e}")
    if "access_token" not in token_data:
        raise ValueError(f"No access_token in response")
    return token_data


def get_user_info(access_token: str) -> Dict:
    req = urllib.request.Request(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            user_data = json.loads(resp.read().decode())
    except Exception as e:
        logger.error(f"Google userinfo failed: {e}")
        raise ValueError(f"User info failed: {e}")
    if not user_data.get("email"):
        raise ValueError("No email in Google user info")
    return user_data


def _ensure_columns():
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS google_oauth_id TEXT")
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider TEXT DEFAULT 'password'")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.debug(f"_ensure_columns failed: {e}")


def find_or_create_user(google_user: Dict) -> Dict:
    _ensure_columns()
    email = (google_user.get("email") or "").strip().lower()
    name = (google_user.get("name") or "").strip() or email.split("@")[0]
    google_id = str(google_user.get("id") or "")
    if not email:
        raise ValueError("No email in Google user")

    from database import db
    conn = db.get_connection()
    cur = conn.cursor()

    if google_id:
        cur.execute("SELECT user_id, email, name, role FROM users WHERE google_oauth_id = %s LIMIT 1", (google_id,))
        row = cur.fetchone()
        if row:
            cur.close(); conn.close()
            return {"user_id": row[0], "email": row[1], "name": row[2], "role": row[3] or "candidate", "is_new": False}

    cur.execute("SELECT user_id, email, name, role, google_oauth_id FROM users WHERE LOWER(email) = %s LIMIT 1", (email,))
    row = cur.fetchone()

    if row:
        existing_user_id = row[0]
        existing_role = row[3] or "candidate"
        existing_google_id = row[4]
        if not existing_google_id and google_id:
            cur.execute(
                "UPDATE users SET google_oauth_id = %s, auth_provider = 'google', verified = TRUE WHERE user_id = %s",
                (google_id, existing_user_id),
            )
            conn.commit()
        cur.close(); conn.close()
        return {"user_id": existing_user_id, "email": email, "name": row[2] or name, "role": existing_role, "is_new": False}

    user_id = f"USR-{secrets.token_hex(6).upper()}"
    try:
        cur.execute(
            """
            INSERT INTO users (user_id, email, name, password_hash, role, verified, google_oauth_id, auth_provider, created_at)
            VALUES (%s, %s, %s, %s, 'candidate', TRUE, %s, 'google', NOW())
            RETURNING user_id
            """,
            (user_id, email, name, "", google_id),
        )
        conn.commit()
    except Exception as e:
        cur.execute("SELECT user_id, email, name, role FROM users WHERE LOWER(email) = %s LIMIT 1", (email,))
        row = cur.fetchone()
        cur.close(); conn.close()
        if row:
            return {"user_id": row[0], "email": row[1], "name": row[2], "role": row[3] or "candidate", "is_new": False}
        raise ValueError(f"Failed to create user: {e}")

    cur.close(); conn.close()
    return {"user_id": user_id, "email": email, "name": name, "role": "candidate", "is_new": True}