-- ============================================================================
-- Charvak IT Consulting - Career V2 Engine Persistence (Tier 3, Session C/2)
-- Migration: 20260918_career_v2_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist Career V2 modules to Postgres so they survive Render
--            restarts: job alerts, saved jobs, company follows, salary
--            reports, interview schedules, offers.
-- Safety:    All CREATE TABLE IF NOT EXISTS. Adds tables only. No existing
--            table altered.
-- Rollback:  DROP TABLE IF EXISTS charvak_career_offers;
--            DROP TABLE IF EXISTS charvak_career_interviews;
--            DROP TABLE IF EXISTS charvak_career_salary_reports;
--            DROP TABLE IF EXISTS charvak_career_company_follows;
--            DROP TABLE IF EXISTS charvak_career_saved_jobs;
--            DROP TABLE IF EXISTS charvak_career_job_alerts;
-- ============================================================================

-- 1. JOB ALERTS
CREATE TABLE IF NOT EXISTS charvak_career_job_alerts (
    alert_id     TEXT PRIMARY KEY,
    email        TEXT NOT NULL,
    keywords     JSONB DEFAULT '[]'::jsonb,
    location     TEXT DEFAULT '',
    frequency    TEXT DEFAULT 'daily',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_career_alerts_email ON charvak_career_job_alerts(email);

-- 2. SAVED JOBS (one row per email+job)
CREATE TABLE IF NOT EXISTS charvak_career_saved_jobs (
    save_id      TEXT PRIMARY KEY,
    email        TEXT NOT NULL,
    job_id       TEXT NOT NULL,
    saved_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(email, job_id)
);
CREATE INDEX IF NOT EXISTS idx_career_saved_email ON charvak_career_saved_jobs(email);

-- 3. COMPANY FOLLOWS (one row per email+company)
CREATE TABLE IF NOT EXISTS charvak_career_company_follows (
    follow_id    TEXT PRIMARY KEY,
    email        TEXT NOT NULL,
    company      TEXT NOT NULL,
    followed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(email, company)
);
CREATE INDEX IF NOT EXISTS idx_career_follows_email ON charvak_career_company_follows(email);

-- 4. SALARY REPORTS (anonymous)
CREATE TABLE IF NOT EXISTS charvak_career_salary_reports (
    salary_id    TEXT PRIMARY KEY,
    role         TEXT NOT NULL,
    company      TEXT DEFAULT 'Anonymous',
    amount       NUMERIC(12,2) DEFAULT 0,
    location     TEXT DEFAULT '',
    recorded_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_career_salary_role ON charvak_career_salary_reports(role);

-- 5. INTERVIEWS
CREATE TABLE IF NOT EXISTS charvak_career_interviews (
    interview_id      TEXT PRIMARY KEY,
    candidate_email   TEXT NOT NULL,
    employer          TEXT,
    role              TEXT,
    date              TEXT,
    platform          TEXT DEFAULT 'Zoom',
    status            TEXT DEFAULT 'scheduled',
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_career_interviews_email ON charvak_career_interviews(candidate_email);

-- 6. OFFERS
CREATE TABLE IF NOT EXISTS charvak_career_offers (
    offer_id          TEXT PRIMARY KEY,
    candidate_email   TEXT NOT NULL,
    company           TEXT,
    role              TEXT,
    salary            NUMERIC(12,2) DEFAULT 0,
    status            TEXT DEFAULT 'received',
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_career_offers_email ON charvak_career_offers(candidate_email);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================