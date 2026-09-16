"""
Charvak Micro-Internship Engine
Complete end-to-end system: Post → Screen → Assign → Track → Pay
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets
import json

logger = logging.getLogger("charvakit.microinternship")


class ProjectStatus:
    OPEN = "open"
    IN_REVIEW = "in_review"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ApplicationStatus:
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    ASSIGNED = "assigned"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class MicroInternshipEngine:
    """Complete micro-internship management system."""
    
    def __init__(self):
        self._ensure_tables()
        logger.info("Micro-Internship Engine ready (DB-backed)")

    def _ensure_tables(self):
        """Idempotent table creation for micro-internship tables."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_micro_clients (
                    client_id         TEXT PRIMARY KEY,
                    company_name      TEXT NOT NULL,
                    contact_email     TEXT NOT NULL,
                    contact_name      TEXT,
                    industry          TEXT DEFAULT '',
                    company_size      TEXT DEFAULT '',
                    total_projects    INTEGER DEFAULT 0,
                    active_projects   INTEGER DEFAULT 0,
                    total_spend       NUMERIC(12,2) DEFAULT 0,
                    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_micro_projects (
                    project_id        TEXT PRIMARY KEY,
                    title             TEXT NOT NULL,
                    category          TEXT DEFAULT 'Web Development',
                    difficulty        TEXT DEFAULT 'Intermediate',
                    duration_weeks    INTEGER DEFAULT 2,
                    budget_inr        NUMERIC(12,2) NOT NULL,
                    budget_usd        NUMERIC(12,2),
                    skills_required   JSONB DEFAULT '[]'::jsonb,
                    description       TEXT DEFAULT '',
                    client_id         TEXT,
                    company_name      TEXT,
                    contact_email     TEXT,
                    escrow_required   BOOLEAN DEFAULT TRUE,
                    escrow_id         TEXT,
                    assigned_intern   JSONB,
                    status            TEXT DEFAULT 'open',
                    applications_count INTEGER DEFAULT 0,
                    milestones        JSONB DEFAULT '[]'::jsonb,
                    submission        JSONB,
                    feedback          TEXT,
                    rating            INTEGER,
                    deadline          TIMESTAMP,
                    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at      TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_micro_applications (
                    application_id    TEXT PRIMARY KEY,
                    project_id        TEXT NOT NULL,
                    candidate_name    TEXT,
                    candidate_email   TEXT,
                    skills            JSONB DEFAULT '[]'::jsonb,
                    portfolio_url     TEXT DEFAULT '',
                    why_interested    TEXT DEFAULT '',
                    status            TEXT DEFAULT 'applied',
                    ai_score          INTEGER DEFAULT 0,
                    applied_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assigned_at       TIMESTAMP,
                    submitted_at      TIMESTAMP,
                    approved_at       TIMESTAMP
                )
            """)
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"micro tables init failed: {e}")


    # ============================================================
    # CLIENT MANAGEMENT
    # ============================================================
    
    def register_client(self, data: Dict) -> Dict:
        """Register a client company."""
        client_id = f"CLIENT-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_micro_clients
                    (client_id, company_name, contact_email, contact_name,
                     industry, company_size)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (client_id, data.get("company_name"), data.get("contact_email"),
                  data.get("contact_name"), data.get("industry", ""),
                  data.get("company_size", "")))
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"Client registered: {client_id} - {data.get('company_name')}")
            return {
                "status": "success",
                "client_id": client_id,
                "message": "Client registered successfully"
            }
        except Exception as e:
            logger.error(f"register_client failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_client(self, client_id: str) -> Optional[Dict]:
        """Get client by ID."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT client_id, company_name, contact_email, contact_name,
                       industry, company_size, total_projects, active_projects,
                       total_spend, created_at
                FROM charvak_micro_clients WHERE client_id = %s
            """, (client_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
            if not row:
                return None
            return {
                "client_id": row[0],
                "company_name": row[1],
                "contact_email": row[2],
                "contact_name": row[3],
                "industry": row[4] or "",
                "company_size": row[5] or "",
                "total_projects": row[6] or 0,
                "active_projects": row[7] or 0,
                "total_spend": float(row[8] or 0),
                "created_at": row[9].isoformat() if row[9] else None,
            }
        except Exception as e:
            logger.error(f"get_client failed: {e}")
            return None


    def get_client_dashboard(self, client_id: str) -> Dict:
        """Get full client dashboard with all projects and applications."""
        client = self.get_client(client_id)
        if not client:
            return {"status": "error", "message": "Client not found"}
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT project_id, title, category, difficulty, duration_weeks,
                       budget_inr, budget_usd, skills_required, description,
                       client_id, company_name, contact_email, escrow_required,
                       escrow_id, assigned_intern, status, applications_count,
                       milestones, submission, feedback, rating, deadline,
                       created_at, completed_at
                FROM charvak_micro_projects WHERE client_id = %s
                ORDER BY created_at DESC
            """, (client_id,))
            proj_rows = cur.fetchall()
            projects = []
            project_ids = []
            for r in proj_rows:
                projects.append({
                    "project_id": r[0], "title": r[1], "category": r[2],
                    "difficulty": r[3], "duration_weeks": r[4],
                    "budget_inr": float(r[5] or 0), "budget_usd": float(r[6] or 0),
                    "skills_required": r[7] if isinstance(r[7], list) else json.loads(r[7] or "[]"),
                    "description": r[8] or "", "client_id": r[9],
                    "company_name": r[10], "contact_email": r[11],
                    "escrow_required": bool(r[12]), "escrow_id": r[13],
                    "assigned_intern": r[14] if isinstance(r[14], dict) else (json.loads(r[14]) if r[14] else None),
                    "status": r[15], "applications_count": r[16] or 0,
                    "milestones": r[17] if isinstance(r[17], list) else json.loads(r[17] or "[]"),
                    "submission": r[18] if isinstance(r[18], dict) else (json.loads(r[18]) if r[18] else None),
                    "feedback": r[19] or "", "rating": r[20] or 0,
                    "deadline": r[21].isoformat() if r[21] else None,
                    "created_at": r[22].isoformat() if r[22] else None,
                    "completed_at": r[23].isoformat() if r[23] else None,
                })
                project_ids.append(r[0])
            applications = []
            if project_ids:
                cur.execute("""
                    SELECT application_id, project_id, candidate_name, candidate_email,
                           skills, portfolio_url, why_interested, status, ai_score,
                           applied_at, assigned_at, submitted_at, approved_at
                    FROM charvak_micro_applications WHERE project_id = ANY(%s)
                    ORDER BY applied_at DESC
                """, (project_ids,))
                for r in cur.fetchall():
                    applications.append({
                        "application_id": r[0], "project_id": r[1],
                        "candidate_name": r[2], "candidate_email": r[3],
                        "skills": r[4] if isinstance(r[4], list) else json.loads(r[4] or "[]"),
                        "portfolio_url": r[5] or "", "why_interested": r[6] or "",
                        "status": r[7], "ai_score": r[8] or 0,
                        "applied_at": r[9].isoformat() if r[9] else None,
                        "assigned_at": r[10].isoformat() if r[10] else None,
                        "submitted_at": r[11].isoformat() if r[11] else None,
                        "approved_at": r[12].isoformat() if r[12] else None,
                    })
            cur.close(); conn.close()
            return {
                "status": "success",
                "client": client,
                "projects": projects,
                "applications": applications,
                "stats": {
                    "total_projects": len(projects),
                    "active_projects": len([p for p in projects if p["status"] in ["assigned", "in_progress"]]),
                    "total_applications": len(applications),
                    "total_spend": client["total_spend"],
                    "hired_count": len([p for p in projects if p["status"] == "completed"])
                }
            }
        except Exception as e:
            logger.error(f"get_client_dashboard failed: {e}")
            return {"status": "error", "message": str(e)}


    # ============================================================
    # PROJECT MANAGEMENT
    # ============================================================
    
    def post_project(self, data: Dict) -> Dict:
        """Post a new micro-internship project."""
        project_id = f"PROJ-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        duration_weeks = int(data.get("duration_weeks", 2))
        budget_inr = float(data.get("budget_inr", 5000))
        skills_required = data.get("skills_required", [])
        milestones = self._generate_milestones(duration_weeks, budget_inr)
        deadline = datetime.now() + timedelta(weeks=duration_weeks)
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_micro_projects
                    (project_id, title, category, difficulty, duration_weeks,
                     budget_inr, budget_usd, skills_required, description,
                     client_id, company_name, contact_email, escrow_required,
                     milestones, status, applications_count, deadline)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s,
                        %s, %s, %s, %s, %s::jsonb, 'open', 0, %s)
            """, (project_id, data.get("title"),
                  data.get("category", "Web Development"),
                  data.get("difficulty", "Intermediate"),
                  duration_weeks, budget_inr, round(budget_inr / 83, 2),
                  json.dumps(skills_required), data.get("description", ""),
                  data.get("client_id"), data.get("company_name"),
                  data.get("contact_email"), data.get("escrow_required", True),
                  json.dumps(milestones), deadline))
            # Create escrow if required
            escrow_id = None
            if data.get("escrow_required", True):
                try:
                    from escrow_engine import escrow_engine
                    escrow_resp = escrow_engine.create_escrow({
                        "client_name": data.get("company_name"),
                        "client_email": data.get("contact_email"),
                        "vendor_name": "Pending assignment",
                        "vendor_email": "",
                        "amount": budget_inr,
                        "currency": "INR",
                        "description": f"Micro-internship: {data.get('title')}",
                        "milestones": milestones,
                        "duration_days": duration_weeks * 7,
                    })
                    if escrow_resp.get("status") == "success":
                        escrow_id = escrow_resp["escrow_id"]
                        cur.execute("""
                            UPDATE charvak_micro_projects
                            SET escrow_id = %s WHERE project_id = %s
                        """, (escrow_id, project_id))
                        logger.info(f"Escrow created for project {project_id}: {escrow_id}")
                except Exception as ee:
                    logger.warning(f"escrow creation failed (non-fatal): {ee}")

            # Increment client's total_projects
            if data.get("client_id"):
                cur.execute("""
                    UPDATE charvak_micro_clients
                    SET total_projects = total_projects + 1
                    WHERE client_id = %s
                """, (data.get("client_id"),))
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"Project posted: {project_id} - {data.get('title')}")
            return {
                "status": "success",
                "project_id": project_id,
                "message": "Project posted successfully! Candidates can now apply.",
                "project_url": f"https://charvakit.com/micro-internship/{project_id}",
                "escrow": {
                    "required": data.get("escrow_required", True),
                    "amount": budget_inr,
                    "escrow_id": escrow_id,
                    "status": "pending_deposit" if escrow_id else ("not_required" if not data.get("escrow_required", True) else "creation_failed")
                }
            }
        except Exception as e:
            logger.error(f"post_project failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_project(self, project_id: str) -> Dict:
        """Get project details."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT project_id, title, category, difficulty, duration_weeks,
                       budget_inr, budget_usd, skills_required, description,
                       client_id, company_name, contact_email, escrow_required,
                       escrow_id, assigned_intern, status, applications_count,
                       milestones, submission, feedback, rating, deadline,
                       created_at, completed_at
                FROM charvak_micro_projects WHERE project_id = %s
            """, (project_id,))
            r = cur.fetchone()
            cur.close(); conn.close()
            if not r:
                return {"status": "error", "message": "Project not found"}
            return {"status": "success", "project": {
                "project_id": r[0], "title": r[1], "category": r[2],
                "difficulty": r[3], "duration_weeks": r[4],
                "budget_inr": float(r[5] or 0), "budget_usd": float(r[6] or 0),
                "skills_required": r[7] if isinstance(r[7], list) else json.loads(r[7] or "[]"),
                "description": r[8] or "", "client_id": r[9],
                "company_name": r[10], "contact_email": r[11],
                "escrow_required": bool(r[12]), "escrow_id": r[13],
                "assigned_intern": r[14] if isinstance(r[14], dict) else (json.loads(r[14]) if r[14] else None),
                "status": r[15], "applications_count": r[16] or 0,
                "milestones": r[17] if isinstance(r[17], list) else json.loads(r[17] or "[]"),
                "submission": r[18] if isinstance(r[18], dict) else (json.loads(r[18]) if r[18] else None),
                "feedback": r[19] or "", "rating": r[20] or 0,
                "deadline": r[21].isoformat() if r[21] else None,
                "created_at": r[22].isoformat() if r[22] else None,
                "completed_at": r[23].isoformat() if r[23] else None,
            }}
        except Exception as e:
            logger.error(f"get_project failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_open_projects(self, filters: Dict = None) -> Dict:
        """Get all open projects for candidate browsing."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            where = ["status = 'open'"]
            params = []
            if filters:
                if filters.get("category"):
                    where.append("category = %s"); params.append(filters["category"])
                if filters.get("difficulty"):
                    where.append("difficulty = %s"); params.append(filters["difficulty"])
                if filters.get("max_budget"):
                    where.append("budget_inr <= %s"); params.append(filters["max_budget"])
            sql = """
                SELECT project_id, title, category, difficulty, duration_weeks,
                       budget_inr, budget_usd, skills_required, description,
                       client_id, company_name, contact_email, escrow_required,
                       escrow_id, assigned_intern, status, applications_count,
                       milestones, submission, feedback, rating, deadline,
                       created_at, completed_at
                FROM charvak_micro_projects WHERE """ + " AND ".join(where) + " ORDER BY created_at DESC"
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            projects = []
            for r in rows:
                proj = {
                    "project_id": r[0], "title": r[1], "category": r[2],
                    "difficulty": r[3], "duration_weeks": r[4],
                    "budget_inr": float(r[5] or 0), "budget_usd": float(r[6] or 0),
                    "skills_required": r[7] if isinstance(r[7], list) else json.loads(r[7] or "[]"),
                    "description": r[8] or "", "client_id": r[9],
                    "company_name": r[10], "contact_email": r[11],
                    "escrow_required": bool(r[12]), "escrow_id": r[13],
                    "assigned_intern": r[14] if isinstance(r[14], dict) else (json.loads(r[14]) if r[14] else None),
                    "status": r[15], "applications_count": r[16] or 0,
                    "milestones": r[17] if isinstance(r[17], list) else json.loads(r[17] or "[]"),
                    "submission": r[18] if isinstance(r[18], dict) else (json.loads(r[18]) if r[18] else None),
                    "feedback": r[19] or "", "rating": r[20] or 0,
                    "deadline": r[21].isoformat() if r[21] else None,
                    "created_at": r[22].isoformat() if r[22] else None,
                    "completed_at": r[23].isoformat() if r[23] else None,
                }
                # Optional skill substring filter (post-query, JSONB skill search is complex)
                if filters and filters.get("skill"):
                    if filters["skill"].lower() not in " ".join(proj["skills_required"]).lower():
                        continue
                projects.append(proj)
            cur.execute("SELECT DISTINCT category FROM charvak_micro_projects")
            cats = [row[0] for row in cur.fetchall()]
            cur.close(); conn.close()
            return {
                "status": "success",
                "projects": projects,
                "count": len(projects),
                "categories": cats,
                "total_budget": sum(p["budget_inr"] for p in projects),
            }
        except Exception as e:
            logger.error(f"get_open_projects failed: {e}")
            return {"status": "error", "message": str(e), "projects": [], "count": 0}


    def _generate_milestones(self, weeks: int, budget: float) -> List[Dict]:
        """Generate project milestones."""
        milestones = []
        if weeks == 1:
            milestones = [
                {"name": "Project Kickoff", "week": 1, "payment": round(budget * 0.3, 2)},
                {"name": "Final Delivery", "week": 1, "payment": round(budget * 0.7, 2)}
            ]
        elif weeks == 2:
            milestones = [
                {"name": "Project Kickoff", "week": 1, "payment": round(budget * 0.2, 2)},
                {"name": "Mid-Project Review", "week": 1, "payment": round(budget * 0.3, 2)},
                {"name": "Final Delivery", "week": 2, "payment": round(budget * 0.5, 2)}
            ]
        else:
            milestones = [
                {"name": "Project Kickoff", "week": 1, "payment": round(budget * 0.15, 2)},
                {"name": "Progress Checkpoint", "week": weeks // 2, "payment": round(budget * 0.25, 2)},
                {"name": "Final Review", "week": weeks - 1, "payment": round(budget * 0.25, 2)},
                {"name": "Project Completion", "week": weeks, "payment": round(budget * 0.35, 2)}
            ]
        return milestones
    
    # ============================================================
    # APPLICATION MANAGEMENT
    # ============================================================
    
    def apply_to_project(self, data: Dict) -> Dict:
        """Candidate applies to a project."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT status, skills_required FROM charvak_micro_projects WHERE project_id = %s", (data.get("project_id"),))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Project not found"}
            if row[0] != "open":
                cur.close(); conn.close()
                return {"status": "error", "message": "Project is no longer accepting applications"}
            required_skills = row[1] if isinstance(row[1], list) else json.loads(row[1] or "[]")
            application_id = f"APP-{secrets.token_hex(4).upper()}"
            ai_score = self._calculate_ai_score(data.get("skills", []), required_skills)
            cur.execute("""
                INSERT INTO charvak_micro_applications
                    (application_id, project_id, candidate_name, candidate_email,
                     skills, portfolio_url, why_interested, status, ai_score)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, 'applied', %s)
            """, (application_id, data.get("project_id"), data.get("candidate_name"),
                  data.get("candidate_email"), json.dumps(data.get("skills", [])),
                  data.get("portfolio_url", ""), data.get("why_interested", ""),
                  ai_score))
            cur.execute("""
                UPDATE charvak_micro_projects
                SET applications_count = applications_count + 1
                WHERE project_id = %s
            """, (data.get("project_id"),))
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"Application received: {application_id} for {data.get('project_id')}")
            return {
                "status": "success",
                "application_id": application_id,
                "ai_match_score": ai_score,
                "message": "Application submitted! The client will review your profile."
            }
        except Exception as e:
            logger.error(f"apply_to_project failed: {e}")
            return {"status": "error", "message": str(e)}


    def _calculate_ai_score(self, candidate_skills: List[str], required_skills: List[str]) -> int:
        """Calculate AI match score between candidate and project."""
        if not required_skills:
            return 70  # Default score if no skills specified
        
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        required_skills_lower = [s.lower() for s in required_skills]
        
        matches = 0
        for req_skill in required_skills_lower:
            for cand_skill in candidate_skills_lower:
                if req_skill in cand_skill or cand_skill in req_skill:
                    matches += 1
                    break
        
        score = int((matches / len(required_skills_lower)) * 100)
        return min(score, 100)
    
    def get_project_applications(self, project_id: str) -> Dict:
        """Get all applications for a project."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT application_id, project_id, candidate_name, candidate_email,
                       skills, portfolio_url, why_interested, status, ai_score,
                       applied_at, assigned_at, submitted_at, approved_at
                FROM charvak_micro_applications WHERE project_id = %s
                ORDER BY ai_score DESC
            """, (project_id,))
            apps = []
            for r in cur.fetchall():
                apps.append({
                    "application_id": r[0], "project_id": r[1],
                    "candidate_name": r[2], "candidate_email": r[3],
                    "skills": r[4] if isinstance(r[4], list) else json.loads(r[4] or "[]"),
                    "portfolio_url": r[5] or "", "why_interested": r[6] or "",
                    "status": r[7], "ai_score": r[8] or 0,
                    "applied_at": r[9].isoformat() if r[9] else None,
                    "assigned_at": r[10].isoformat() if r[10] else None,
                    "submitted_at": r[11].isoformat() if r[11] else None,
                    "approved_at": r[12].isoformat() if r[12] else None,
                })
            cur.close(); conn.close()
            shortlisted = [a for a in apps if a["status"] == "shortlisted"]
            avg = sum(a["ai_score"] for a in apps) / len(apps) if apps else 0
            return {"status": "success", "applications": apps, "count": len(apps),
                    "shortlisted": shortlisted, "average_score": avg}
        except Exception as e:
            logger.error(f"get_project_applications failed: {e}")
            return {"status": "error", "message": str(e), "applications": [], "count": 0}


    # ============================================================
    # ASSIGNMENT & TRACKING
    # ============================================================
    
    def assign_intern(self, project_id: str, application_id: str) -> Dict:
        """Assign a candidate to a project."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT project_id, title, escrow_required, budget_inr FROM charvak_micro_projects WHERE project_id = %s", (project_id,))
            proj = cur.fetchone()
            if not proj:
                cur.close(); conn.close()
                return {"status": "error", "message": "Project not found"}
            cur.execute("SELECT candidate_name, candidate_email FROM charvak_micro_applications WHERE application_id = %s AND project_id = %s", (application_id, project_id))
            app = cur.fetchone()
            if not app:
                cur.close(); conn.close()
                return {"status": "error", "message": "Application not found"}
            intern = {"name": app[0], "email": app[1], "application_id": application_id}
            cur.execute("""
                UPDATE charvak_micro_projects
                SET assigned_intern = %s::jsonb, status = 'assigned'
                WHERE project_id = %s
            """, (json.dumps(intern), project_id))
            cur.execute("""
                UPDATE charvak_micro_applications
                SET status = 'assigned', assigned_at = CURRENT_TIMESTAMP
                WHERE application_id = %s
            """, (application_id,))
            conn.commit()
            cur.close(); conn.close()
            return {
                "status": "success",
                "message": f"{app[0]} assigned to {proj[1]}",
                "next_step": "Project started. Intern can begin work.",
                "escrow_required": bool(proj[2]),
                "escrow_amount": float(proj[3] or 0),
            }
        except Exception as e:
            logger.error(f"assign_intern failed: {e}")
            return {"status": "error", "message": str(e)}


    def submit_work(self, project_id: str, submission_data: Dict) -> Dict:
        """Intern submits work for review."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT project_id FROM charvak_micro_projects WHERE project_id = %s", (project_id,))
            if not cur.fetchone():
                cur.close(); conn.close()
                return {"status": "error", "message": "Project not found"}
            submission = {
                "deliverables": submission_data.get("deliverables", ""),
                "submitted_at": datetime.now().isoformat(),
                "notes": submission_data.get("notes", ""),
            }
            cur.execute("""
                UPDATE charvak_micro_projects
                SET submission = %s::jsonb, status = 'submitted'
                WHERE project_id = %s
            """, (json.dumps(submission), project_id))
            cur.execute("""
                UPDATE charvak_micro_applications
                SET status = 'submitted', submitted_at = CURRENT_TIMESTAMP
                WHERE project_id = %s AND status = 'assigned'
            """, (project_id,))

            # Advance escrow to 'work_delivered' so it can be released on approval
            escrow_delivered = False
            cur.execute("SELECT escrow_id FROM charvak_micro_projects WHERE project_id = %s", (project_id,))
            esc_row = cur.fetchone()
            if esc_row and esc_row[0]:
                try:
                    from escrow_engine import escrow_engine
                    del_result = escrow_engine.deliver_work(esc_row[0], {
                        "deliverables": submission_data.get("deliverables", ""),
                        "notes": submission_data.get("notes", ""),
                        "source": "micro_internship.submit_work",
                    })
                    if del_result.get("status") == "success":
                        escrow_delivered = True
                        logger.info(f"Escrow delivered for project {project_id}: {esc_row[0]}")
                    else:
                        logger.warning(f"escrow deliver_work returned: {del_result.get('message')}")
                except Exception as ee:
                    logger.warning(f"escrow deliver_work failed (non-fatal): {ee}")

            conn.commit()
            cur.close(); conn.close()
            return {
                "status": "success",
                "message": "Work submitted! Client will review.",
                "escrow_advanced": escrow_delivered,
                "review_deadline": (datetime.now() + timedelta(days=3)).isoformat(),
                "escrow_release": "Payment will be released upon client approval",
            }
        except Exception as e:
            logger.error(f"submit_work failed: {e}")
            return {"status": "error", "message": str(e)}


    def approve_work(self, project_id: str, approval_data: Dict) -> Dict:
        """Client approves work and payment is released."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT project_id, client_id, budget_inr, assigned_intern
                FROM charvak_micro_projects WHERE project_id = %s
            """, (project_id,))
            proj = cur.fetchone()
            if not proj:
                cur.close(); conn.close()
                return {"status": "error", "message": "Project not found"}
            _pid, client_id, budget_inr, assigned_intern = proj
            feedback = approval_data.get("feedback", "")
            rating = approval_data.get("rating", 5)
            cur.execute("""
                UPDATE charvak_micro_projects
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP,
                    feedback = %s, rating = %s
                WHERE project_id = %s
            """, (feedback, rating, project_id))
            cur.execute("""
                UPDATE charvak_micro_applications
                SET status = 'approved', approved_at = CURRENT_TIMESTAMP
                WHERE project_id = %s AND status = 'submitted'
            """, (project_id,))
            if client_id:
                cur.execute("""
                    UPDATE charvak_micro_clients
                    SET total_spend = total_spend + %s,
                        active_projects = GREATEST(active_projects - 1, 0)
                    WHERE client_id = %s
                """, (budget_inr, client_id))
            conn.commit()

            # Release escrow funds if this project has one
            escrow_result = None
            cur.execute("SELECT escrow_id FROM charvak_micro_projects WHERE project_id = %s", (project_id,))
            escrow_row = cur.fetchone()
            if escrow_row and escrow_row[0]:
                try:
                    from escrow_engine import escrow_engine
                    escrow_result = escrow_engine.release_funds(escrow_row[0])
                    if escrow_result.get("status") == "success":
                        logger.info(f"Escrow released for project {project_id}: {escrow_row[0]}")
                        # Fire admin notification email (non-blocking)
                        try:
                            from notification_engine import notification_engine
                            notification_engine.send_email(
                                "hr@charvakit.com",
                                f"Payout pending: Intern for {project_id}",
                                f"""
                                <div style="font-family:Arial,sans-serif;">
                                  <h2 style="color:#3ba591;">Payout pending</h2>
                                  <p><strong>Project:</strong> {project_id}</p>
                                  <p><strong>Escrow:</strong> {escrow_row[0]}</p>
                                  <p><strong>Amount due:</strong> INR {budget_inr}</p>
                                  <p>Please transfer manually via bank/UPI and mark as paid in the admin panel.</p>
                                  <p><a href="https://www.charvakit.com/admin-control">Open Admin Control</a></p>
                                </div>
                                """
                            )
                        except Exception as ne:
                            logger.warning(f"payout notification email failed: {ne}")
                except Exception as ee:
                    logger.warning(f"escrow release failed (non-fatal): {ee}")

            cur.close(); conn.close()
            intern_name = "Unknown"
            if assigned_intern:
                ai = assigned_intern if isinstance(assigned_intern, dict) else json.loads(assigned_intern)
                intern_name = ai.get("name", "Unknown")
            logger.info(f"Project completed: {project_id} | Payment released: {budget_inr}")
            return {
                "status": "success",
                "message": "Project completed! Payment released from escrow.",
                "amount_released": float(budget_inr or 0),
                "intern_name": intern_name,
                "escrow_released": escrow_result.get("status") == "success" if escrow_result else False,
                "payout_status": escrow_result.get("payout_status") if escrow_result else None,
                "conversion_ready": True,
                "next_step": "You can now offer the intern a full-time position",
            }
        except Exception as e:
            logger.error(f"approve_work failed: {e}")
            return {"status": "error", "message": str(e)}


    # ============================================================
    # HELPERS
    # ============================================================
    
    def _find_project(self, project_id: str) -> Optional[Dict]:
        result = self.get_project(project_id)
        return result.get("project") if result.get("status") == "success" else None

    def _find_application(self, application_id: str) -> Optional[Dict]:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT application_id, project_id, candidate_name, candidate_email,
                       skills, portfolio_url, why_interested, status, ai_score,
                       applied_at, assigned_at, submitted_at, approved_at
                FROM charvak_micro_applications WHERE application_id = %s
            """, (application_id,))
            r = cur.fetchone()
            cur.close(); conn.close()
            if not r:
                return None
            return {
                "application_id": r[0], "project_id": r[1],
                "candidate_name": r[2], "candidate_email": r[3],
                "skills": r[4] if isinstance(r[4], list) else json.loads(r[4] or "[]"),
                "portfolio_url": r[5] or "", "why_interested": r[6] or "",
                "status": r[7], "ai_score": r[8] or 0,
                "applied_at": r[9].isoformat() if r[9] else None,
                "assigned_at": r[10].isoformat() if r[10] else None,
                "submitted_at": r[11].isoformat() if r[11] else None,
                "approved_at": r[12].isoformat() if r[12] else None,
            }
        except Exception as e:
            logger.error(f"_find_application failed: {e}")
            return None


    def get_stats(self) -> Dict:
        """Get system statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM charvak_micro_projects")
            total_projects = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_micro_projects WHERE status = 'open'")
            open_projects = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_micro_projects WHERE status = 'completed'")
            completed_projects = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_micro_applications")
            total_applications = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_micro_clients")
            total_clients = cur.fetchone()[0] or 0
            cur.execute("SELECT COALESCE(SUM(budget_inr), 0) FROM charvak_micro_projects")
            total_value = float(cur.fetchone()[0] or 0)
            cur.execute("SELECT COALESCE(SUM(budget_inr), 0) FROM charvak_micro_projects WHERE status = 'completed'")
            total_paid = float(cur.fetchone()[0] or 0)
            cur.close(); conn.close()
            return {
                "status": "success",
                "stats": {
                    "total_projects": total_projects,
                    "open_projects": open_projects,
                    "completed_projects": completed_projects,
                    "total_applications": total_applications,
                    "total_clients": total_clients,
                    "total_value_inr": total_value,
                    "total_paid_inr": total_paid,
                }
            }
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": str(e)}



# ============================================================
# SINGLETON
# ============================================================
micro_internship_engine = MicroInternshipEngine()
