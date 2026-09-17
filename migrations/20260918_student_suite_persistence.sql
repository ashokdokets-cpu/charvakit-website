-- ============================================================================
-- Charvak IT Consulting - Student Suite Persistence (Tier 3, Session E/2)
-- Migration: 20260918_student_suite_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist subscriptions + usage tracking to Postgres.
-- Safety:    All CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_student_suite_usage;
--            DROP TABLE IF EXISTS charvak_student_suite_subscriptions;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_student_suite_subscriptions (
    email          TEXT PRIMARY KEY,
    plan           TEXT NOT NULL DEFAULT 'free',
    requests_used  INTEGER DEFAULT 0,
    subscribed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_student_subs_plan ON charvak_student_suite_subscriptions(plan);

CREATE TABLE IF NOT EXISTS charvak_student_suite_usage (
    usage_id       TEXT PRIMARY KEY,
    email          TEXT NOT NULL,
    feature        TEXT NOT NULL,
    count          INTEGER DEFAULT 1,
    last_used_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(email, feature)
);
CREATE INDEX IF NOT EXISTS idx_student_usage_email   ON charvak_student_suite_usage(email);
CREATE INDEX IF NOT EXISTS idx_student_usage_feature ON charvak_student_suite_usage(feature);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================