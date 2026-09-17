-- ============================================================================
-- Charvak IT Consulting - Final Year Project Persistence (Tier 3, Session E/4)
-- Migration: 20260918_final_year_project_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist FYP subscriptions to Postgres.
--            AI methods (topic/proposal/docs/viva) are stateless; no table needed.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_fyp_subscriptions;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_fyp_subscriptions (
    subscription_id  TEXT PRIMARY KEY,
    email            TEXT NOT NULL,
    plan             TEXT NOT NULL DEFAULT 'free',
    price            INTEGER DEFAULT 0,
    status           TEXT NOT NULL DEFAULT 'active',
    subscribed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_fyp_subs_email  ON charvak_fyp_subscriptions(email);
CREATE INDEX IF NOT EXISTS idx_fyp_subs_plan   ON charvak_fyp_subscriptions(plan);
CREATE INDEX IF NOT EXISTS idx_fyp_subs_status ON charvak_fyp_subscriptions(status);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================