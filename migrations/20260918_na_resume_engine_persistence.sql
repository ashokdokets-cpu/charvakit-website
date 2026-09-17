-- ============================================================================
-- Charvak IT Consulting - NA Resume Engine Persistence (Tier 3, Session G/4)
-- Migration: 20260918_na_resume_engine_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist PII redaction log, compliance reports, sub-vendors,
--            and sub-vendor submissions to Postgres.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_na_sub_vendor_submissions;
--            DROP TABLE IF EXISTS charvak_na_sub_vendors;
--            DROP TABLE IF EXISTS charvak_na_compliance_reports;
--            DROP TABLE IF EXISTS charvak_na_redaction_log;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_na_redaction_log (
    log_id           TEXT PRIMARY KEY,
    candidate_id     TEXT,
    redactions       JSONB DEFAULT '{}'::jsonb,
    original_length  INTEGER DEFAULT 0,
    redacted_length  INTEGER DEFAULT 0,
    redacted_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_na_redact_candidate ON charvak_na_redaction_log(candidate_id);
CREATE INDEX IF NOT EXISTS idx_na_redact_time      ON charvak_na_redaction_log(redacted_at);

CREATE TABLE IF NOT EXISTS charvak_na_compliance_reports (
    report_id              TEXT PRIMARY KEY,
    report_type            TEXT NOT NULL,
    job_id                 TEXT,
    candidate_id           TEXT,
    eeoc_compliant         BOOLEAN,
    nyc_law_144_applicable BOOLEAN,
    issues                 JSONB DEFAULT '[]'::jsonb,
    warnings               JSONB DEFAULT '[]'::jsonb,
    restrictions           JSONB DEFAULT '[]'::jsonb,
    checked_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_na_comp_type      ON charvak_na_compliance_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_na_comp_job       ON charvak_na_compliance_reports(job_id);
CREATE INDEX IF NOT EXISTS idx_na_comp_candidate ON charvak_na_compliance_reports(candidate_id);

CREATE TABLE IF NOT EXISTS charvak_na_sub_vendors (
    vendor_id              TEXT PRIMARY KEY,
    name                   TEXT,
    tier                   TEXT DEFAULT 'Tier-2',
    email                  TEXT,
    specialization         JSONB DEFAULT '[]'::jsonb,
    active_candidates      INTEGER DEFAULT 0,
    successful_placements  INTEGER DEFAULT 0,
    status                 TEXT DEFAULT 'active',
    registered_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_na_vendors_email  ON charvak_na_sub_vendors(email);
CREATE INDEX IF NOT EXISTS idx_na_vendors_status ON charvak_na_sub_vendors(status);

CREATE TABLE IF NOT EXISTS charvak_na_sub_vendor_submissions (
    submission_key  TEXT PRIMARY KEY,
    vendor_id       TEXT NOT NULL,
    candidate_id    TEXT,
    job_id          TEXT,
    status          TEXT DEFAULT 'submitted',
    submitted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_na_vendor_subs_vendor    ON charvak_na_sub_vendor_submissions(vendor_id);
CREATE INDEX IF NOT EXISTS idx_na_vendor_subs_candidate ON charvak_na_sub_vendor_submissions(candidate_id);
CREATE INDEX IF NOT EXISTS idx_na_vendor_subs_status    ON charvak_na_sub_vendor_submissions(status);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================