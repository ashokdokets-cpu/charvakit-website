-- ============================================================================
-- Charvak IT Consulting - AI Internship Persistence (Tier 3, Session E/3)
-- Migration: 20260918_ai_internship_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist enrollments + daily submissions to Postgres.
--            Static program catalog (20 programs) stays in code.
-- Safety:    All CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_ai_internship_submissions;
--            DROP TABLE IF EXISTS charvak_ai_internship_enrollments;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_ai_internship_enrollments (
    enrollment_id  TEXT PRIMARY KEY,
    email          TEXT NOT NULL,
    program_id     TEXT NOT NULL,
    duration       TEXT DEFAULT 'standard',
    total_days     INTEGER DEFAULT 28,
    current_day    INTEGER DEFAULT 1,
    status         TEXT NOT NULL DEFAULT 'active',
    start_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at   TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ai_intern_email     ON charvak_ai_internship_enrollments(email);
CREATE INDEX IF NOT EXISTS idx_ai_intern_program   ON charvak_ai_internship_enrollments(program_id);
CREATE INDEX IF NOT EXISTS idx_ai_intern_status    ON charvak_ai_internship_enrollments(status);

CREATE TABLE IF NOT EXISTS charvak_ai_internship_submissions (
    submission_id  TEXT PRIMARY KEY,
    enrollment_id  TEXT NOT NULL,
    day            INTEGER NOT NULL,
    submission     TEXT,
    ai_feedback    JSONB DEFAULT '{}'::jsonb,
    submitted_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(enrollment_id, day)
);
CREATE INDEX IF NOT EXISTS idx_ai_intern_sub_enroll ON charvak_ai_internship_submissions(enrollment_id);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================