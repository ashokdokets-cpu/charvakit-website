-- ============================================================================
-- Charvak IT Consulting - University Engine Persistence (Tier 3, Session D/3)
-- Migration: 20260918_university_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist universities, students, first-destination outcomes.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_university_outcomes;
--            DROP TABLE IF EXISTS charvak_university_students;
--            DROP TABLE IF EXISTS charvak_universities;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_universities (
    university_id   TEXT PRIMARY KEY,
    name            TEXT,
    admin_email     TEXT,
    location        TEXT DEFAULT '',
    type            TEXT DEFAULT 'University',
    student_count   INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_universities_admin ON charvak_universities(admin_email);
CREATE INDEX IF NOT EXISTS idx_universities_name  ON charvak_universities(name);

CREATE TABLE IF NOT EXISTS charvak_university_students (
    student_id        TEXT PRIMARY KEY,
    university_id     TEXT NOT NULL,
    name              TEXT,
    email             TEXT,
    graduation_year   INTEGER DEFAULT 2026,
    status            TEXT DEFAULT 'enrolled',
    placement_status  TEXT DEFAULT 'not_placed',
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_unistudents_university ON charvak_university_students(university_id);
CREATE INDEX IF NOT EXISTS idx_unistudents_email      ON charvak_university_students(email);
CREATE INDEX IF NOT EXISTS idx_unistudents_placement  ON charvak_university_students(placement_status);

CREATE TABLE IF NOT EXISTS charvak_university_outcomes (
    outcome_id     TEXT PRIMARY KEY,
    student_id     TEXT NOT NULL,
    outcome_type   TEXT DEFAULT 'employed',
    company_name   TEXT DEFAULT '',
    salary         NUMERIC(12,2) DEFAULT 0,
    job_title      TEXT DEFAULT '',
    location       TEXT DEFAULT '',
    recorded_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_unioutcomes_student ON charvak_university_outcomes(student_id);
CREATE INDEX IF NOT EXISTS idx_unioutcomes_type    ON charvak_university_outcomes(outcome_type);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================