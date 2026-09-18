-- ============================================================================
-- Charvak IT Consulting - ATS Persistence (Tier 3, Session B/1)
-- Migration: 20260918_ats_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist ATS integrations + sync log.
--            ATSProvider constants stay in code (static).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_ats_sync_log;
--            DROP TABLE IF EXISTS charvak_ats_integrations;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_ats_integrations (
    integration_id   TEXT PRIMARY KEY,
    provider         TEXT,
    api_key_prefix   TEXT,
    base_url         TEXT DEFAULT '',
    company_name     TEXT,
    direction        TEXT DEFAULT 'bidirectional',
    status           TEXT DEFAULT 'connected',
    connected_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ats_integrations_provider ON charvak_ats_integrations(provider);
CREATE INDEX IF NOT EXISTS idx_ats_integrations_status   ON charvak_ats_integrations(status);

CREATE TABLE IF NOT EXISTS charvak_ats_sync_log (
    sync_id      TEXT PRIMARY KEY,
    direction    TEXT,
    provider     TEXT,
    jobs_count   INTEGER DEFAULT 0,
    details      JSONB NOT NULL DEFAULT '{}'::jsonb,
    synced_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ats_sync_direction ON charvak_ats_sync_log(direction);
CREATE INDEX IF NOT EXISTS idx_ats_sync_provider  ON charvak_ats_sync_log(provider);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================