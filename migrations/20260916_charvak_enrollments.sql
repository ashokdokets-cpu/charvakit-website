-- ============================================================================
-- Charvak IT Consulting - Enrollments Table (backfill)
-- Migration: 20260916_charvak_enrollments.sql
-- Created:   2026-09-19 (Session I backfill)
-- Purpose:   Ensure charvak_enrollments exists before course_payments.sql runs.
--            Previously this table was created only by ai_courses._ensure_tables()
--            and scripts/migrate_tier3_courses.py — meaning a fresh migration
--            restore could fail on the index in 20260916_course_payments.sql.
-- Safety:    All CREATE ... IF NOT EXISTS. Safe to re-run.
-- Rollback:  DROP TABLE IF EXISTS charvak_enrollments;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_enrollments (
    enrollment_id   TEXT        PRIMARY KEY,
    email           TEXT        NOT NULL,
    course_name     TEXT        NOT NULL,
    duration_weeks  INTEGER     DEFAULT 8,
    user_level      TEXT        DEFAULT 'beginner',
    curriculum      JSONB,
    progress        INTEGER     DEFAULT 0,
    total_weeks     INTEGER     DEFAULT 8,
    status          TEXT        DEFAULT 'active',
    started_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_charvak_enrollments_email
    ON charvak_enrollments(email);
CREATE INDEX IF NOT EXISTS idx_charvak_enrollments_course
    ON charvak_enrollments(course_name);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
