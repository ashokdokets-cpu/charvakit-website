"""
candidate_marketing_engine.py - Candidate-First US Sales Engine
"""
import json
import logging
from database import db
from bench_jd_filter import bench_jd_filter
from openai_compat import build_payload, translate_kwargs
import httpx

logger = logging.getLogger(__name__)

class CandidateMarketingEngine:
    def get_bench_candidates(self):
        """Fetch all active bench candidates."""
        conn = db.get_pooled_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT candidate_id, name, email, location, visa_status, 
                       work_auth_status, skills, experience_years, rate_min, rate_max
                FROM charvak_candidates 
                WHERE status = 'registered' OR status = 'active'
                ORDER BY name
            """)
            rows = cur.fetchall()
            candidates = []
            for r in rows:
                candidates.append({
                    "candidate_id": r[0], "name": r[1], "email": r[2],
                    "location": r[3], "visa_status": r[4] or r[5],
                    "skills": r[6] or [], "experience_years": r[7],
                    "rate_min": float(r[8]) if r[8] else None,
                    "rate_max": float(r[9]) if r[9] else None
                })
            return candidates
        finally:
            cur.close()
            db.release_pooled_connection(conn)

    def get_matched_jobs(self, candidate_id):
        """Reverse Match: Find scraped jobs that fit this candidate."""
        conn = db.get_pooled_connection()
        try:
            cur = conn.cursor()
            
            # Get candidate skills
            cur.execute("SELECT skills, rate_min, rate_max FROM charvak_candidates WHERE candidate_id = %s", (candidate_id,))
            row = cur.fetchone()
            if not row: return []
            cand_skills = row[0] or []
            
            # Fetch recent jobs (limit 500 for performance)
            cur.execute("""
                SELECT job_id, title, company, location, skills, description, source, created_at
                FROM charvak_jobs 
                WHERE (status IS NULL OR LOWER(status) IN ('active', 'open'))
                ORDER BY created_at DESC LIMIT 500
            """)
            jobs = cur.fetchall()
            
            matched_jobs = []
            for j in jobs:
                jd_data = {
                    "role_title": j[1], "title": j[1], "company": j[2],
                    "location": j[3], "skills_required": j[4] or [],
                    "work_auth_required": "Any", "rate_min": None, "rate_max": None,
                    "raw_text": j[5] or "", "source": j[6]
                }
                
                # We only care if the overlap is good
                is_relevant, reason, best_cand, _, overlap = bench_jd_filter.is_relevant(jd_data)
                if is_relevant and overlap >= 0.30:
                    matched_jobs.append({
                        "job_id": j[0], "title": j[1], "company": j[2],
                        "location": j[3], "source": j[6],
                        "overlap_pct": round(overlap * 100, 1),
                        "posted_at": j[7].isoformat() if j[7] else None
                    })
            
            # Sort by highest overlap
            matched_jobs.sort(key=lambda x: x["overlap_pct"], reverse=True)
            return matched_jobs[:10] # Return top 10
        finally:
            cur.close()
            db.release_pooled_connection(conn)

    def generate_marketing_blurb(self, candidate_id):
        """Use AI to generate a vendor-ready summary for the candidate."""
        conn = db.get_pooled_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT name, skills, experience_years, location, visa_status, work_auth_status, rate_min, rate_max
                FROM charvak_candidates WHERE candidate_id = %s
            """, (candidate_id,))
            row = cur.fetchone()
            if not row: return "Candidate not found."
            
            name, skills, exp, loc, visa, auth, r_min, r_max = row
            visa_info = visa or auth or "Work Auth Unknown"
            rate_info = f"${r_min}-${r_max}/hr" if r_min and r_max else "Rate Negotiable"
            
            prompt = f"""
            Write a highly professional, 3-sentence summary for a US IT staffing vendor.
            Candidate: {name}
            Experience: {exp} years
            Location: {loc}
            Work Authorization: {visa_info}
            Rate: {rate_info}
            Key Skills: {", ".join(skills) if isinstance(skills, list) else skills}
            
            Focus on their strongest technical skills and their availability. Do not use fluff words. Be direct.
            """
            
            payload = build_payload(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "AI Blurb unavailable: Missing OPENAI_API_KEY."

            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json=payload
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        finally:
            cur.close()
            db.release_pooled_connection(conn)

candidate_marketing_engine = CandidateMarketingEngine()