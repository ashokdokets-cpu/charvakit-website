-- 20261004_premium_reports.sql
-- Session 16 Commit 2: Premium Report product (Rs 199 / 400 credits).
-- Generic report generator; report_type = auditbot | lock_in_breaker | skill_twin.

CREATE TABLE IF NOT EXISTS charvak_premium_reports (
    report_id       TEXT PRIMARY KEY,
    email           TEXT NOT NULL,
    report_type     TEXT NOT NULL,
    source_id       TEXT,
    source_data     JSONB NOT NULL DEFAULT '{}'::jsonb,
    title           TEXT,
    subtitle        TEXT,
    content_json    JSONB NOT NULL DEFAULT '{}'::jsonb,
    credits_used    INTEGER NOT NULL DEFAULT 400,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_premium_reports_email
    ON charvak_premium_reports (email, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_premium_reports_type
    ON charvak_premium_reports (report_type, created_at DESC);