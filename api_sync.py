"""
Charvakit <-> DoketsRB API Sync Module
Real-time data synchronization between both platforms.

Database-backed: uses charvak_synced_users, charvak_synced_applications, charvak_skill_gaps.
Preserves all original function signatures — main.py unchanged.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import hashlib
import hmac
import json
import logging
import os

logger = logging.getLogger("charvakit.api_sync")

# --- Configuration ---
API_SECRET = os.getenv("SYNC_API_SECRET", "charvak-doketsrb-sync-secret-2024")
API_KEY = os.getenv("SYNC_API_KEY", "cvk_sync_key_2024")


# --- Data Models ---
class ResumeSync(BaseModel):
    user_id: str
    doketsrb_id: str
    name: str
    email: str
    phone: Optional[str] = None
    resume_data: dict
    skills: List[str]
    experience: Optional[List[dict]] = []
    education: Optional[List[dict]] = []


class ApplicationSync(BaseModel):
    user_id: str
    application_id: str
    job_title: str
    company: str
    job_url: Optional[str] = None
    status: str
    applied_date: Optional[str] = None
    source: str = "charvakit"
    notes: Optional[str] = None


class SkillGapSync(BaseModel):
    user_id: str
    skill_gaps: List[dict]
    recommended_courses: Optional[List[str]] = []


class StatusRequest(BaseModel):
    user_id: str


# --- Auth Helpers ---
def verify_api_key(request: Request):
    """Verify API key from header."""
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


def verify_signature(payload: bytes, signature: str):
    """Verify HMAC signature."""
    expected = hmac.new(API_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    return True


# --- Database Helpers ---
def _ensure_tables():
    """Idempotent creation of sync tables."""
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charvak_synced_users (
                user_id TEXT PRIMARY KEY,
                doketsrb_id TEXT,
                name TEXT,
                email TEXT,
                phone TEXT,
                resume_data JSONB,
                skills JSONB,
                experience JSONB,
                education JSONB,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charvak_synced_applications (
                application_id TEXT PRIMARY KEY,
                user_id TEXT,
                job_title TEXT,
                company TEXT,
                job_url TEXT,
                status TEXT,
                applied_date TEXT,
                source TEXT DEFAULT 'charvakit',
                notes TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charvak_skill_gaps (
                user_id TEXT PRIMARY KEY,
                skill_gaps JSONB,
                recommended_courses JSONB,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Sync table init failed: {e}")


_ensure_tables()


# --- API Handlers ---

async def handle_resume_sync(data: ResumeSync, request: Request):
    """Receive resume data from DoketsRB. Persists to charvak_synced_users."""
    body = await request.body()
    signature = request.headers.get("X-Signature", "")
    if signature:
        verify_signature(body, signature)

    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO charvak_synced_users
                (user_id, doketsrb_id, name, email, phone, resume_data, skills, experience, education, synced_at)
            VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id) DO UPDATE SET
                doketsrb_id = EXCLUDED.doketsrb_id,
                name = EXCLUDED.name,
                email = EXCLUDED.email,
                phone = EXCLUDED.phone,
                resume_data = EXCLUDED.resume_data,
                skills = EXCLUDED.skills,
                experience = EXCLUDED.experience,
                education = EXCLUDED.education,
                synced_at = CURRENT_TIMESTAMP
        """, (
            data.user_id,
            data.doketsrb_id,
            data.name,
            data.email,
            data.phone,
            json.dumps(data.resume_data or {}),
            json.dumps(data.skills or []),
            json.dumps(data.experience or []),
            json.dumps(data.education or []),
        ))
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Resume synced: {data.user_id}")

        return JSONResponse({
            "status": "success",
            "message": f"Resume synced for user {data.user_id}",
            "synced_at": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"handle_resume_sync failed: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


async def handle_application_sync(data: ApplicationSync, request: Request):
    """Sync job application status. Persists to charvak_synced_applications."""
    body = await request.body()
    signature = request.headers.get("X-Signature", "")
    if signature:
        verify_signature(body, signature)

    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO charvak_synced_applications
                (application_id, user_id, job_title, company, job_url, status, applied_date, source, notes, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (application_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                job_title = EXCLUDED.job_title,
                company = EXCLUDED.company,
                job_url = EXCLUDED.job_url,
                status = EXCLUDED.status,
                applied_date = EXCLUDED.applied_date,
                source = EXCLUDED.source,
                notes = EXCLUDED.notes,
                last_updated = CURRENT_TIMESTAMP
        """, (
            data.application_id,
            data.user_id,
            data.job_title,
            data.company,
            data.job_url,
            data.status,
            data.applied_date or datetime.now().strftime("%Y-%m-%d"),
            data.source,
            data.notes,
        ))
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Application synced: {data.application_id}")

        return JSONResponse({
            "status": "success",
            "message": f"Application {data.application_id} synced",
            "status": data.status
        })
    except Exception as e:
        logger.error(f"handle_application_sync failed: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


async def handle_get_jobs(request: Request):
    """Return available jobs for DoketsRB tracker. Reads from charvak_jobs."""
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT job_id, title, company, job_type, location, salary
            FROM charvak_jobs
            WHERE status = 'active'
            ORDER BY created_at DESC LIMIT 100
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        jobs = [
            {
                "id": r[0],
                "title": r[1],
                "company": r[2],
                "type": r[3],
                "location": r[4],
                "salary": r[5],
            }
            for r in rows
        ]
        return JSONResponse({"status": "success", "count": len(jobs), "jobs": jobs})
    except Exception as e:
        logger.error(f"handle_get_jobs failed: {e}")
        return JSONResponse({"status": "success", "count": 0, "jobs": [], "error": str(e)})


async def handle_skill_sync(data: SkillGapSync, request: Request):
    """Receive skill gap analysis from DoketsRB. Persists to charvak_skill_gaps."""
    body = await request.body()
    signature = request.headers.get("X-Signature", "")
    if signature:
        verify_signature(body, signature)

    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO charvak_skill_gaps
                (user_id, skill_gaps, recommended_courses, synced_at)
            VALUES (%s, %s::jsonb, %s::jsonb, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id) DO UPDATE SET
                skill_gaps = EXCLUDED.skill_gaps,
                recommended_courses = EXCLUDED.recommended_courses,
                synced_at = CURRENT_TIMESTAMP
        """, (
            data.user_id,
            json.dumps(data.skill_gaps or []),
            json.dumps(data.recommended_courses or []),
        ))
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Skill gaps synced: {data.user_id}")

        return JSONResponse({
            "status": "success",
            "message": f"Skill gaps synced for user {data.user_id}",
            "gaps_count": len(data.skill_gaps)
        })
    except Exception as e:
        logger.error(f"handle_skill_sync failed: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


async def handle_get_status(user_id: str, request: Request):
    """Get full career status for a user."""
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()

        # User profile
        cur.execute("""
            SELECT user_id, doketsrb_id, name, email, phone, resume_data, skills, experience, education, synced_at
            FROM charvak_synced_users WHERE user_id = %s
        """, (user_id,))
        user_row = cur.fetchone()
        user = {}
        if user_row:
            user = {
                "user_id": user_row[0],
                "doketsrb_id": user_row[1],
                "name": user_row[2],
                "email": user_row[3],
                "phone": user_row[4],
                "resume_data": user_row[5],
                "skills": user_row[6],
                "experience": user_row[7],
                "education": user_row[8],
                "synced_at": user_row[9].isoformat() if user_row[9] else None,
            }

        # Applications
        cur.execute("""
            SELECT application_id, job_title, company, job_url, status, applied_date, source, notes, last_updated
            FROM charvak_synced_applications WHERE user_id = %s
            ORDER BY last_updated DESC LIMIT 100
        """, (user_id,))
        apps_rows = cur.fetchall()
        user_apps = {}
        for r in apps_rows:
            user_apps[r[0]] = {
                "user_id": user_id,
                "job_title": r[1],
                "company": r[2],
                "job_url": r[3],
                "status": r[4],
                "applied_date": r[5],
                "source": r[6],
                "notes": r[7],
                "last_updated": r[8].isoformat() if r[8] else None,
            }

        # Skill gaps
        cur.execute("""
            SELECT skill_gaps, recommended_courses FROM charvak_skill_gaps WHERE user_id = %s
        """, (user_id,))
        gap_row = cur.fetchone()
        skill_gaps = gap_row[0] if gap_row else []
        recommended = gap_row[1] if gap_row else []

        cur.close()
        conn.close()

        return JSONResponse({
            "user_id": user_id,
            "profile": user,
            "applications": user_apps,
            "applications_count": len(user_apps),
            "skill_gaps": skill_gaps or [],
            "recommended_courses": recommended or [],
            "last_synced": user.get("synced_at", "Never") if user else "Never"
        })
    except Exception as e:
        logger.error(f"handle_get_status failed: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


# --- Health Check ---
async def api_health():
    return JSONResponse({
        "status": "healthy",
        "service": "Charvakit Sync API",
        "version": "1.1.0",
        "endpoints": [
            "POST /api/sync/resume",
            "POST /api/sync/application",
            "GET /api/sync/jobs",
            "POST /api/sync/skills",
            "GET /api/sync/status/{user_id}"
        ]
    })