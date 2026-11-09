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
        self.api_key = os.getenv("TECHMAP_API_KEY", "")
        self.base_url = "https://daily-international-job-postings.p.rapidapi.com/api/v2/jobs/search"
        
        # Strict list of Indian cities/states to double-check results
        self.india_keywords = [
            "india", "bangalore", "bengaluru", "mumbai", "delhi", "new delhi", 
            "hyderabad", "chennai", "kolkata", "pune", "ahmedabad", "jaipur", 
            "surat", "lucknow", "kanpur", "nagpur", "indore", "thane", 
            "bhopal", "visakhapatnam", "patna", "vadodara", "guntur", "vijayawada",
            "telangana", "andhra pradesh", "karnataka", "maharashtra", "tamil nadu"
        ]

    def fetch_india_jobs(self, limit=50):
        """Fetch real Indian jobs from a legal API."""
        if not self.api_key:
            logger.warning("[india_radar] No TECHMAP_API_KEY set. Cannot fetch jobs.")
            return []

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "daily-international-job-postings.p.rapidapi.com"
        }
        
        # We request NCS data and India location
        # Let the API use its default date (most recent complete day).
        # Naukri is the largest Indian source on Techmap.
        params = {
            "portal": "naukri",
            "countryCode": "in",
            "limit": limit
        }

        try:
            resp = requests.get(self.base_url, headers=headers, params=params, timeout=30)
            if resp.status_code != 200:
                logger.error(f"[india_radar] API Error {resp.status_code}: {resp.text}")
                return []
                
            data = resp.json()
            jobs = data.get("data", []) or data.get("jobs", [])
            logger.info(f"[india_radar] Fetched {len(jobs)} raw jobs from API.")
            return jobs
        except Exception as e:
            logger.error(f"[india_radar] API fetch failed: {e}")
            return []

    def _is_truly_india(self, job):
        """Safety filter to ensure no US/EU jobs slip through."""
        loc = str(job.get("location", "")).lower()
        title = str(job.get("title", "")).lower()
        desc = str(job.get("description", "")).lower()
        combined = f"{loc} {title} {desc}"
        
        # If it contains any Indian keyword, it's valid
        if any(kw in combined for kw in self.india_keywords):
            return True
            
        # If it contains these explicit non-India keywords, reject it
        if any(kw in loc for kw in ["usa", "united states", "uk", "canada", "europe", "germany"]):
            return False
            
        return False

    def run_radar(self):
        """Fetch, Match, and Alert."""
        logger.info("[india_radar] Starting India Radar scan...")
        raw_jobs = self.fetch_india_jobs(limit=50)
        
        if not raw_jobs:
            return {"status": "empty", "matched": 0, "message": "No jobs fetched from API."}

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
                return {"status": "no_candidates", "matched": 0, "message": "No Indian candidates found in DB."}

            for job in raw_jobs:
                # 1. SAFETY FILTER: Ensure it's actually India
                if not self._is_truly_india(job):
                    continue

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
                
                # 2. Match using existing filter
                is_relevant, reason, best_cand, best_email, overlap = bench_jd_filter.is_relevant(jd_data)
                
                if is_relevant and overlap >= 0.20: # 20% threshold for Indian market
                    matched_count += 1
                    
                    cur.execute("""
                        INSERT INTO charvak_radar_alerts 
                        (job_title, company, location, salary, matched_candidate, candidate_email, overlap_pct, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending_alert')
                    """, (job_title, job_company, job_loc, job_salary, best_cand, best_email, round(overlap*100, 1)))
            
            conn.commit()
            return {"status": "success", "matched": matched_count, "raw_fetched": len(raw_jobs)}
            
        except Exception as e:
            logger.error(f"[india_radar] run_radar failed: {e}")
            conn.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            cur.close()
            db.release_pooled_connection(conn)

india_radar_engine = IndiaRadarEngine()