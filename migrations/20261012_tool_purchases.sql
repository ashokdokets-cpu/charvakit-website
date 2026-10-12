-- charvak_tool_purchases
-- Session 43-A1.6: one-off tool runs paid via Razorpay at Rs 99.

CREATE TABLE IF NOT EXISTS charvak_tool_purchases (
    purchase_id            TEXT PRIMARY KEY,
    email                  TEXT,                    -- optional; user may be anonymous
    tool_slug              TEXT NOT NULL,           -- e.g. 'resume_roast'
    tool_name              TEXT,                    -- human-readable, e.g. 'Resume Roast'
    amount_inr             INTEGER NOT NULL DEFAULT 99,
    currency               TEXT NOT NULL DEFAULT 'INR',
    razorpay_order_id      TEXT UNIQUE,
    razorpay_payment_id    TEXT UNIQUE,             -- idempotency key
    status                 TEXT NOT NULL DEFAULT 'pending',
    result_json            JSONB,
    error_message          TEXT,
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at           TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tool_purchases_email
    ON charvak_tool_purchases (email, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_tool_purchases_tool
    ON charvak_tool_purchases (tool_slug, created_at DESC);