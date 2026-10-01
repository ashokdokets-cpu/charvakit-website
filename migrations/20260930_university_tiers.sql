-- 20260930_university_tiers.sql
-- University subscriptions: Starter / Growth / Enterprise yearly.
-- Credits charged = price_inr / 5.

CREATE TABLE IF NOT EXISTS charvak_university_subscriptions (
    university_id   TEXT PRIMARY KEY,
    admin_email     TEXT NOT NULL,
    tier            TEXT NOT NULL,      -- starter | growth | enterprise
    price_inr       INTEGER,
    credits_used    INTEGER NOT NULL DEFAULT 0,
    started_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at      TIMESTAMP NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_univ_subs_admin ON charvak_university_subscriptions (admin_email, expires_at DESC);
CREATE INDEX IF NOT EXISTS idx_univ_subs_expires ON charvak_university_subscriptions (expires_at);
