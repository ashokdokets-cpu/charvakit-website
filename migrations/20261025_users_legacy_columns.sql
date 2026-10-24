-- 20261025_users_legacy_columns.sql
-- Formalizes columns that were added manually to prod
-- before migration tracking was in place.
-- Idempotent: safe to run on both prod and local.

-- verified: whether the user has confirmed their email
ALTER TABLE users ADD COLUMN IF NOT EXISTS verified BOOLEAN DEFAULT FALSE;

-- id: legacy auto-increment column (user_id TEXT is primary key)
ALTER TABLE users ADD COLUMN IF NOT EXISTS id SERIAL;

-- google_oauth_id + auth_provider: Google OAuth support
ALTER TABLE users ADD COLUMN IF NOT EXISTS google_oauth_id TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider TEXT DEFAULT 'password';

-- Case-insensitive email uniqueness
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_lower
    ON users (LOWER(email))
    WHERE email IS NOT NULL;