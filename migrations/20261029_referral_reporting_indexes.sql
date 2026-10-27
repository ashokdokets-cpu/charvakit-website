-- ============================================================
-- Session 97 — Admin reporting indexes
-- Idempotent. Reporting query performance + aggregations.
-- ============================================================

-- Existing indexes from Session 92 cover the basics.
-- Add a few for the admin report queries.

CREATE INDEX IF NOT EXISTS idx_conv_referrer_created
    ON charvak_referral_conversions (referrer_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conv_created_status
    ON charvak_referral_conversions (created_at DESC, status);

CREATE INDEX IF NOT EXISTS idx_payout_referrer_paid
    ON charvak_payout_requests (referrer_id, paid_at DESC)
    WHERE status = 'paid';

CREATE INDEX IF NOT EXISTS idx_recurring_billing_status
    ON charvak_recurring_commissions (billing_period, status);

-- Verify no schema changes needed for reporting
-- (payment_reference on conversions already exists from Session 92)