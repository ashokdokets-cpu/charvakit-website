-- ============================================================
-- Payout requests (Session 94 — manual flow)
-- Idempotent, safe to re-run.
-- ============================================================

CREATE TABLE IF NOT EXISTS charvak_payout_requests (
    payout_id TEXT PRIMARY KEY,
    referrer_id TEXT NOT NULL REFERENCES charvak_referrer_accounts(referrer_id),
    amount_inr INTEGER NOT NULL,
    amount_local NUMERIC(10,2),
    currency TEXT DEFAULT 'INR',
    payout_method TEXT NOT NULL,              -- razorpay | paypal | wire | upi
    payout_details JSONB NOT NULL,             -- {upi_id, bank_account, paypal_email, etc}
    status TEXT DEFAULT 'requested',           -- requested | approved | processing | paid | rejected | refunded
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by TEXT,
    approved_at TIMESTAMP,
    paid_at TIMESTAMP,
    payment_reference TEXT,                    -- UTR / PayPal transaction ID
    admin_notes TEXT,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_payout_ref ON charvak_payout_requests(referrer_id);
CREATE INDEX IF NOT EXISTS idx_payout_status ON charvak_payout_requests(status);
CREATE INDEX IF NOT EXISTS idx_payout_time ON charvak_payout_requests(requested_at);
CREATE INDEX IF NOT EXISTS idx_payout_referrer_status ON charvak_payout_requests(referrer_id, status);

-- Also add payment method fields to referrer account (if not present)
ALTER TABLE charvak_referrer_accounts
    ADD COLUMN IF NOT EXISTS payout_method TEXT,
    ADD COLUMN IF NOT EXISTS payout_details JSONB DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS payout_country TEXT DEFAULT 'IN';