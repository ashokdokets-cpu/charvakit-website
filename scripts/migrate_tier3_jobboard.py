"""
Tier 3 Session 1 — Job Board + API Sync persistence
Creates 4 tables:
  - charvak_jobs                (job postings)
  - charvak_applications        (job applications)
  - charvak_synced_users        (from api_sync.users_db)
  - charvak_skill_gaps          (from api_sync.skill_gaps_db)
  - charvak_synced_applications (from api_sync.applications_db)
Idempotent — safe to run multiple times.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()
import psycopg2

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("Creating tables...\n")

# 1. charvak_jobs — persistent job postings
cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_jobs (
        job_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        job_type TEXT DEFAULT 'Permanent',
        location TEXT DEFAULT 'Remote',
        salary TEXT DEFAULT '',
        description TEXT DEFAULT '',
        skills TEXT DEFAULT '',
        posted_by TEXT DEFAULT 'api',
        posted_date TEXT DEFAULT '',
        status TEXT DEFAULT 'active',
        applications_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_jobs_status ON charvak_jobs(status)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_jobs_posted_date ON charvak_jobs(posted_date DESC)")
print("  [OK] charvak_jobs")

# 2. charvak_applications — job applications
cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_applications (
        application_id TEXT PRIMARY KEY,
        job_id TEXT NOT NULL,
        user_id TEXT DEFAULT 'anonymous',
        resume_url TEXT DEFAULT '',
        applied_at TEXT DEFAULT '',
        status TEXT DEFAULT 'applied',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_applications_job ON charvak_applications(job_id)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_applications_user ON charvak_applications(user_id)")
print("  [OK] charvak_applications")

# 3. charvak_synced_users — from DoketsRB resume sync
cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_synced_users (
        user_id TEXT PRIMARY KEY,
        doketsrb_id TEXT,
        name TEXT,
        email TEXT,
        phone TEXT,
        resume_data JSONB,
        skills JSONB,
        experience JSONB,
        education JSONB,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
print("  [OK] charvak_synced_users")

# 4. charvak_synced_applications — from DoketsRB application sync
cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_synced_applications (
        application_id TEXT PRIMARY KEY,
        user_id TEXT,
        job_title TEXT,
        company TEXT,
        job_url TEXT,
        status TEXT,
        applied_date TEXT,
        source TEXT DEFAULT 'charvakit',
        notes TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_sync_apps_user ON charvak_synced_applications(user_id)")
print("  [OK] charvak_synced_applications")

# 5. charvak_skill_gaps — from DoketsRB skill analysis
cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_skill_gaps (
        user_id TEXT PRIMARY KEY,
        skill_gaps JSONB,
        recommended_courses JSONB,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
print("  [OK] charvak_skill_gaps")

conn.commit()

# Verify
print("\nVerifying:")
for table in ['charvak_jobs', 'charvak_applications', 'charvak_synced_users', 'charvak_synced_applications', 'charvak_skill_gaps']:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  {table}: {cur.fetchone()[0]} rows")

cur.close()
conn.close()
print("\nMigration complete.")