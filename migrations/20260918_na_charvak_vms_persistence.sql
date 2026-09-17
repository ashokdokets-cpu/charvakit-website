-- ============================================================================
-- Charvak IT Consulting - NA Native VMS Persistence (Tier 3, Session G/6)
-- Migration: 20260918_na_charvak_vms_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist requisitions, timecards, SOW contracts to Postgres.
--            vendor_performance is a dead field (never written) - no table.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_na_cvms_sow_contracts;
--            DROP TABLE IF EXISTS charvak_na_cvms_timecards;
--            DROP TABLE IF EXISTS charvak_na_cvms_requisitions;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_na_cvms_requisitions (
    req_id               TEXT PRIMARY KEY,
    client_id            TEXT NOT NULL,
    title                TEXT,
    description          TEXT DEFAULT '',
    skills_required      JSONB DEFAULT '[]'::jsonb,
    rate_range           JSONB DEFAULT '{}'::jsonb,
    location             TEXT DEFAULT 'Remote',
    duration             TEXT DEFAULT '6 months',
    visa_restrictions    JSONB DEFAULT '[]'::jsonb,
    submission_limit     INTEGER DEFAULT 3,
    status               TEXT DEFAULT 'Open - Accepting Submissions',
    submissions_count    INTEGER DEFAULT 0,
    interviews_scheduled INTEGER DEFAULT 0,
    offer_extended       BOOLEAN DEFAULT FALSE,
    timeline             JSONB DEFAULT '[]'::jsonb,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_na_cvms_req_client ON charvak_na_cvms_requisitions(client_id);
CREATE INDEX IF NOT EXISTS idx_na_cvms_req_status ON charvak_na_cvms_requisitions(status);

CREATE TABLE IF NOT EXISTS charvak_na_cvms_timecards (
    timecard_id        TEXT PRIMARY KEY,
    req_id             TEXT NOT NULL,
    candidate_id       TEXT,
    hours              NUMERIC(8,2) DEFAULT 0,
    rate               NUMERIC(8,2) DEFAULT 0,
    gross_amount       NUMERIC(12,2) DEFAULT 0,
    charvak_fee        NUMERIC(12,2) DEFAULT 0,
    net_amount         NUMERIC(12,2) DEFAULT 0,
    period_end         TEXT,
    status             TEXT DEFAULT 'Submitted for Approval',
    payment_triggered  BOOLEAN DEFAULT FALSE,
    payment_reference  TEXT,
    approval_history   JSONB DEFAULT '[]'::jsonb,
    submitted_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_na_cvms_tc_req       ON charvak_na_cvms_timecards(req_id);
CREATE INDEX IF NOT EXISTS idx_na_cvms_tc_candidate ON charvak_na_cvms_timecards(candidate_id);
CREATE INDEX IF NOT EXISTS idx_na_cvms_tc_status    ON charvak_na_cvms_timecards(status);

CREATE TABLE IF NOT EXISTS charvak_na_cvms_sow_contracts (
    sow_id             TEXT PRIMARY KEY,
    client_id          TEXT NOT NULL,
    vendor_id          TEXT NOT NULL,
    title              TEXT,
    description        TEXT,
    deliverables       JSONB DEFAULT '[]'::jsonb,
    total_value        NUMERIC(12,2) DEFAULT 0,
    start_date         TEXT,
    end_date           TEXT,
    milestones         JSONB DEFAULT '[]'::jsonb,
    payment_schedule   JSONB DEFAULT '[]'::jsonb,
    status             TEXT DEFAULT 'Active',
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_na_cvms_sow_client ON charvak_na_cvms_sow_contracts(client_id);
CREATE INDEX IF NOT EXISTS idx_na_cvms_sow_vendor ON charvak_na_cvms_sow_contracts(vendor_id);
CREATE INDEX IF NOT EXISTS idx_na_cvms_sow_status ON charvak_na_cvms_sow_contracts(status);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================