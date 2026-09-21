-- migrations/20260922_cbat.sql
-- Session M-2: RRB ALP CBAT (Computer-Based Aptitude Test) module.

CREATE TABLE IF NOT EXISTS charvak_cbat_sessions (
    session_id       TEXT PRIMARY KEY,
    email            TEXT NOT NULL,
    sub_test         TEXT NOT NULL,
    sections_json    JSONB NOT NULL,
    total_questions  INTEGER NOT NULL,
    total_time_ms    INTEGER NOT NULL,
    started_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at     TIMESTAMP,
    status           TEXT NOT NULL DEFAULT 'in_progress',
    score            NUMERIC(5,2),
    correct_count    INTEGER,
    passed           BOOLEAN
);
CREATE INDEX IF NOT EXISTS idx_cbat_sessions_email    ON charvak_cbat_sessions(email);
CREATE INDEX IF NOT EXISTS idx_cbat_sessions_sub_test ON charvak_cbat_sessions(sub_test);

CREATE TABLE IF NOT EXISTS charvak_cbat_answers (
    answer_id       TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL,
    question_index  INTEGER NOT NULL,
    selected        INTEGER,
    time_taken_ms   INTEGER,
    is_correct      BOOLEAN,
    submitted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, question_index)
);
CREATE INDEX IF NOT EXISTS idx_cbat_answers_session ON charvak_cbat_answers(session_id);