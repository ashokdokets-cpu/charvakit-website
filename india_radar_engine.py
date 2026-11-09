"""
india_radar_engine.py - India Market Requirement Radar
"""
import os
import logging
import requests
from database import db
from bench_jd_filter import bench_jd_filter

logger = logging.getLogger(__name__)

class IndiaRadarEngine:
    def __init__(self):
        # Using Techmap API as a legal aggregator for NCS and Indian job boards
        self.api_key = os.getenv("TECHMAP_API_KEY", "")
        self.base_url = "https://daily-international-job-postings.p.rapidapi.com/api/v2/jobs/search"

    def fetch_india_jobs(self, limit=50):
        """Fetch real Indian jobs from a legal API."""
        if not self.api_key:
            logger.warning("[india_radar] No TECHMAP_API_KEY set. Using demo mode.")
            # DEMO MODE: Return fake data if no API key is set, so you can test the UI
            return [
                {"title": "Junior Accountant", "company": "Guntur Textiles", "location": "Guntur, AP", "salary": "15k-20k", "skills": ["Tally", "Excel"], "description": "Need immediate joiner."},
                {"title": "React Developer", "company": "Tech Mahindra", "location": "Hyderabad, TS", "salary": "4L-6L", "skills": ["React", "JavaScript", "HTML"], "description": "Looking for 2 years exp."},
                {"title": "Data Entry Operator", "company": "AP Govt", "location": "Vijayawada, AP", "salary": "12k", "skills": ["Typing", "MS Office"], "description": "Contractual role."}
            ]

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "daily-international-job-postings.p.rapidapi.com"
        }
        params = {"portal": "ncs", "countryCode": "in", "limit": limit}

        try:
            resp = requests.get(self.base_url, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json().get("data", []) or resp.json().get("jobs", [])
        except Exception as e:
            logger.error(f"[india_radar] API fetch failed: {e}")
            return []

    def run_radar(self):
        """Fetch, Match, and Alert."""
        logger.info("[india_radar] Starting India Radar scan...")
        raw_jobs = self.fetch_india_jobs(limit=20)
        
        if not raw_jobs:
            return {"status": "empty", "matched": 0}

        conn = db.get_pooled_connection()
        if not conn: return {"status": "error", "message": "DB unavailable"}
            
        matched_count = 0
        try:
            cur = conn.cursor()
            # Get Indian candidates (we assume they have 'India' in location)
            cur.execute("""
                SELECT candidate_id, name, email, skills, location
                FROM charvak_candidates 
                WHERE location ILIKE '%India%' OR location ILIKE '%Bangalore%' 
                   OR location ILIKE '%Mumbai%' OR location ILIKE '%Hyderabad%'
                   OR location ILIKE '%Guntur%' OR location ILIKE '%Chennai%'
                   OR location ILIKE '%Pune%' OR location ILIKE '%Delhi%'
                LIMIT 100
            """)
            candidates = cur.fetchall()
            
            if not candidates:
                return {"status": "no_candidates", "matched": 0}

            for job in raw_jobs:
                job_title = job.get("title", "")
                job_company = job.get("company", "")
                job_loc = job.get("location", "")
                job_salary = job.get("salary", "")
                job_skills = job.get("skills", [])
                job_desc = job.get("description", "")

                jd_data = {
                    "role_title": job_title, "title": job_title, "company": job_company,
                    "location": job_loc, "skills_required": job_skills,
                    "work_auth_required": "Any", "rate_min": None, "rate_max": None,
                    "raw_text": job_desc, "source": "ncs"
                }
                
                is_relevant, reason, best_cand, best_email, overlap = bench_jd_filter.is_relevant(jd_data)
                
                if is_relevant and overlap >= 0.20: # 20% threshold for Indian market
                    matched_count += 1
                    
                    # Insert alert with UNLOCKED status to start (candidates see it, but must pay to get the email)
                    cur.execute("""
                        INSERT INTO charvak_radar_alerts 
                        (job_title, company, location, salary, matched_candidate, candidate_email, overlap_pct, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending_alert')
                    """, (job_title, job_company, job_loc, job_salary, best_cand, best_email, round(overlap*100, 1)))
            
            conn.commit()
            return {"status": "success", "matched": matched_count}
            
        except Exception as e:
            logger.error(f"[india_radar] run_radar failed: {e}")
            conn.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            db.release_pooled_connection(conn)

india_radar_engine = IndiaRadarEngine()