"""
Candidate profile engine (Session 22c / Patch 3a)

Owns the charvak_candidates row lifecycle for the staffing pipeline.
Called from:
  POST /api/candidates/upsert
  GET  /api/candidates/me
"""
import logging
import secrets
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger("charvakit.candidates_engine")


# Fields we accept from the client. Anything else is ignored.
ALLOWED_FIELDS = [
    "name", "phone", "location", "job_title",
    "current_company", "current_salary_inr", "current_salary_currency",
    "experience_years", "relevant_experience_years",
    "notice_period", "expected_hike_percent",
    "variable_component", "other_benefits",
    "skills", "education", "degree", "university", "graduation_year",
    "resume_text", "additional_email", "additional_phone",
    "candidate_summary", "country",
]


class CandidatesEngine:
    def __init__(self):
        pass

    # ----------------------------------------------------------------
    # Read
    # ----------------------------------------------------------------

    def get_me(self, email: str) -> Dict:
        """Fetch the caller's candidate row."""
        email = (email or "").strip().lower()
        if not email:
            return {"status": "error", "message": "email required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT candidate_id, name, email, phone, location, job_title,
                       current_company, current_salary_inr, current_salary_currency,
                       experience_years, relevant_experience_years, notice_period,
                       skills, education, degree, university, graduation_year,
                       resume_text, additional_email, additional_phone,
                       candidate_summary, country, status, registered_at, updated_at
                FROM charvak_candidates
                WHERE email = %s
            """, (email,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_me failed: {e}")
            return {"status": "error", "message": f"Fetch failed: {e}"}

        if not row:
            return {"status": "not_found", "message": "No candidate profile yet"}

        return {
            "status": "success",
            "candidate": {
                "candidate_id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "location": row[4],
                "job_title": row[5],
                "current_company": row[6],
                "current_salary_inr": float(row[7]) if row[7] is not None else None,
                "current_salary_currency": row[8],
                "experience_years": row[9],
                "relevant_experience_years": row[10],
                "notice_period": row[11],
                "skills": row[12],
                "education": row[13],
                "degree": row[14],
                "university": row[15],
                "graduation_year": row[16],
                "resume_text": row[17],
                "additional_email": row[18],
                "additional_phone": row[19],
                "candidate_summary": row[20],
                "country": row[21],
                "status": row[22],
                "created_at": row[23].isoformat() if row[23] else None,
                "updated_at": row[24].isoformat() if row[24] else None,
            },
        }

    # ----------------------------------------------------------------
    # Upsert
    # ----------------------------------------------------------------

    def upsert(self, data: Dict) -> Dict:
        """
        Create or update the candidate row for data['email'].
        Only non-empty fields in ALLOWED_FIELDS are written.
        """
        email = (data.get("email") or "").strip().lower()
        if not email:
            return {"status": "error", "message": "email required"}

        # Normalize experience_years from alternate key names if present
        if "experience_years" not in data and "experience" in data:
            try:
                data["experience_years"] = int(data["experience"])
            except (TypeError, ValueError):
                pass

        # Only allow known fields
        payload = {k: data.get(k) for k in ALLOWED_FIELDS if data.get(k) not in (None, "")}

        if not payload:
            return {"status": "error", "message": "No fields to save"}

        # Fields stored as JSONB in Postgres -- coerce comma-separated strings to arrays
        JSONB_LIST_FIELDS = ("skills", "certifications", "languages_spoken", "preferred_roles")
        import json as _json
        for f in JSONB_LIST_FIELDS:
            if f in payload:
                v = payload[f]
                if isinstance(v, list):
                    payload[f] = _json.dumps(v)
                elif isinstance(v, str):
                    items = [s.strip() for s in v.split(",") if s.strip()]
                    payload[f] = _json.dumps(items)
                else:
                    payload[f] = _json.dumps([])

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Does the row exist?
            cur.execute("SELECT candidate_id FROM charvak_candidates WHERE email = %s", (email,))
            existing = cur.fetchone()

            if existing:
                candidate_id = existing[0]
                # Build a safe UPDATE with only provided fields
                set_parts = []
                params = []
                for k, v in payload.items():
                    set_parts.append(f"{k} = %s")
                    params.append(v)
                set_parts.append("updated_at = CURRENT_TIMESTAMP")
                params.append(candidate_id)
                sql = f"UPDATE charvak_candidates SET {', '.join(set_parts)} WHERE candidate_id = %s"
                cur.execute(sql, tuple(params))
                action = "updated"
            else:
                candidate_id = "CAND-" + secrets.token_hex(4).upper()
                cols = ["candidate_id", "email"] + list(payload.keys())
                vals = [candidate_id, email] + list(payload.values())
                placeholders = ", ".join(["%s"] * len(cols))
                sql = f"INSERT INTO charvak_candidates ({', '.join(cols)}) VALUES ({placeholders})"
                cur.execute(sql, tuple(vals))
                action = "created"

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"upsert failed: {e}")
            return {"status": "error", "message": f"Save failed: {e}"}

        return {
            "status": "success",
            "candidate_id": candidate_id,
            "action": action,
        }


candidates_engine = CandidatesEngine()
