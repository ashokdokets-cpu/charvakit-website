-- 20260930_team_subscriptions.sql
-- Team Dashboard: Growing Team Pro tier (Rs 2,999/mo).
-- One subscription row per admin email. 30-day expiry.

CREATE TABLE IF NOT EXISTS charvak_team_subscriptions (
    email          TEXT PRIMARY KEY,
    tier           TEXT NOT NULL DEFAULT 'pro',
    started_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at     TIMESTAMP NOT NULL,
    max_members    INTEGER NOT NULL DEFAULT 20,
    credits_used   INTEGER NOT NULL DEFAULT 0,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_team_subs_expires ON charvak_team_subscriptions (expires_at);
