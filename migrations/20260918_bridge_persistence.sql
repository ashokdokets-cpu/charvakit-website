-- ============================================================================
-- Charvak IT Consulting - Bridge Engine Persistence (Tier 3, Session H/4)
-- Migration: 20260918_bridge_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist 5-step assessment journey sessions.
--            CATEGORIES, QUESTIONS, THRESHOLD stay in code (static).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_bridge_sessions;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_bridge_sessions (
    session_id    TEXT PRIMARY KEY,
    current_step  INTEGER DEFAULT 1,
    answers       JSONB DEFAULT '{}'::jsonb,
    scores        JSONB DEFAULT '{}'::jsonb,
    readiness     INTEGER DEFAULT 0,
    started_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_bridge_started ON charvak_bridge_sessions(started_at);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================