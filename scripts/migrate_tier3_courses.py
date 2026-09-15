"""
Tier 3 Session 4 — AI Courses persistence
Creates 4 tables:
  - charvak_courses        (course catalog)
  - charvak_enrollments    (user enrollments)
  - charvak_course_lessons (AI-generated weekly lessons, cached)
  - charvak_certificates   (completion certificates)
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

print("Creating tables...\n")

# 1. charvak_courses — catalog
cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_courses (
        course_id TEXT PRIMARY KEY,
        course_name TEXT NOT NULL UNIQUE,
        category TEXT DEFAULT 'Technology',
        duration_weeks INTEGER DEFAULT 8,
        price_inr INTEGER DEFAULT 0,
        description TEXT DEFAULT '',
        level TEXT DEFAULT 'Beginner',
        icon TEXT DEFAULT '',
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_courses_category ON charvak_courses(category)")
print("  [OK] charvak_courses")

# 2. charvak_enrollments
cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_enrollments (
        enrollment_id TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        course_name TEXT NOT NULL,
        duration_weeks INTEGER DEFAULT 8,
        user_level TEXT DEFAULT 'beginner',
        curriculum JSONB,
        progress INTEGER DEFAULT 0,
        total_weeks INTEGER DEFAULT 8,
        status TEXT DEFAULT 'active',
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_enrollments_email ON charvak_enrollments(email)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_enrollments_course ON charvak_enrollments(course_name)")
print("  [OK] charvak_enrollments")

# 3. charvak_course_lessons — cached AI-generated lessons
cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_course_lessons (
        lesson_id TEXT PRIMARY KEY,
        enrollment_id TEXT NOT NULL,
        week_num INTEGER NOT NULL,
        topic TEXT DEFAULT '',
        lesson_content JSONB,
        completed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(enrollment_id, week_num)
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_lessons_enrollment ON charvak_course_lessons(enrollment_id)")
print("  [OK] charvak_course_lessons")

# 4. charvak_certificates
cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_certificates (
        certificate_id TEXT PRIMARY KEY,
        enrollment_id TEXT NOT NULL,
        email TEXT NOT NULL,
        course_name TEXT NOT NULL,
        duration_weeks INTEGER,
        issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_certs_email ON charvak_certificates(email)")
print("  [OK] charvak_certificates")

conn.commit()

print("\nVerifying:")
for t in ['charvak_courses', 'charvak_enrollments', 'charvak_course_lessons', 'charvak_certificates']:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"  {t}: {cur.fetchone()[0]} rows")

cur.close()
conn.close()
print("\nMigration complete.")