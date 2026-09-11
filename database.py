"""
Charvakit Database Module
PostgreSQL database connection and operations
"""
import os
import secrets
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

class Database:
    def __init__(self):
        self.db_url = DATABASE_URL
        if not self.db_url or self.db_url.startswith("sqlite"):
            print(f"Warning: Using fallback database URL")
        self.init_db()

    def get_connection(self):
        """Get PostgreSQL connection."""
        if not self.db_url or self.db_url.startswith("sqlite"):
            raise Exception("PostgreSQL DATABASE_URL not configured properly")
        return psycopg2.connect(self.db_url)

    def init_db(self):
        """Initialize database tables."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create users table for Charvak
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT,
                    phone TEXT,
                    role TEXT DEFAULT 'candidate',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create applications table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id SERIAL PRIMARY KEY,
                    job_id INTEGER,
                    user_id TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create jobs table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            cursor.close()
            conn.close()
            print("? Database tables initialized successfully")
        except Exception as e:
            print(f"Database init error: {e}")

    def create_user(self, email, password, name, role="candidate", phone=None):
        """Create a new user. Password should already be hashed."""
        user_id = f"USR{secrets.token_hex(4).upper()}"

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (user_id, email, password_hash, name, phone, role) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, email, password, name, phone, role)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return {"status": "success", "user_id": user_id}
        except Exception as e:
            print(f"Create user error: {e}")
            return {"status": "error", "message": "Email already registered"}

    def get_user_by_email(self, email):
        """Get user by email."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, email, password_hash, name, phone, role FROM users WHERE email = %s",
                (email,)
            )
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
            print(f"Get user error: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Get user by ID."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, email, password_hash, name, phone, role FROM users WHERE user_id = %s",
                (user_id,)
            )
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
            print(f"Get user error: {e}")
            return None

    def save_contact(self, name, email, phone, subject, message):
        """Save a contact form submission to the database."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    subject TEXT,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cursor.execute(
                "INSERT INTO contacts (name, email, phone, subject, message) VALUES (%s, %s, %s, %s, %s)",
                (name, email, phone, subject, message)
            )
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Contact saved: {email} ? {subject}")
            return {"status": "success"}
        except Exception as e:
            logger.error(f"save_contact failed: {e}")
            return {"status": "error", "message": str(e)}

    def update_user(self, user_id, **kwargs):
        """Update user fields."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            for key, value in kwargs.items():
                cursor.execute(f"UPDATE users SET {key} = %s WHERE user_id = %s", (value, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def delete_user(self, user_id):
        """Delete user."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


db = Database()
