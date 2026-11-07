-- Migration: 20261108_relevance_filter.sql
-- Purpose: Add tables for bench-relevance filter (Session 108G)
-- Idempotent: Safe to run multiple times

-- Rejected JDs audit trail
CREATE TABLE IF NOT EXISTS charvak_rejected_jds (
    rejected_id         TEXT PRIMARY KEY,
    source              TEXT NOT NULL,
    raw_email_subject   TEXT,
    raw_email_from      TEXT,
    role_title          TEXT,
    company             TEXT,
    location            TEXT,
    skills_required     TEXT,
    work_auth_required  TEXT,
    rate_min            FLOAT,
    rate_max            FLOAT,
    raw_json            JSONB,
    reject_reason       TEXT NOT NULL,
    best_candidate_hint TEXT,
    skills_overlap_pct  FLOAT,
    rejected_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rejected_jds_reason ON charvak_rejected_jds (reject_reason, rejected_at DESC);
CREATE INDEX IF NOT EXISTS idx_rejected_jds_date ON charvak_rejected_jds (rejected_at DESC);

-- Config table (per-candidate relevance rules)
CREATE TABLE IF NOT EXISTS charvak_bench_relevance_config (
    config_id           TEXT PRIMARY KEY DEFAULT 'default',
    skill_overlap_min   FLOAT DEFAULT 0.30,
    log_rejected_jds    BOOLEAN DEFAULT TRUE,
    retention_days      INTEGER DEFAULT 30,
    rate_weight         FLOAT DEFAULT 0.10,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed default config
INSERT INTO charvak_bench_relevance_config (config_id) VALUES ('default')
ON CONFLICT (config_id) DO NOTHING;

-- Per-candidate visa acceptance override (optional)
CREATE TABLE IF NOT EXISTS charvak_candidate_visa_accepts (
    candidate_email     TEXT NOT NULL,
    accepts_visa        TEXT NOT NULL,
    PRIMARY KEY (candidate_email, accepts_visa)
);

-- Default: each candidate accepts their own visa + 'Any'
INSERT INTO charvak_candidate_visa_accepts (candidate_email, accepts_visa)
SELECT email, work_auth_status FROM charvak_candidates WHERE work_auth_status IS NOT NULL
ON CONFLICT DO NOTHING;

INSERT INTO charvak_candidate_visa_accepts (candidate_email, accepts_visa)
SELECT email, 'Any' FROM charvak_candidates
ON CONFLICT DO NOTHING;
