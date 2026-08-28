"""
Charvakit Database Module
PostgreSQL database connection and operations
"""
import os
import secrets
import hashlib
import psycopg2
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "")


class Database:
    def __init__(self):
        self.db_url = DATABASE_URL
        self.init_db()
    
    def get_connection(self):
        """Get PostgreSQL connection."""
        return psycopg2.connect(self.db_url)
    
    def init_db(self):
        """Initialize database tables."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
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
            conn.commit()
            cursor.close()
            conn.close()
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