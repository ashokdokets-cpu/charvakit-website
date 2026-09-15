"""
Add recipient_name column to charvak_certificates.
Idempotent.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()
import psycopg2

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute("""
    ALTER TABLE charvak_certificates
    ADD COLUMN IF NOT EXISTS recipient_name TEXT
""")
print("[OK] Added recipient_name column")

# Also add to enrollments so users can edit before generating cert
cur.execute("""
    ALTER TABLE charvak_enrollments
    ADD COLUMN IF NOT EXISTS recipient_name TEXT
""")
print("[OK] Added recipient_name column to enrollments")

conn.commit()
cur.close()
conn.close()
print("\nMigration complete.")