-- ============================================================================
-- Charvak IT Consulting - NA VMS Connector Persistence (Tier 3, Session G/2)
-- Migration: 20260918_na_vms_connector_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist VMS-ingested jobs + submissions to Postgres.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_na_vms_submissions;
--            DROP TABLE IF EXISTS charvak_na_vms_jobs;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_na_vms_jobs (
    job_id               TEXT PRIMARY KEY,
    source               TEXT,
    title                TEXT,
    client               TEXT,
    vms_provider         TEXT,
    location             TEXT,
    rate_range           JSONB DEFAULT '{}'::jsonb,
    skills_required      JSONB DEFAULT '[]'::jsonb,
    visa_restrictions    JSONB DEFAULT '[]'::jsonb,
    duration             TEXT,
    status               TEXT DEFAULT 'Active - Accepting Submissions',
    posted_date          TEXT,
    submission_deadline  TEXT,
    submission_limit     INTEGER DEFAULT 3,
    interview_process    TEXT,
    compliance_notes     TEXT,
    ghost_score          NUMERIC(3,2) DEFAULT 0,
    is_ghost             BOOLEAN DEFAULT FALSE,
    ingested_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_na_vms_jobs_status   ON charvak_na_vms_jobs(status);
CREATE INDEX IF NOT EXISTS idx_na_vms_jobs_ghost    ON charvak_na_vms_jobs(is_ghost);
CREATE INDEX IF NOT EXISTS idx_na_vms_jobs_source   ON charvak_na_vms_jobs(source);

CREATE TABLE IF NOT EXISTS charvak_na_vms_submissions (
    submission_id  TEXT PRIMARY KEY,
    job_id         TEXT NOT NULL,
    candidate_id   TEXT,
    vendor_id      TEXT,
    status         TEXT DEFAULT 'Submitted',
    work_auth      JSONB DEFAULT '{}'::jsonb,
    timeline       JSONB DEFAULT '[]'::jsonb,
    submitted_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_na_vms_subs_job       ON charvak_na_vms_submissions(job_id);
CREATE INDEX IF NOT EXISTS idx_na_vms_subs_candidate ON charvak_na_vms_submissions(candidate_id);
CREATE INDEX IF NOT EXISTS idx_na_vms_subs_status    ON charvak_na_vms_submissions(status);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================