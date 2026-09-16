-- ============================================================================
-- Charvak IT Consulting - Mock Drives + Assessment Results (Tier 3)
-- Migration: 20260917_mock_drives.sql
-- Created:   2026-09-17
-- Purpose:   Persist company mock drive sessions, answers, and all
--            assessment results. Fixes: in-memory dict loss on Render restart.
-- Safety:    All CREATE ... IF NOT EXISTS. Adds tables only; no existing table altered.
-- Rollback:  DROP TABLE IF EXISTS charvak_mock_answers;
--            DROP TABLE IF EXISTS charvak_mock_sessions;
--            DROP TABLE IF EXISTS charvak_assessment_results;
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Mock drive sessions (one row per started company mock drive)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_mock_sessions (
    session_id       TEXT PRIMARY KEY,
    email            TEXT NOT NULL,
    company_id       TEXT NOT NULL,
    company_name     TEXT NOT NULL,
    pattern          TEXT NOT NULL,
    sections_json    JSONB NOT NULL,
    total_questions  INTEGER NOT NULL,
    started_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at     TIMESTAMP,
    status           TEXT NOT NULL DEFAULT 'in_progress',
    score            NUMERIC(5,2),
    correct_count    INTEGER,
    passed           BOOLEAN
);
CREATE INDEX IF NOT EXISTS idx_mock_sessions_email  ON charvak_mock_sessions(email);
CREATE INDEX IF NOT EXISTS idx_mock_sessions_status ON charvak_mock_sessions(status);

-- ---------------------------------------------------------------------------
-- 2. Mock drive answers (one row per answered question)
--    UNIQUE on (session_id, section_name, question_id) so re-answering
--    updates the existing row instead of creating duplicates.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_mock_answers (
    answer_id     TEXT PRIMARY KEY,
    session_id    TEXT NOT NULL,
    section_name  TEXT NOT NULL,
    question_id   INTEGER NOT NULL,
    selected      INTEGER NOT NULL,
    submitted_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, section_name, question_id)
);
CREATE INDEX IF NOT EXISTS idx_mock_answers_session ON charvak_mock_answers(session_id);

-- ---------------------------------------------------------------------------
-- 3. Assessment results (backs results_system.py - used by mock drives and
--    any future assessment feature that calls record_assessment_result).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_assessment_results (
    result_id        TEXT PRIMARY KEY,
    email            TEXT NOT NULL,
    assessment_type  TEXT NOT NULL,
    assessment_name  TEXT NOT NULL,
    score            NUMERIC(5,2) NOT NULL,
    total_questions  INTEGER NOT NULL,
    correct_answers  INTEGER NOT NULL,
    percentage       NUMERIC(5,2) NOT NULL,
    passed           BOOLEAN NOT NULL,
    details_json     JSONB,
    completed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_assessment_results_email ON charvak_assessment_results(email);
CREATE INDEX IF NOT EXISTS idx_assessment_results_type  ON charvak_assessment_results(assessment_type);
CREATE INDEX IF NOT EXISTS idx_assessment_results_completed ON charvak_assessment_results(completed_at DESC);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================