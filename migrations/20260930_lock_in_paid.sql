-- 20260930_lock_in_paid.sql
-- Lock-In Breaker paid tiers: one-time migration + continuous protection.

CREATE TABLE IF NOT EXISTS charvak_lock_in_engagements (
    engagement_id  TEXT PRIMARY KEY,
    email          TEXT NOT NULL,
    tier           TEXT NOT NULL,         -- 'migration' | 'protection'
    audit_id       TEXT,
    provider       TEXT,
    monthly_spend  NUMERIC,
    services_json  JSONB,
    plan_json      JSONB,
    expires_at     TIMESTAMP,
    credits_used   INTEGER NOT NULL DEFAULT 0,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lock_in_engagements_email
    ON charvak_lock_in_engagements (email, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lock_in_engagements_tier
    ON charvak_lock_in_engagements (email, tier, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lock_in_engagements_audit
    ON charvak_lock_in_engagements (audit_id);
