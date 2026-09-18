-- ============================================================================
-- Charvak IT Consulting - Chatbot Persistence (Tier 3, Session H/3)
-- Migration: 20260918_chatbot_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist chat sessions + full message history as JSONB.
--            FAQ catalog stays in code (static 10-item list).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_chatbot_sessions;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_chatbot_sessions (
    session_id   TEXT PRIMARY KEY,
    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_chatbot_created ON charvak_chatbot_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_chatbot_updated ON charvak_chatbot_sessions(updated_at);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================