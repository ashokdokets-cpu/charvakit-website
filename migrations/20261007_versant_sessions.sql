-- ============================================================
-- Session 40a - versant session persistence
-- ============================================================
-- cbt_versant.py was refactored to persist sessions but the
-- migration was never added. This brings the DB in sync.
--
-- Verified against cbt_versant.py:
--   - create_session       INSERT
--   - get_session          SELECT
--   - _upsert_answer       INSERT ... ON CONFLICT
--   - complete_session     SELECT, UPDATE
-- ============================================================

CREATE TABLE IF NOT EXISTS charvak_versant_sessions (
    session_id      TEXT PRIMARY KEY,
    email           TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'in_progress',
    details_json    JSONB NOT NULL DEFAULT '{}'::jsonb,
    overall_score   NUMERIC,
    started_at      TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP WITHOUT TIME ZONE,
    integrity_summary JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_versant_sessions_email
    ON charvak_versant_sessions (email);

CREATE INDEX IF NOT EXISTS idx_versant_sessions_status
    ON charvak_versant_sessions (status);

CREATE INDEX IF NOT EXISTS idx_versant_sessions_started
    ON charvak_versant_sessions (started_at DESC);


CREATE TABLE IF NOT EXISTS charvak_versant_answers (
    answer_id       BIGSERIAL PRIMARY KEY,
    session_id      TEXT NOT NULL,
    section_id      TEXT NOT NULL,
    question_id     TEXT NOT NULL,
    question_text   TEXT,
    answer_text     TEXT,
    transcript      TEXT,
    answered_at     TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT charvak_versant_answers_unique
        UNIQUE (session_id, section_id, question_id)
);

CREATE INDEX IF NOT EXISTS idx_versant_answers_session
    ON charvak_versant_answers (session_id);