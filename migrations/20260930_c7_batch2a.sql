-- 20260930_c7_batch2a.sql
-- Batch 2a: 3 new tables for the C7 templates that already have frontends.

-- Geo-Compliance contracts
CREATE TABLE IF NOT EXISTS charvak_geo_compliance_contracts (
    contract_id      TEXT PRIMARY KEY,
    email            TEXT NOT NULL,
    countries_json   JSONB,
    service_type     TEXT,
    contract_json    JSONB,
    credits_used     INTEGER NOT NULL DEFAULT 0,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_geo_contracts_email ON charvak_geo_compliance_contracts (email, created_at DESC);

-- Geo-Compliance global hiring engagements
CREATE TABLE IF NOT EXISTS charvak_geo_compliance_hiring (
    setup_id         TEXT PRIMARY KEY,
    email            TEXT NOT NULL,
    countries_json   JSONB,
    setup_json       JSONB,
    credits_used     INTEGER NOT NULL DEFAULT 0,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_geo_hiring_email ON charvak_geo_compliance_hiring (email, created_at DESC);

-- Reverse-Staffing subscriptions
CREATE TABLE IF NOT EXISTS charvak_reverse_staffing_subscriptions (
    email            TEXT PRIMARY KEY,
    tier             TEXT NOT NULL DEFAULT 'subscription',
    started_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at       TIMESTAMP NOT NULL,
    matches_used     INTEGER NOT NULL DEFAULT 0,
    credits_used     INTEGER NOT NULL DEFAULT 0,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_rev_staff_subs_expires ON charvak_reverse_staffing_subscriptions (expires_at);
