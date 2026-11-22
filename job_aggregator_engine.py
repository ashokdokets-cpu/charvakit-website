"""
Multi-Source Job Aggregator - Session 120
Pulls jobs from Adzuna and future sources.
"""
import os
import json
import logging
import requests
import psycopg2
from database import db

logger = logging.getLogger("charvakit.job_aggregator")


class AdzunaClient:
    """Free Adzuna API — India coverage."""
    
    BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    
    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID", "")
        self.app_key = os.getenv("ADZUNA_APP_KEY", "")
    
    def is_configured(self) -> bool:
        return bool(self.app_id and self.app_key)
    
    def fetch_jobs(self, keyword: str = "software engineer", limit: int = 50) -> list:
        if not self.is_configured():
            logger.warning("[adzuna] Not configured — missing ADZUNA_APP_ID or ADZUNA_APP_KEY")
            return []
        
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": min(limit, 50),
            "what": keyword,
            "content-type": "application/json"
        }
        
        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=30)
            if resp.status_code != 200:
                logger.error(f"[adzuna] API error {resp.status_code}: {resp.text[:200]}")
                return []
            
            data = resp.json()
            return data.get("results", [])
        except Exception as e:
            logger.error(f"[adzuna] Fetch failed: {e}")
            return []


class JobAggregatorEngine:
    def __init__(self):
        self.adzuna = AdzunaClient()
    
    def sync_adzuna(self, keyword: str = "software engineer", limit: int = 50) -> dict:
        """Fetch jobs from Adzuna and insert into charvak_jobs."""
        if not self.adzuna.is_configured():
            return {"status": "error", "message": "Adzuna not configured"}
        
        raw_jobs = self.adzuna.fetch_jobs(keyword=keyword, limit=limit)
        if not raw_jobs:
            return {"status": "error", "message": "No jobs fetched from Adzuna"}
        
        conn = db.get_connection()
        cur = conn.cursor()
        inserted = 0
        skipped = 0
        
        try:
            for job in raw_jobs:
                external_id = str(job.get("id", ""))
                job_id = f"JOB-ADZUNA-{external_id[:12]}"
                title = (job.get("title") or "").strip()
                company = (job.get("company", {}).get("display_name") or "").strip()
                location = (job.get("location", {}).get("display_name") or "India").strip()
                description = (job.get("description") or "")[:5000]
                posted = job.get("created", "")
                salary_min = job.get("salary_min")
                salary_max = job.get("salary_max")
                
                if not title or not company:
                    skipped += 1
                    continue
                
                if salary_min and salary_max:
                    salary = f"Rs {int(salary_min):,} - Rs {int(salary_max):,}"
                elif salary_min:
                    salary = f"Rs {int(salary_min):,}+"
                else:
                    salary = None
                
                try:
                    cur.execute("""
                        INSERT INTO charvak_jobs 
                        (job_id, title, company, location, description, salary, status, source, posted_date, raw_json)
                        VALUES (%s, %s, %s, %s, %s, %s, 'active', 'adzuna', %s, %s)
                        ON CONFLICT (job_id) DO NOTHING
                    """, (job_id, title, company, location, description, salary, posted, json.dumps(job)))
                    if cur.rowcount > 0:
                        inserted += 1
                    else:
                        skipped += 1
                except Exception as e:
                    logger.error(f"[adzuna] Insert failed for {title[:40]}: {e}")
                    skipped += 1
            
            conn.commit()
        finally:
            cur.close()
            conn.close()
        
        return {
            "status": "success",
            "source": "adzuna",
            "fetched": len(raw_jobs),
            "inserted": inserted,
            "skipped": skipped
        }
    
    def get_stats(self) -> dict:
        """Report job counts by source."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT source, COUNT(*) 
                FROM charvak_jobs 
                WHERE status = 'active'
                GROUP BY source
                ORDER BY COUNT(*) DESC
            """)
            return {row[0] or "unknown": row[1] for row in cur.fetchall()}
        finally:
            cur.close()
            conn.close()


job_aggregator = JobAggregatorEngine()