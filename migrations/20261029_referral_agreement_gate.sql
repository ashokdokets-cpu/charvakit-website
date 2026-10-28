-- ============================================================
-- Session 99 — Gate referral link behind agreement acceptance
-- ============================================================

ALTER TABLE charvak_referrer_accounts
    ADD COLUMN IF NOT EXISTS code_activated BOOLEAN DEFAULT FALSE;

-- Grandfather existing referrers who already accepted v0.9 (test accounts)
UPDATE charvak_referrer_accounts
SET code_activated = TRUE
WHERE agreement_accepted_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_referrer_code_activated
    ON charvak_referrer_accounts (referral_code)
    WHERE code_activated = TRUE;