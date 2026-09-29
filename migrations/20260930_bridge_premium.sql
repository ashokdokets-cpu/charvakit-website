-- 20260930_bridge_premium.sql
-- Bridge Premium Calculator: multi-year revenue projections + sensitivity analysis
-- for universities. One-time purchase, 1000 credits.

CREATE TABLE IF NOT EXISTS charvak_bridge_premium_reports (
    report_id        TEXT PRIMARY KEY,
    email            TEXT NOT NULL,
    students         INTEGER,
    placement_rate   NUMERIC,
    avg_salary       NUMERIC,
    isa_percent      NUMERIC,
    isa_months       INTEGER,
    report_json      JSONB,
    credits_used     INTEGER NOT NULL DEFAULT 0,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bridge_premium_email
    ON charvak_bridge_premium_reports (email, created_at DESC);
