-- ============================================================================
-- Charvak IT Consulting - Outreach Engine Persistence (Tier 3, Session F/2)
-- Migration: 20260918_outreach_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist cold emails, Gmail syncs, auto-tracked apps, premium users.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_outreach_premium_users;
--            DROP TABLE IF EXISTS charvak_outreach_auto_tracked;
--            DROP TABLE IF EXISTS charvak_outreach_email_syncs;
--            DROP TABLE IF EXISTS charvak_outreach_cold_emails;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_outreach_cold_emails (
    email_id              TEXT PRIMARY KEY,
    company               TEXT,
    hiring_manager        TEXT,
    domain                TEXT,
    likely_emails         JSONB DEFAULT '[]'::jsonb,
    confidence            TEXT,
    cold_email_template   TEXT,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_outreach_ce_company ON charvak_outreach_cold_emails(company);
CREATE INDEX IF NOT EXISTS idx_outreach_ce_domain  ON charvak_outreach_cold_emails(domain);

CREATE TABLE IF NOT EXISTS charvak_outreach_email_syncs (
    sync_id       TEXT PRIMARY KEY,
    email         TEXT NOT NULL,
    sync_type     TEXT DEFAULT 'all',
    status        TEXT DEFAULT 'connected',
    connected_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_outreach_syncs_email ON charvak_outreach_email_syncs(email);

CREATE TABLE IF NOT EXISTS charvak_outreach_auto_tracked (
    track_id    TEXT PRIMARY KEY,
    email       TEXT NOT NULL,
    company     TEXT,
    role        TEXT,
    status      TEXT DEFAULT 'applied',
    tracked_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_outreach_tracked_email   ON charvak_outreach_auto_tracked(email);
CREATE INDEX IF NOT EXISTS idx_outreach_tracked_company ON charvak_outreach_auto_tracked(company);

CREATE TABLE IF NOT EXISTS charvak_outreach_premium_users (
    subscription_id  TEXT PRIMARY KEY,
    email            TEXT NOT NULL,
    plan             TEXT DEFAULT 'basic',
    price            INTEGER DEFAULT 0,
    features         JSONB DEFAULT '[]'::jsonb,
    subscribed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_outreach_premium_email ON charvak_outreach_premium_users(email);
CREATE INDEX IF NOT EXISTS idx_outreach_premium_plan  ON charvak_outreach_premium_users(plan);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================