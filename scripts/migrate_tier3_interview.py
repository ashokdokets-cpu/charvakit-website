"""
Tier 3 Session 3 — Interview Prep persistence
Creates 2 tables:
  - charvak_interview_sessions   (session metadata + final score)
  - charvak_interview_answers    (per-question answers + AI feedback)
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

cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_interview_sessions (
        session_id TEXT PRIMARY KEY,
        candidate_email TEXT NOT NULL,
        role TEXT NOT NULL,
        difficulty TEXT DEFAULT 'Intermediate',
        credits_charged INTEGER DEFAULT 0,
        total_score INTEGER DEFAULT 0,
        max_score INTEGER DEFAULT 0,
        questions_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'in_progress',
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_interview_email ON charvak_interview_sessions(candidate_email)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_interview_status ON charvak_interview_sessions(status)")
print("  [OK] charvak_interview_sessions")

cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_interview_answers (
        answer_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        question_num INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        category TEXT,
        user_answer TEXT,
        ai_score INTEGER,
        ai_feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_answers_session ON charvak_interview_answers(session_id)")
print("  [OK] charvak_interview_answers")

conn.commit()

print("\nVerifying:")
for t in ['charvak_interview_sessions', 'charvak_interview_answers']:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"  {t}: {cur.fetchone()[0]} rows")

cur.close()
conn.close()
print("\nMigration complete.")