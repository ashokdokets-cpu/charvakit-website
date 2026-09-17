"""
Charvak Candidate Pool Engine
Centralized candidate registry with skill indexing
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets
import json

logger = logging.getLogger("charvakit.candidates")


class CandidateStatus:
    REGISTERED = "registered"
    SKILL_CHECKED = "skill_checked"
    BADGE_EARNED = "badge_earned"
    INTERNSHIP_DONE = "internship_done"
    PLACED = "placed"
    REJECTED = "rejected"


class CandidateEngine:
    """Central candidate pool."""
    
    def __init__(self):
        self._ensure_tables()
        logger.info("Candidate Engine ready (DB-backed)")

    def _ensure_tables(self):
        """Idempotent table creation for candidate tables."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_candidates (
                    candidate_id        TEXT PRIMARY KEY,
                    name                TEXT NOT NULL,
                    email               TEXT NOT NULL UNIQUE,
                    phone               TEXT DEFAULT '',
                    skills              JSONB DEFAULT '[]'::jsonb,
                    experience_years    INTEGER DEFAULT 0,
                    years_coding        INTEGER,
                    job_title           TEXT DEFAULT '',
                    preferred_roles     JSONB DEFAULT '[]'::jsonb,
                    location            TEXT DEFAULT '',
                    visa_status         TEXT DEFAULT '',
                    portfolio_url       TEXT DEFAULT '',
                    github_url          TEXT DEFAULT '',
                    linkedin_url        TEXT DEFAULT '',
                    resume_text         TEXT DEFAULT '',
                    education           TEXT DEFAULT '',
                    degree              TEXT DEFAULT '',
                    major               TEXT DEFAULT '',
                    university          TEXT DEFAULT '',
                    gpa                 NUMERIC(4,2),
                    graduation_year     INTEGER,
                    certifications      JSONB DEFAULT '[]'::jsonb,
                    languages_spoken    JSONB DEFAULT '[]'::jsonb,
                    work_authorization  TEXT DEFAULT '',
                    willing_to_relocate BOOLEAN DEFAULT FALSE,
                    remote_preference   TEXT DEFAULT 'Open',
                    salary_expectation  TEXT DEFAULT '',
                    availability        TEXT DEFAULT 'Immediate',
                    status              TEXT DEFAULT 'registered',
                    skill_score         INTEGER,
                    badge_id            TEXT,
                    placement           JSONB,
                    registered_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute("CREATE INDEX IF NOT EXISTS idx_candidates_email ON charvak_candidates(email)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_candidates_status ON charvak_candidates(status)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_candidates_location ON charvak_candidates(location)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_candidates_experience ON charvak_candidates(experience_years)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_candidates_skill_score ON charvak_candidates(skill_score)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_candidates_visa ON charvak_candidates(visa_status)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_candidates_university ON charvak_candidates(university)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_candidates_grad_year ON charvak_candidates(graduation_year)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_candidates_skills_gin ON charvak_candidates USING GIN (skills)")
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"candidate tables init failed: {e}")

    def _row_to_candidate(self, r):
        """Convert a row tuple from charvak_candidates to the dict shape."""
        if not r:
            return None
        return {
            "candidate_id": r[0], "name": r[1], "email": r[2], "phone": r[3],
            "skills": r[4] if isinstance(r[4], list) else json.loads(r[4] or "[]"),
            "experience_years": r[5] or 0,
            "years_coding": r[6],
            "current_role": r[7] or "",  # column is job_title; key is current_role for compat
            "preferred_roles": r[8] if isinstance(r[8], list) else json.loads(r[8] or "[]"),
            "location": r[9] or "", "visa_status": r[10] or "",
            "portfolio_url": r[11] or "", "github_url": r[12] or "",
            "linkedin_url": r[13] or "", "resume_text": r[14] or "",
            "education": r[15] or "", "degree": r[16] or "",
            "major": r[17] or "", "university": r[18] or "",
            "gpa": float(r[19]) if r[19] else None,
            "graduation_year": r[20],
            "certifications": r[21] if isinstance(r[21], list) else json.loads(r[21] or "[]"),
            "languages_spoken": r[22] if isinstance(r[22], list) else json.loads(r[22] or "[]"),
            "work_authorization": r[23] or "",
            "willing_to_relocate": bool(r[24]) if r[24] is not None else False,
            "remote_preference": r[25] or "Open",
            "salary_expectation": r[26] or "",
            "availability": r[27] or "Immediate",
            "status": r[28] or "registered",
            "skill_score": r[29], "badge_id": r[30],
            "placement": r[31] if isinstance(r[31], dict) else (json.loads(r[31]) if r[31] else None),
            "registered_at": r[32].isoformat() if r[32] else None,
            "updated_at": r[33].isoformat() if r[33] else None,
        }


    def register_candidate(self, data: Dict) -> Dict:
        """Register a new candidate."""
        candidate_id = f"CAND-{secrets.token_hex(4).upper()}"
        gpa = float(data.get("gpa", 0)) if data.get("gpa") else None
        grad_year = int(data.get("graduation_year", 0)) if data.get("graduation_year") else None
        years_coding = int(data.get("years_coding", 0)) if data.get("years_coding") else None
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_candidates
                    (candidate_id, name, email, phone, skills, experience_years,
                     years_coding, job_title, preferred_roles, location, visa_status,
                     portfolio_url, github_url, linkedin_url, resume_text,
                     education, degree, major, university, gpa, graduation_year,
                     certifications, languages_spoken, work_authorization,
                     willing_to_relocate, remote_preference, salary_expectation,
                     availability, status)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s::jsonb,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s, 'registered')
            ''', (candidate_id, data.get("name"), data.get("email"),
                  data.get("phone", ""),
                  json.dumps(data.get("skills", [])),
                  int(data.get("experience_years", 0)),
                  years_coding, data.get("current_role", ""),
                  json.dumps(data.get("preferred_roles", [])),
                  data.get("location", ""), data.get("visa_status", ""),
                  data.get("portfolio_url", ""), data.get("github_url", ""),
                  data.get("linkedin_url", ""), data.get("resume_text", ""),
                  data.get("education", ""), data.get("degree", ""),
                  data.get("major", ""), data.get("university", ""),
                  gpa, grad_year,
                  json.dumps(data.get("certifications", [])),
                  json.dumps(data.get("languages_spoken", [])),
                  data.get("work_authorization", ""),
                  bool(data.get("willing_to_relocate", False)),
                  data.get("remote_preference", "Open"),
                  data.get("salary_expectation", ""),
                  data.get("availability", "Immediate")))
            conn.commit()
            cur.close(); conn.close()
            return {"status": "success", "candidate_id": candidate_id, "message": "Welcome to Charvak!"}
        except Exception as e:
            err_str = str(e).lower()
            if "duplicate" in err_str or "unique constraint" in err_str:
                logger.info(f"Duplicate candidate registration attempted: {data.get('email')}")
                return {"status": "error", "message": "This email is already registered. Please log in or use a different email.", "code": "duplicate_email"}
            logger.error(f"register_candidate failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_candidate(self, candidate_id: str) -> Dict:
        """Get candidate by ID."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT candidate_id, name, email, phone, skills, experience_years,
                       years_coding, job_title, preferred_roles, location, visa_status,
                       portfolio_url, github_url, linkedin_url, resume_text,
                       education, degree, major, university, gpa, graduation_year,
                       certifications, languages_spoken, work_authorization,
                       willing_to_relocate, remote_preference, salary_expectation,
                       availability, status, skill_score, badge_id, placement,
                       registered_at, updated_at
                FROM charvak_candidates WHERE candidate_id = %s
            ''', (candidate_id,))
            r = cur.fetchone()
            cur.close(); conn.close()
            if not r:
                return {"status": "error", "message": "Candidate not found"}
            return {"status": "success", "candidate": self._row_to_candidate(r)}
        except Exception as e:
            logger.error(f"get_candidate failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_candidate_by_email(self, email: str) -> Optional[Dict]:
        """Get candidate by email."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT candidate_id, name, email, phone, skills, experience_years,
                       years_coding, job_title, preferred_roles, location, visa_status,
                       portfolio_url, github_url, linkedin_url, resume_text,
                       education, degree, major, university, gpa, graduation_year,
                       certifications, languages_spoken, work_authorization,
                       willing_to_relocate, remote_preference, salary_expectation,
                       availability, status, skill_score, badge_id, placement,
                       registered_at, updated_at
                FROM charvak_candidates WHERE email = %s
            ''', (email,))
            r = cur.fetchone()
            cur.close(); conn.close()
            return self._row_to_candidate(r) if r else None
        except Exception as e:
            logger.error(f"get_candidate_by_email failed: {e}")
            return None


    def update_skill_score(self, candidate_id: str, score: int, badge_id: str = None) -> Dict:
        """Update candidate's skill score after assessment."""
        new_status = "badge_earned" if score >= 70 else "skill_checked"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_candidates
                SET skill_score = %s,
                    badge_id = %s,
                    status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE candidate_id = %s
                RETURNING candidate_id
            ''', (score, badge_id, new_status, candidate_id))
            row = cur.fetchone()
            conn.commit()
            cur.close(); conn.close()
            if not row:
                return {"status": "error", "message": "Candidate not found"}
            return {
                "status": "success",
                "candidate_id": candidate_id,
                "skill_score": score,
                "badge_earned": score >= 70,
                "message": "Skill score updated!"
            }
        except Exception as e:
            logger.error(f"update_skill_score failed: {e}")
            return {"status": "error", "message": str(e)}


    def search_candidates(self, filters: Dict = None) -> Dict:
        """Advanced search with filter combinations (18 supported filters)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            where = []
            params = []
            filters = filters or {}

            if filters.get("skill"):
                # JSONB skills contains string (case-insensitive substring)
                where.append("skills::text ILIKE %s")
                params.append("%" + filters["skill"].lower() + "%")
            if filters.get("experience_min"):
                where.append("experience_years >= %s")
                params.append(int(filters["experience_min"]))
            if filters.get("experience_max"):
                where.append("experience_years <= %s")
                params.append(int(filters["experience_max"]))
            if filters.get("location"):
                where.append("location ILIKE %s")
                params.append("%" + filters["location"].lower() + "%")
            if filters.get("visa_status"):
                where.append("visa_status ILIKE %s")
                params.append("%" + filters["visa_status"].lower() + "%")
            if filters.get("skill_score_min"):
                where.append("skill_score IS NOT NULL AND skill_score >= %s")
                params.append(int(filters["skill_score_min"]))
            if filters.get("education"):
                where.append("education ILIKE %s")
                params.append("%" + filters["education"].lower() + "%")
            if filters.get("degree"):
                where.append("degree ILIKE %s")
                params.append("%" + filters["degree"].lower() + "%")
            if filters.get("major"):
                where.append("major ILIKE %s")
                params.append("%" + filters["major"].lower() + "%")
            if filters.get("university"):
                where.append("university ILIKE %s")
                params.append("%" + filters["university"].lower() + "%")
            if filters.get("gpa_min"):
                where.append("gpa IS NOT NULL AND gpa >= %s")
                params.append(float(filters["gpa_min"]))
            if filters.get("graduation_year_min"):
                where.append("graduation_year IS NOT NULL AND graduation_year >= %s")
                params.append(int(filters["graduation_year_min"]))
            if filters.get("certification"):
                where.append("certifications::text ILIKE %s")
                params.append("%" + filters["certification"].lower() + "%")
            if filters.get("language"):
                where.append("languages_spoken::text ILIKE %s")
                params.append("%" + filters["language"].lower() + "%")
            if filters.get("work_authorization"):
                where.append("work_authorization ILIKE %s")
                params.append("%" + filters["work_authorization"].lower() + "%")
            if filters.get("remote_preference"):
                where.append("remote_preference ILIKE %s")
                params.append("%" + filters["remote_preference"].lower() + "%")
            if filters.get("availability"):
                where.append("availability ILIKE %s")
                params.append("%" + filters["availability"].lower() + "%")
            if filters.get("years_coding_min"):
                where.append("years_coding IS NOT NULL AND years_coding >= %s")
                params.append(int(filters["years_coding_min"]))

            sql = '''
                SELECT candidate_id, name, email, phone, skills, experience_years,
                       years_coding, job_title, preferred_roles, location, visa_status,
                       portfolio_url, github_url, linkedin_url, resume_text,
                       education, degree, major, university, gpa, graduation_year,
                       certifications, languages_spoken, work_authorization,
                       willing_to_relocate, remote_preference, salary_expectation,
                       availability, status, skill_score, badge_id, placement,
                       registered_at, updated_at
                FROM charvak_candidates
            '''
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY registered_at DESC"

            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            cur.close(); conn.close()
            results = [self._row_to_candidate(r) for r in rows]
            return {"status": "success", "candidates": results, "count": len(results)}
        except Exception as e:
            logger.error(f"search_candidates failed: {e}")
            return {"status": "error", "message": str(e), "candidates": [], "count": 0}


    def mark_placed(self, candidate_id: str, placement_data: Dict = None) -> Dict:
        """Mark candidate as placed."""
        placement_data = placement_data or {}
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_candidates
                SET status = 'placed',
                    placement = %s::jsonb,
                    updated_at = CURRENT_TIMESTAMP
                WHERE candidate_id = %s
                RETURNING name
            ''', (json.dumps(placement_data), candidate_id))
            row = cur.fetchone()
            conn.commit()
            cur.close(); conn.close()
            if not row:
                return {"status": "error", "message": "Candidate not found"}
            return {"status": "success", "message": f"{row[0]} marked as placed!"}
        except Exception as e:
            logger.error(f"mark_placed failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_pool_stats(self) -> Dict:
        """Get candidate pool statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM charvak_candidates")
            total = cur.fetchone()[0] or 0
            cur.execute('''
                SELECT COUNT(*) FROM charvak_candidates
                WHERE status IN ('badge_earned','internship_done','placed')
            ''')
            verified = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_candidates WHERE status = 'placed'")
            placed = cur.fetchone()[0] or 0
            cur.execute('''
                SELECT COALESCE(AVG(experience_years), 0) FROM charvak_candidates
            ''')
            avg_exp = float(cur.fetchone()[0] or 0)
            cur.execute("SELECT COUNT(DISTINCT location) FROM charvak_candidates WHERE location <> ''")
            locations = cur.fetchone()[0] or 0
            # Unique skills across all candidates via JSONB
            cur.execute('''
                SELECT COUNT(DISTINCT s) FROM (
                    SELECT jsonb_array_elements_text(skills) AS s FROM charvak_candidates
                ) sub
            ''')
            unique_skills = cur.fetchone()[0] or 0
            cur.close(); conn.close()
            return {
                "status": "success",
                "stats": {
                    "total_candidates": total,
                    "verified_candidates": verified,
                    "placed_candidates": placed,
                    "unique_skills": unique_skills,
                    "avg_experience_years": round(avg_exp, 1),
                    "locations": locations,
                },
            }
        except Exception as e:
            logger.error(f"get_pool_stats failed: {e}")
            return {"status": "error", "message": str(e)}


    def _find(self, candidate_id: str) -> Optional[Dict]:
        """Internal helper: return candidate dict or None."""
        result = self.get_candidate(candidate_id)
        if result.get("status") == "success":
            return result.get("candidate")
        return None



candidate_engine = CandidateEngine()