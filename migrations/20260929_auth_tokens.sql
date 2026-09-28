-- 20260929_auth_tokens.sql
-- Persist auth tokens so uvicorn restarts (dev) and Render restarts (prod)
-- do not invalidate every logged-in session.
--
-- Idempotent: safe to re-run.

CREATE TABLE IF NOT EXISTS charvak_auth_tokens (
    token        TEXT PRIMARY KEY,
    user_id      TEXT,
    email        TEXT NOT NULL,
    role         TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at   TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_charvak_auth_tokens_email
    ON charvak_auth_tokens (email);

CREATE INDEX IF NOT EXISTS idx_charvak_auth_tokens_expires
    ON charvak_auth_tokens (expires_at);

-- Optional cleanup helper (not scheduled, called on-demand)
-- DELETE FROM charvak_auth_tokens WHERE expires_at < NOW();
