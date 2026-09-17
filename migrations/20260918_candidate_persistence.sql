-- ============================================================================
-- Charvak IT Consulting - Candidate Engine Persistence (Session A/2)
-- Migration: 20260918_candidate_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist candidate pool + skill profiles to Postgres so they
--            survive Render restarts.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_candidates;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_candidates (
    candidate_id        TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    email               TEXT NOT NULL UNIQUE,
    phone               TEXT DEFAULT '',

    -- Career
    skills              JSONB DEFAULT '[]'::jsonb,
    experience_years    INTEGER DEFAULT 0,
    years_coding        INTEGER,
    job_title           TEXT DEFAULT '',
    preferred_roles     JSONB DEFAULT '[]'::jsonb,

    -- Contact & portfolio
    location            TEXT DEFAULT '',
    visa_status         TEXT DEFAULT '',
    portfolio_url       TEXT DEFAULT '',
    github_url          TEXT DEFAULT '',
    linkedin_url        TEXT DEFAULT '',
    resume_text         TEXT DEFAULT '',

    -- Education
    education           TEXT DEFAULT '',
    degree              TEXT DEFAULT '',
    major               TEXT DEFAULT '',
    university          TEXT DEFAULT '',
    gpa                 NUMERIC(4,2),
    graduation_year     INTEGER,

    -- Certifications & languages
    certifications      JSONB DEFAULT '[]'::jsonb,
    languages_spoken    JSONB DEFAULT '[]'::jsonb,

    -- Authorization
    work_authorization  TEXT DEFAULT '',
    willing_to_relocate BOOLEAN DEFAULT FALSE,

    -- Preferences
    remote_preference   TEXT DEFAULT 'Open',
    salary_expectation  TEXT DEFAULT '',
    availability        TEXT DEFAULT 'Immediate',

    -- Verification
    status              TEXT DEFAULT 'registered',
    skill_score         INTEGER,
    badge_id            TEXT,

    -- Placement (free-form JSONB from mark_placed)
    placement           JSONB,

    -- Timestamps
    registered_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Search filter indexes
CREATE INDEX IF NOT EXISTS idx_candidates_email         ON charvak_candidates(email);
CREATE INDEX IF NOT EXISTS idx_candidates_status        ON charvak_candidates(status);
CREATE INDEX IF NOT EXISTS idx_candidates_location      ON charvak_candidates(location);
CREATE INDEX IF NOT EXISTS idx_candidates_experience    ON charvak_candidates(experience_years);
CREATE INDEX IF NOT EXISTS idx_candidates_skill_score   ON charvak_candidates(skill_score);
CREATE INDEX IF NOT EXISTS idx_candidates_visa          ON charvak_candidates(visa_status);
CREATE INDEX IF NOT EXISTS idx_candidates_university    ON charvak_candidates(university);
CREATE INDEX IF NOT EXISTS idx_candidates_grad_year     ON charvak_candidates(graduation_year);
CREATE INDEX IF NOT EXISTS idx_candidates_skills_gin    ON charvak_candidates USING GIN (skills);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================