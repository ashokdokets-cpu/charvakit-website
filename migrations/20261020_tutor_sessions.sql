-- Session 67a: AI Tutor persistent sessions + messages
-- Replaces in-memory self.sessions dict with DB-backed storage.
-- Idempotent: safe to run multiple times.

CREATE TABLE IF NOT EXISTS charvak_tutor_sessions (
    session_id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    course_name TEXT NOT NULL,
    enrollment_id TEXT,
    week_num INTEGER,
    topic TEXT,
    user_level TEXT DEFAULT 'beginner',
    turn_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS charvak_tutor_messages (
    message_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tutor_sessions_email
    ON charvak_tutor_sessions(email, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_tutor_sessions_enrollment
    ON charvak_tutor_sessions(enrollment_id);
CREATE INDEX IF NOT EXISTS idx_tutor_messages_session
    ON charvak_tutor_messages(session_id, created_at);
