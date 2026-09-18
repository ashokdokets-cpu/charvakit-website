-- ============================================================================
-- Charvak IT Consulting - Content Generator Persistence (Tier 3, Session J/2)
-- Migration: 20260918_content_generator_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist used_content dedup set (one row per content key).
--            content_cache is a dead field (declared, never written) - skip.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_content_used_content;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_content_used_content (
    content_key  TEXT PRIMARY KEY,
    used_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_content_used_at ON charvak_content_used_content(used_at);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================