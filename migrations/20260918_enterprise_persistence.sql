-- ============================================================================
-- Charvak IT Consulting - Enterprise Persistence (Tier 3, Session B/2)
-- Migration: 20260918_enterprise_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist all 8 enterprise modules to Postgres.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_enterprise_kiosk_sessions;
--            DROP TABLE IF EXISTS charvak_enterprise_surveys;
--            DROP TABLE IF EXISTS charvak_enterprise_resume_books;
--            DROP TABLE IF EXISTS charvak_enterprise_employer_tiers;
--            DROP TABLE IF EXISTS charvak_enterprise_appointments;
--            DROP TABLE IF EXISTS charvak_enterprise_resume_approvals;
--            DROP TABLE IF EXISTS charvak_enterprise_pathways;
--            DROP TABLE IF EXISTS charvak_enterprise_salary_data;
-- ============================================================================

-- 1. SALARY BENCHMARKING
CREATE TABLE IF NOT EXISTS charvak_enterprise_salary_data (
    salary_id        TEXT PRIMARY KEY,
    university       TEXT,
    major            TEXT DEFAULT '',
    industry         TEXT DEFAULT '',
    base_salary      NUMERIC(12,2) DEFAULT 0,
    signing_bonus    NUMERIC(12,2) DEFAULT 0,
    location         TEXT DEFAULT '',
    graduation_year  INTEGER DEFAULT 2026,
    recorded_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ent_salary_univ  ON charvak_enterprise_salary_data(university);
CREATE INDEX IF NOT EXISTS idx_ent_salary_inds  ON charvak_enterprise_salary_data(industry);
CREATE INDEX IF NOT EXISTS idx_ent_salary_loc   ON charvak_enterprise_salary_data(location);

-- 2. STUDENT PATHWAYS
CREATE TABLE IF NOT EXISTS charvak_enterprise_pathways (
    pathway_id   TEXT PRIMARY KEY,
    name         TEXT,
    description  TEXT DEFAULT '',
    steps        JSONB DEFAULT '[]'::jsonb,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ent_pathways_name ON charvak_enterprise_pathways(name);

-- 3. RESUME APPROVAL WORKFLOW
CREATE TABLE IF NOT EXISTS charvak_enterprise_resume_approvals (
    review_id          TEXT PRIMARY KEY,
    student_id         TEXT,
    student_name       TEXT,
    resume_text        TEXT DEFAULT '',
    status             TEXT DEFAULT 'pending',
    reviewer_comments  TEXT DEFAULT '',
    submitted_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at        TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ent_resume_student ON charvak_enterprise_resume_approvals(student_id);
CREATE INDEX IF NOT EXISTS idx_ent_resume_status  ON charvak_enterprise_resume_approvals(status);

-- 4. APPOINTMENT BOOKING
CREATE TABLE IF NOT EXISTS charvak_enterprise_appointments (
    appointment_id     TEXT PRIMARY KEY,
    student_id         TEXT,
    student_name       TEXT,
    advisor_id         TEXT,
    date               TEXT,
    duration_minutes   INTEGER DEFAULT 30,
    reason             TEXT DEFAULT 'Career Counseling',
    status             TEXT DEFAULT 'booked',
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ent_appt_advisor ON charvak_enterprise_appointments(advisor_id);
CREATE INDEX IF NOT EXISTS idx_ent_appt_student ON charvak_enterprise_appointments(student_id);

-- 5. EMPLOYER TIERING
CREATE TABLE IF NOT EXISTS charvak_enterprise_employer_tiers (
    tier_id       TEXT PRIMARY KEY,
    company_name  TEXT,
    tier          TEXT DEFAULT 'tier2',
    notes         TEXT DEFAULT '',
    set_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ent_tiers_tier    ON charvak_enterprise_employer_tiers(tier);
CREATE INDEX IF NOT EXISTS idx_ent_tiers_company ON charvak_enterprise_employer_tiers(company_name);

-- 6. RESUME BOOKS
CREATE TABLE IF NOT EXISTS charvak_enterprise_resume_books (
    book_id      TEXT PRIMARY KEY,
    name         TEXT,
    description  TEXT DEFAULT '',
    student_ids  JSONB DEFAULT '[]'::jsonb,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ent_books_name ON charvak_enterprise_resume_books(name);

-- 7. SURVEYS
CREATE TABLE IF NOT EXISTS charvak_enterprise_surveys (
    survey_id   TEXT PRIMARY KEY,
    title       TEXT,
    questions   JSONB DEFAULT '[]'::jsonb,
    responses   INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ent_surveys_title ON charvak_enterprise_surveys(title);

-- 8. KIOSK MODE
CREATE TABLE IF NOT EXISTS charvak_enterprise_kiosk_sessions (
    kiosk_id     TEXT PRIMARY KEY,
    event_id     TEXT,
    location     TEXT DEFAULT 'Main Entrance',
    status       TEXT DEFAULT 'active',
    check_ins    INTEGER DEFAULT 0,
    started_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ent_kiosks_event  ON charvak_enterprise_kiosk_sessions(event_id);
CREATE INDEX IF NOT EXISTS idx_ent_kiosks_status ON charvak_enterprise_kiosk_sessions(status);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================