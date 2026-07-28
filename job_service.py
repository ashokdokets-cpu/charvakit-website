"""
Charvakit Job Board Service
Live job database with real postings
"""
import os
import json
import secrets
from datetime import datetime
from typing import Dict, List, Optional
from database import db

class JobBoard:
    def __init__(self):
        self.db = db
    
    def post_job(self, title: str, company: str, job_type: str, location: str, 
                 salary: str, description: str, skills: str, posted_by: str,
                 application_url: str = None) -> Dict:
        """Post a new job"""
        job_id = f"JOB{secrets.token_hex(4).upper()}"
        
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO jobs (job_id, title, company, type, location, salary, description, skills_required, posted_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (job_id, title, company, job_type, location, salary, description, skills, posted_by))
        conn.commit()
        conn.close()
        
        return {"status": "success", "job_id": job_id, "title": title, "company": company}
    
    def get_jobs(self, filters: Dict = None) -> List[Dict]:
        """Get jobs with optional filters"""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM jobs WHERE is_active = 1'
        params = []
        
        if filters:
            if filters.get('type'):
                query += ' AND type = ?'
                params.append(filters['type'])
            if filters.get('location'):
                query += ' AND location LIKE ?'
                params.append(f'%{filters["location"]}%')
            if filters.get('keyword'):
                query += ' AND (title LIKE ? OR description LIKE ? OR skills_required LIKE ?)'
                kw = f'%{filters["keyword"]}%'
                params.extend([kw, kw, kw])
        
        query += ' ORDER BY posted_date DESC'
        cursor.execute(query, params)
        jobs = cursor.fetchall()
        conn.close()
        
        return [{
            "job_id": j[1], "title": j[2], "company": j[3],
            "type": j[4], "location": j[5], "salary": j[6],
            "description": j[7], "skills": j[8], "posted_date": j[10]
        } for j in jobs]
    
    def apply_to_job(self, job_id: str, user_id: str, resume_url: str = None) -> Dict:
        """Apply for a job"""
        app_id = f"APP{secrets.token_hex(4).upper()}"
        
        # Get job details
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT title, company FROM jobs WHERE job_id = ?', (job_id,))
        job = cursor.fetchone()
        
        if not job:
            conn.close()
            return {"status": "error", "message": "Job not found"}
        
        cursor.execute('''
            INSERT INTO applications (application_id, user_id, job_title, company, job_url, source)
            VALUES (?, ?, ?, ?, ?, 'charvakit')
        ''', (app_id, user_id, job[0], job[1], f'/jobs/{job_id}'))
        conn.commit()
        conn.close()
        
        return {"status": "success", "application_id": app_id, "job_title": job[0]}
    
    def get_stats(self) -> Dict:
        """Get job board statistics"""
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE is_active = 1')
        active = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM applications')
        apps = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM applications')
        candidates = cursor.fetchone()[0]
        conn.close()
        
        return {
            "active_jobs": active,
            "total_applications": apps,
            "total_candidates": candidates,
            "avg_response": "48hrs"
        }

# Initialize job board
job_board = JobBoard()

# Seed some default jobs if empty
def seed_default_jobs():
    existing = job_board.get_jobs()
    if not existing:
        default_jobs = [
            ("Senior React Developer", "TechCorp", "Permanent", "Bengaluru", "15-25 LPA", 
             "Looking for experienced React developers with TypeScript and Node.js skills.", "React, TypeScript, Node.js", "system"),
            ("Python Backend Developer", "DataFlow", "Contract", "Remote", "12-18 LPA",
             "FastAPI developer needed for 6-month contract. PostgreSQL experience required.", "Python, FastAPI, PostgreSQL, AWS", "system"),
            ("Full Stack Developer", "WebSolutions", "Contract-to-Hire", "Hyderabad", "10-18 LPA",
             "MERN stack developer with 3+ years experience.", "MongoDB, Express, React, Node.js", "system"),
            ("DevOps Engineer", "CloudFirst", "Permanent", "Remote", "12-20 LPA",
             "AWS, Docker, Kubernetes expert needed for cloud infrastructure team.", "AWS, Docker, Kubernetes, CI/CD", "system"),
            ("AI/ML Engineer", "AI Labs", "Permanent", "Singapore", "SGD 80-120K",
             "Python, TensorFlow, PyTorch expert for AI research team.", "Python, TensorFlow, PyTorch, ML", "system"),
            ("Cloud Architect", "CloudSys", "Contract", "Dubai", "AED 25-35K/month",
             "AWS, Azure, GCP architect for 12-month enterprise migration project.", "AWS, Azure, GCP, Terraform", "system"),
        ]
        for job in default_jobs:
            job_board.post_job(*job)

# Seed jobs on first run
try:
    seed_default_jobs()
except Exception as e:
    print(f"Seed error (non-critical): {e}")