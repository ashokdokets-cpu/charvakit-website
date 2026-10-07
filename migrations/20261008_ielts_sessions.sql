-- ============================================================
-- Session 40b - IELTS session persistence
-- ============================================================
-- One generic session table for all four IELTS sub-tests.
-- The four existing attempt tables (charvak_ielts_reading_attempts,
-- charvak_ielts_listening_attempts, etc.) stay as-is - they capture
-- per-attempt detail. This new table captures the SESSION lifecycle:
-- started_at, completed_at, band_score, integrity_summary.
--
-- Session ID prefixes:
--   IELTS-W-XXXXXXXX  ->  test_type = 'writing'
--   IELTS-R-XXXXXXXX  ->  test_type = 'reading'
--   IELTS-L-XXXXXXXX  ->  test_type = 'listening'
--   IELTS-S-XXXXXXXX  ->  test_type = 'speaking'
-- ============================================================

CREATE TABLE IF NOT EXISTS charvak_ielts_sessions (
    session_id        TEXT PRIMARY KEY,
    email             TEXT NOT NULL,
    test_type         TEXT NOT NULL,
    content_ref       TEXT,
    status            TEXT NOT NULL DEFAULT 'in_progress',
    band_score        NUMERIC,
    details_json      JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at        TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at      TIMESTAMP WITHOUT TIME ZONE,
    integrity_summary JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_ielts_sessions_email
    ON charvak_ielts_sessions (email);

CREATE INDEX IF NOT EXISTS idx_ielts_sessions_type
    ON charvak_ielts_sessions (test_type);

CREATE INDEX IF NOT EXISTS idx_ielts_sessions_status
    ON charvak_ielts_sessions (status);

CREATE INDEX IF NOT EXISTS idx_ielts_sessions_started
    ON charvak_ielts_sessions (started_at DESC);