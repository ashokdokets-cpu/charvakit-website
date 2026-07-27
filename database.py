"""
Charvakit Database Module
PostgreSQL database connection, models, and CRUD operations
"""
import os
import hashlib
import secrets
from datetime import datetime
from typing import Optional, List, Dict

# Using SQLite for development (easy setup), PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///charvakit.db")

# For production PostgreSQL:
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@host:5432/charvakit")

# --- Simple Database Class (SQLite) ---
import sqlite3
import json

class Database:
    def __init__(self, db_path="charvakit.db"):
        self.db_path = db_path
        self.init_db()
    
    def connect(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Create all tables"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                role TEXT DEFAULT 'candidate',
                doketsrb_id TEXT,
                resume_data TEXT,
                skills TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                job_url TEXT,
                status TEXT DEFAULT 'applied',
                applied_date DATE DEFAULT CURRENT_DATE,
                source TEXT DEFAULT 'charvakit',
                notes TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                type TEXT,
                location TEXT,
                salary TEXT,
                description TEXT,
                skills_required TEXT,
                posted_by TEXT,
                posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Skill gaps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skill_gaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                skill TEXT NOT NULL,
                current_level INTEGER,
                required_level INTEGER,
                recommended_course TEXT,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Courses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                trainer TEXT,
                category TEXT,
                duration TEXT,
                price REAL,
                provider TEXT DEFAULT 'charvakit',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Contact messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                subject TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # --- User Operations ---
    def create_user(self, email: str, password: str, name: str, role: str = "candidate", phone: str = None) -> Dict:
        conn = self.connect()
        cursor = conn.cursor()
        user_id = f"USR{secrets.token_hex(4).upper()}"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute('''
                INSERT INTO users (user_id, email, password_hash, name, phone, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, email, password_hash, name, phone, role))
            conn.commit()
            return {"status": "success", "user_id": user_id, "email": email, "name": name}
        except sqlite3.IntegrityError:
            return {"status": "error", "message": "Email already registered"}
        finally:
            conn.close()
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        conn = self.connect()
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('SELECT * FROM users WHERE email = ? AND password_hash = ?', (email, password_hash))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "user_id": user[1], "email": user[2], "name": user[4],
                "phone": user[5], "role": user[6], "doketsrb_id": user[7]
            }
        return None
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return {"user_id": user[1], "email": user[2], "name": user[4], "role": user[6]}
        return None
    
    # --- Application Operations ---
    def add_application(self, user_id: str, job_title: str, company: str, job_url: str = None, source: str = "charvakit") -> Dict:
        conn = self.connect()
        cursor = conn.cursor()
        app_id = f"APP{secrets.token_hex(4).upper()}"
        
        cursor.execute('''
            INSERT INTO applications (application_id, user_id, job_title, company, job_url, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (app_id, user_id, job_title, company, job_url, source))
        conn.commit()
        conn.close()
        return {"status": "success", "application_id": app_id}
    
    def get_user_applications(self, user_id: str) -> List[Dict]:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM applications WHERE user_id = ? ORDER BY last_updated DESC', (user_id,))
        apps = cursor.fetchall()
        conn.close()
        return [{"application_id": a[1], "job_title": a[3], "company": a[4], "status": a[6], "applied_date": a[7], "source": a[8]} for a in apps]
    
    def update_application_status(self, app_id: str, status: str) -> Dict:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('UPDATE applications SET status = ?, last_updated = CURRENT_TIMESTAMP WHERE application_id = ?', (status, app_id))
        conn.commit()
        conn.close()
        return {"status": "success", "application_id": app_id, "new_status": status}
    
    # --- Job Operations ---
    def post_job(self, title: str, company: str, job_type: str, location: str, salary: str, description: str, skills: str, posted_by: str) -> Dict:
        conn = self.connect()
        cursor = conn.cursor()
        job_id = f"JOB{secrets.token_hex(4).upper()}"
        
        cursor.execute('''
            INSERT INTO jobs (job_id, title, company, type, location, salary, description, skills_required, posted_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (job_id, title, company, job_type, location, salary, description, skills, posted_by))
        conn.commit()
        conn.close()
        return {"status": "success", "job_id": job_id}
    
    def get_active_jobs(self) -> List[Dict]:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE is_active = 1 ORDER BY posted_date DESC')
        jobs = cursor.fetchall()
        conn.close()
        return [{"job_id": j[1], "title": j[2], "company": j[3], "type": j[4], "location": j[5], "salary": j[6]} for j in jobs]
    
    # --- Contact Messages ---
    def save_contact(self, name: str, email: str, phone: str, subject: str, message: str) -> Dict:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO contact_messages (name, email, phone, subject, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, phone, subject, message))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Message received"}
    
    # --- Stats ---
    def get_stats(self) -> Dict:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        users = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM applications')
        apps = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE is_active = 1')
        jobs = cursor.fetchone()[0]
        conn.close()
        return {"users": users, "applications": apps, "active_jobs": jobs}

# Initialize database
db = Database()