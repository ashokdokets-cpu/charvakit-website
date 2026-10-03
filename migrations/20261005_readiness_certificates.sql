-- 20261005_readiness_certificates.sql
-- Sprint A: Free Role Readiness Certificate (Session 17)
-- Stores one certificate per completed career assessment.
-- Idempotent. Safe to run multiple times.

CREATE TABLE IF NOT EXISTS charvak_readiness_certificates (
    certificate_id    TEXT PRIMARY KEY,
    assessment_id     TEXT NOT NULL,
    email             TEXT NOT NULL,
    display_name      TEXT,
    role              TEXT NOT NULL,
    industry          TEXT NOT NULL,
    level             TEXT NOT NULL,
    readiness_score   INTEGER NOT NULL,
    percentile        INTEGER,
    benchmark_score   INTEGER,
    verdict           TEXT,
    payload_json      JSONB,
    certificate_hash  TEXT NOT NULL,
    source            TEXT NOT NULL DEFAULT 'written',
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rdc_email
    ON charvak_readiness_certificates (email, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_rdc_hash
    ON charvak_readiness_certificates (certificate_hash);

CREATE INDEX IF NOT EXISTS idx_rdc_assessment
    ON charvak_readiness_certificates (assessment_id);
