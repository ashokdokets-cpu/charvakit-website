-- ============================================================================
-- Charvak IT Consulting - Monitor Service Persistence (Tier 3, Session J/5)
-- Migration: 20260918_monitor_service_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist monitored_sites + alert_history (module-level dicts in
--            the original). Preserves the async monitor API on top of Postgres.
--            SiteMonitor class stays as-is (issues repopulated per check).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_monitor_alert_history;
--            DROP TABLE IF EXISTS charvak_monitor_sites;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_monitor_sites (
    url               TEXT PRIMARY KEY,
    name              TEXT,
    interval_seconds  INTEGER DEFAULT 300,
    status            TEXT DEFAULT 'unknown',
    last_check        TIMESTAMP,
    issues            JSONB DEFAULT '[]'::jsonb,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_monitor_sites_status ON charvak_monitor_sites(status);

CREATE TABLE IF NOT EXISTS charvak_monitor_alert_history (
    alert_id     TEXT PRIMARY KEY,
    url          TEXT NOT NULL,
    name         TEXT,
    issues       JSONB DEFAULT '[]'::jsonb,
    checked_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_monitor_alerts_url     ON charvak_monitor_alert_history(url);
CREATE INDEX IF NOT EXISTS idx_monitor_alerts_checked ON charvak_monitor_alert_history(checked_at);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================