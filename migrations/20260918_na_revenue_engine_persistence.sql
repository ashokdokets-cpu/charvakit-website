-- ============================================================================
-- Charvak IT Consulting - NA Revenue Engine Persistence (Tier 3, Session G/3)
-- Migration: 20260918_na_revenue_engine_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist subscriptions + transactions to Postgres.
--            revenue_by_stream and monthly_revenue are derived aggregates.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_na_revenue_transactions;
--            DROP TABLE IF EXISTS charvak_na_revenue_subscriptions;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_na_revenue_subscriptions (
    firm_id         TEXT PRIMARY KEY,
    subscription_id TEXT,
    tier            TEXT,
    bench_limit     INTEGER DEFAULT 0,
    features        JSONB DEFAULT '[]'::jsonb,
    monthly_fee     NUMERIC(12,2) DEFAULT 0,
    status          TEXT DEFAULT 'active',
    start_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    next_billing    TIMESTAMP,
    payment_method  TEXT,
    auto_renew      BOOLEAN DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_na_rev_subs_status ON charvak_na_revenue_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_na_rev_subs_tier   ON charvak_na_revenue_subscriptions(tier);

CREATE TABLE IF NOT EXISTS charvak_na_revenue_transactions (
    transaction_id  TEXT PRIMARY KEY,
    firm_id         TEXT NOT NULL,
    stream          TEXT NOT NULL,
    amount          NUMERIC(12,2) DEFAULT 0,
    details         JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_na_rev_txn_firm    ON charvak_na_revenue_transactions(firm_id);
CREATE INDEX IF NOT EXISTS idx_na_rev_txn_stream  ON charvak_na_revenue_transactions(stream);
CREATE INDEX IF NOT EXISTS idx_na_rev_txn_time    ON charvak_na_revenue_transactions(created_at);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================