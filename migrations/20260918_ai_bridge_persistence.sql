-- ============================================================================
-- Charvak IT Consulting - AI Bridge Persistence (Tier 3, Session H/6)
-- Migration: 20260918_ai_bridge_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist AI assessment sessions + premium reports.
--            ROLES / INDUSTRIES / LEVELS stay in code (static).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_ai_bridge_premium_reports;
--            DROP TABLE IF EXISTS charvak_ai_bridge_sessions;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_ai_bridge_sessions (
    session_id   TEXT PRIMARY KEY,
    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_aib_sessions_started ON charvak_ai_bridge_sessions(started_at);

CREATE TABLE IF NOT EXISTS charvak_ai_bridge_premium_reports (
    premium_id    TEXT PRIMARY KEY,
    session_id    TEXT NOT NULL,
    data          JSONB NOT NULL DEFAULT '{}'::jsonb,
    price         INTEGER DEFAULT 99,
    purchased_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_aib_premium_session ON charvak_ai_bridge_premium_reports(session_id);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================