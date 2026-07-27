"""
Charvakit ↔ DoketsRB API Sync Module
Handles real-time data synchronization between both platforms
"""
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import hashlib
import hmac
import os
import json

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
    status: str  # applied, shortlisted, interviewing, offer, hired, rejected
    applied_date: Optional[str] = None
    source: str = "charvakit"  # charvakit, doketsrb, linkedin, etc.
    notes: Optional[str] = None

class SkillGapSync(BaseModel):
    user_id: str
    skill_gaps: List[dict]  # [{skill, current_level, required_level}]
    recommended_courses: Optional[List[str]] = []

class StatusRequest(BaseModel):
    user_id: str

# --- In-memory storage (replace with DB in production) ---
users_db = {}
applications_db = {}
skill_gaps_db = {}

# --- Auth Helper ---
def verify_api_key(request: Request):
    """Verify API key from header"""
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

def verify_signature(payload: bytes, signature: str):
    """Verify HMAC signature"""
    expected = hmac.new(API_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    return True

# --- API Endpoints ---

async def handle_resume_sync(data: ResumeSync, request: Request):
    """Receive resume data from DoketsRB"""
    # Verify signature
    body = await request.body()
    signature = request.headers.get("X-Signature", "")
    if signature:
        verify_signature(body, signature)
    
    # Store user data
    users_db[data.user_id] = {
        "doketsrb_id": data.doketsrb_id,
        "name": data.name,
        "email": data.email,
        "phone": data.phone,
        "resume_data": data.resume_data,
        "skills": data.skills,
        "experience": data.experience,
        "education": data.education,
        "synced_at": datetime.now().isoformat()
    }
    
    return JSONResponse({
        "status": "success",
        "message": f"Resume synced for user {data.user_id}",
        "synced_at": datetime.now().isoformat()
    })

async def handle_application_sync(data: ApplicationSync, request: Request):
    """Sync job application status"""
    body = await request.body()
    signature = request.headers.get("X-Signature", "")
    if signature:
        verify_signature(body, signature)
    
    app_id = data.application_id
    applications_db[app_id] = {
        "user_id": data.user_id,
        "job_title": data.job_title,
        "company": data.company,
        "job_url": data.job_url,
        "status": data.status,
        "applied_date": data.applied_date or datetime.now().strftime("%Y-%m-%d"),
        "source": data.source,
        "notes": data.notes,
        "last_updated": datetime.now().isoformat()
    }
    
    return JSONResponse({
        "status": "success",
        "message": f"Application {app_id} synced",
        "status": data.status
    })

async def handle_get_jobs(request: Request):
    """Return available jobs for DoketsRB tracker"""
    jobs = [
        {"id": "J001", "title": "Senior React Developer", "company": "TechCorp", "type": "Permanent", "location": "Bengaluru", "salary": "15-25 LPA"},
        {"id": "J002", "title": "Python Backend Developer", "company": "DataFlow", "type": "Contract", "location": "Remote", "salary": "12-18 LPA"},
        {"id": "J003", "title": "Full Stack Developer", "company": "WebSolutions", "type": "Contract-to-Hire", "location": "Hyderabad", "salary": "10-18 LPA"},
        {"id": "J004", "title": "DevOps Engineer", "company": "CloudFirst", "type": "Permanent", "location": "Remote", "salary": "12-20 LPA"},
    ]
    return JSONResponse({"status": "success", "count": len(jobs), "jobs": jobs})

async def handle_skill_sync(data: SkillGapSync, request: Request):
    """Receive skill gap analysis from DoketsRB"""
    body = await request.body()
    signature = request.headers.get("X-Signature", "")
    if signature:
        verify_signature(body, signature)
    
    skill_gaps_db[data.user_id] = {
        "skill_gaps": data.skill_gaps,
        "recommended_courses": data.recommended_courses,
        "synced_at": datetime.now().isoformat()
    }
    
    return JSONResponse({
        "status": "success",
        "message": f"Skill gaps synced for user {data.user_id}",
        "gaps_count": len(data.skill_gaps)
    })

async def handle_get_status(user_id: str, request: Request):
    """Get full career status for a user"""
    user = users_db.get(user_id, {})
    user_apps = {k: v for k, v in applications_db.items() if v.get("user_id") == user_id}
    gaps = skill_gaps_db.get(user_id, {})
    
    return JSONResponse({
        "user_id": user_id,
        "profile": user,
        "applications": user_apps,
        "applications_count": len(user_apps),
        "skill_gaps": gaps.get("skill_gaps", []),
        "recommended_courses": gaps.get("recommended_courses", []),
        "last_synced": user.get("synced_at", "Never")
    })

# --- Health Check ---
async def api_health():
    return JSONResponse({
        "status": "healthy",
        "service": "Charvakit Sync API",
        "version": "1.0.0",
        "endpoints": [
            "POST /api/sync/resume",
            "POST /api/sync/application",
            "GET /api/sync/jobs",
            "POST /api/sync/skills",
            "GET /api/sync/status/{user_id}"
        ]
    })