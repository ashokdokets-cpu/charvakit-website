-- ============================================================================
-- Charvak IT Consulting - Payment Engine Log Persistence (Session E-verify)
-- Migration: 20260918_payment_engine_log.sql
-- Created:   2026-09-18
-- Purpose:   Persist the payment_engine's in-memory log so get_all_payments()
--            and get_payment_status() survive restarts.
--            Durable source of truth remains charvak_course_payments and
--            charvak_credit_purchases; this is the engine's own audit log.
-- Design:    raw_data JSONB holds the entire original dict so reads are
--            lossless (the dict shapes vary per gateway: razorpay has
--            'receipt', paypal has 'custom_id'/'description', UPI has 'txn_id').
--            status and amount are also top-level columns for indexing/queries.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_payment_log;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_payment_log (
    order_id     TEXT PRIMARY KEY,
    status       TEXT,
    amount       NUMERIC(12,2) DEFAULT 0,
    raw_data     JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_payment_log_status ON charvak_payment_log(status);
CREATE INDEX IF NOT EXISTS idx_payment_log_created ON charvak_payment_log(created_at);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================