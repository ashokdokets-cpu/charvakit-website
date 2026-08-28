"""
Charvakit Database Module
PostgreSQL (production) + SQLite (development fallback)
"""
import os
import sqlite3
import secrets
from datetime import datetime, timedelta

# Try PostgreSQL, fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Check if we're on PostgreSQL
USE_POSTGRES = DATABASE_URL and "postgres" in DATABASE_URL

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras

class Database:
    def __init__(self, db_path="charvakit.db"):
        self.db_path = db_path
        if USE_POSTGRES:
            self.init_postgres()
        else:
            self.init_sqlite()
    
    # ============ POSTGRESQL ============
    def init_postgres(self):
        """Initialize PostgreSQL tables"""
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    job_title VARCHAR(255),
                    company VARCHAR(255),
                    email VARCHAR(255),
                    date TIMESTAMP DEFAULT NOW(),
                    source VARCHAR(50) DEFAULT 'job_board',
                    status VARCHAR(50) DEFAULT 'new'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255),
                    company VARCHAR(255),
                    type VARCHAR(50),
                    location VARCHAR(255),
                    salary VARCHAR(100),
                    description TEXT,
                    skills VARCHAR(500),
                    posted_date TIMESTAMP DEFAULT NOW(),
                    expiry_date TIMESTAMP DEFAULT (NOW() + INTERVAL '45 days'),
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            conn.commit()
            conn.close()
            print("PostgreSQL tables ready")
        except Exception as e:
            print(f"PostgreSQL init error: {e}")
    
    def save_application(self, data: dict):
        """Save application to PostgreSQL"""
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO applications (name, job_title, company, date, source)
                VALUES (%s, %s, %s, %s, %s)
            ''', (data.get('name'), data.get('title'), data.get('company'),
                  data.get('date', datetime.now().isoformat()), data.get('source', 'job_board')))
            conn.commit()
            conn.close()
            return True
        except:
            return self._save_sqlite(data)
    
    def get_applications(self):
        """Get all applications from PostgreSQL"""
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute('SELECT * FROM applications ORDER BY date DESC')
            apps = cursor.fetchall()
            conn.close()
            return [dict(a) for a in apps]
        except:
            return self._get_applications_sqlite()
    
    def get_active_jobs(self):
        """Get non-expired jobs from PostgreSQL"""
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute('SELECT * FROM jobs WHERE is_active = TRUE AND expiry_date > NOW()')
            jobs = cursor.fetchall()
            conn.close()
            return [dict(j) for j in jobs]
        except:
            return []
    
    def expire_old_jobs(self):
        """Archive jobs past expiry date"""
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute('UPDATE jobs SET is_active = FALSE WHERE expiry_date < NOW()')
            conn.commit()
            conn.close()
        except:
            pass
    
    # ============ SQLITE FALLBACK ============
    def _save_sqlite(self, data: dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO applications (application_id, user_id, job_title, company, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (f"APP{secrets.token_hex(4).upper()}", 'user', 
              data.get('title'), data.get('company'), 'job_board'))
        conn.commit()
        conn.close()
        return True
    
    def _get_applications_sqlite(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM applications ORDER BY last_updated DESC')
            apps = cursor.fetchall()
            conn.close()
            return [{"name": a[2], "job_title": a[3], "company": a[4], "date": a[7]} for a in apps]
        except:
            conn.close()
            return []
    
    def init_sqlite(self):
        """Create all SQLite tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
    
    # Common methods
    def create_user(self, email: str, password: str, name: str, role: str = "candidate", phone: str = None):
        import psycopg2
        import hashlib
        import os
        import secrets as secrets_module

        user_id = f"USR{secrets.token_hex(4).upper()}"
        salt = secrets_module.token_hex(16)
        password_hash = f"{salt}${hashlib.sha256(f\"{salt}:{password}\".encode()).hexdigest()}"

        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL", ""))
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (user_id, email, password_hash, name, phone, role) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, email, password_hash, name, phone, role)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return {"status": "success", "user_id": user_id}
        except Exception as e:
            return {"status": "error", "message": "Email already registered"}

    def get_user_by_email(self, email: str):
        """Get user by email"""
        import psycopg2
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, email, password_hash, name, phone, role FROM users WHERE email = %s', (email,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row:
                return {
                    "user_id": row[0],
                    "email": row[1],
                    "password_hash": row[2],
                    "name": row[3],
                    "phone": row[4],
                    "role": row[5]
                }
            return None
        except Exception as e:
            print(f"get_user_by_email error: {e}")
            return None

# Initialize database
db = Database()
