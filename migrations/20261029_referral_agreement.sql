-- ============================================================
-- Session 98 — Referral Agreement acceptance tracking
-- Idempotent, safe to re-run.
-- ============================================================

ALTER TABLE charvak_referrer_accounts
    ADD COLUMN IF NOT EXISTS agreement_version TEXT,
    ADD COLUMN IF NOT EXISTS agreement_accepted_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS agreement_ip_hash TEXT;

CREATE INDEX IF NOT EXISTS idx_referrer_agreement
    ON charvak_referrer_accounts (agreement_accepted_at)
    WHERE agreement_accepted_at IS NOT NULL;

-- Seed existing referrers as grandfathered (accepted version 0.9 pre-agreement)
-- This prevents existing test accounts from being blocked on first payout.
UPDATE charvak_referrer_accounts
SET agreement_version = '0.9',
    agreement_accepted_at = created_at,
    agreement_ip_hash = 'grandfathered'
WHERE agreement_accepted_at IS NULL
  AND created_at < NOW();