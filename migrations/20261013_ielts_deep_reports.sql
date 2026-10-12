-- ============================================================
-- Session 43-A1.7: IELTS Deep Report micro-paywall
-- ============================================================
-- Free tier: band score + sub-bands + basic feedback (existing)
-- Paid tier (Rs 99): deep diagnostic + PDF + email

-- 1. Persist the raw essay/transcripts at free-eval time so the
--    paid report uses the exact text that was scored (tamper-proof).
ALTER TABLE charvak_ielts_sessions
    ADD COLUMN IF NOT EXISTS responses_json JSONB;

-- 2. New table for the paid deep reports.
CREATE TABLE IF NOT EXISTS charvak_ielts_deep_reports (
    report_id         TEXT PRIMARY KEY,
    session_id        TEXT NOT NULL,                -- FK to charvak_ielts_sessions
    email             TEXT NOT NULL,
    test_type         TEXT NOT NULL,                -- 'writing' | 'speaking'
    currency          TEXT NOT NULL DEFAULT 'INR',
    amount_local      NUMERIC(12,2) NOT NULL DEFAULT 99,
    tier              TEXT,
    gateway           TEXT NOT NULL,                -- 'razorpay' | 'paypal'
    razorpay_order_id    TEXT UNIQUE,
    razorpay_payment_id  TEXT UNIQUE,
    paypal_order_id      TEXT UNIQUE,
    status            TEXT NOT NULL DEFAULT 'pending',
    report_json       JSONB,                        -- AI-generated content
    pdf_generated_at  TIMESTAMP,
    email_sent_at     TIMESTAMP,
    error_message     TEXT,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at      TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ielts_deep_reports_email
    ON charvak_ielts_deep_reports (email, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ielts_deep_reports_session
    ON charvak_ielts_deep_reports (session_id);

CREATE INDEX IF NOT EXISTS idx_ielts_deep_reports_payment
    ON charvak_ielts_deep_reports (razorpay_payment_id);