-- 20261024_google_oauth.sql
-- Session 82 — Google OAuth infrastructure
-- Idempotent. Safe to run multiple times.

ALTER TABLE users ADD COLUMN IF NOT EXISTS google_oauth_id TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider TEXT DEFAULT 'password';

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_oauth_id
    ON users (google_oauth_id)
    WHERE google_oauth_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_lower
    ON users (LOWER(email))
    WHERE email IS NOT NULL;