-- migrations/20260919_outreach_unique_email.sql
-- K/7: Add UNIQUE constraints on email for outreach tables
-- Prevents duplicate subscriptions/syncs per email.

-- Clean up any existing duplicates (keep most recent)
DELETE FROM charvak_outreach_email_syncs a
USING charvak_outreach_email_syncs b
WHERE a.email = b.email
  AND a.connected_at < b.connected_at;

DELETE FROM charvak_outreach_premium_users a
USING charvak_outreach_premium_users b
WHERE a.email = b.email
  AND a.subscribed_at < b.subscribed_at;

-- Add UNIQUE indexes (idempotent)
CREATE UNIQUE INDEX IF NOT EXISTS uq_outreach_email_syncs_email
    ON charvak_outreach_email_syncs(email);

CREATE UNIQUE INDEX IF NOT EXISTS uq_outreach_premium_users_email
    ON charvak_outreach_premium_users(email);