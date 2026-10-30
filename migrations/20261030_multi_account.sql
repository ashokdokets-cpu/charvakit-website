-- Migration: 20261030_multi_account
-- Session 104a: Track account signals for multi-account abuse detection.
-- Idempotent.

CREATE TABLE IF NOT EXISTS charvak_account_signals (
    signal_id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    ip_hash TEXT,
    email_prefix TEXT,
    user_agent TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(email, ip_hash)
);

CREATE INDEX IF NOT EXISTS idx_as_ip
    ON charvak_account_signals (ip_hash)
    WHERE ip_hash IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_as_prefix
    ON charvak_account_signals (email_prefix)
    WHERE email_prefix IS NOT NULL;