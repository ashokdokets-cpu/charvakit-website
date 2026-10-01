-- 20260930_legacy_shift_tier.sql
-- Legacy-Shift migration tier: full file-by-file migration plan.

CREATE TABLE IF NOT EXISTS charvak_legacy_shift_reports (
    report_id      TEXT PRIMARY KEY,
    email          TEXT NOT NULL,
    code_preview   TEXT,
    analysis_json  JSONB,
    plan_json      JSONB,
    credits_used   INTEGER NOT NULL DEFAULT 0,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_legacy_shift_email ON charvak_legacy_shift_reports (email, created_at DESC);
