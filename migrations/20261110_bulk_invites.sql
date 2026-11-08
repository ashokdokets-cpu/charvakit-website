-- 20261110_bulk_invites.sql
ALTER TABLE charvak_college_invites
    ADD COLUMN IF NOT EXISTS last_email_sent_at TIMESTAMPTZ;

ALTER TABLE charvak_college_invites
    ADD COLUMN IF NOT EXISTS magic_token TEXT;

CREATE INDEX IF NOT EXISTS idx_invites_token
    ON charvak_college_invites (magic_token) WHERE magic_token IS NOT NULL;