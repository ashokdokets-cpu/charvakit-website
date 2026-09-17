-- ============================================================================
-- Charvak IT Consulting - Badge Engine Persistence (Tier 3, Session D/1)
-- Migration: 20260918_badge_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist issued badges + verification metadata.
--            certifications is a dead field (never written) - no table.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_badges;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_badges (
    badge_id           TEXT PRIMARY KEY,
    badge_name         TEXT,
    level              TEXT,
    color              TEXT DEFAULT '#3ba591',
    user_name          TEXT,
    user_email         TEXT NOT NULL,
    score              INTEGER,
    skills             JSONB DEFAULT '[]'::jsonb,
    badge_type         TEXT,
    issued_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until        TIMESTAMP,
    verification_hash  TEXT,
    share_url          TEXT,
    linkedin_url       TEXT
);
CREATE INDEX IF NOT EXISTS idx_badges_user_email ON charvak_badges(user_email);
CREATE INDEX IF NOT EXISTS idx_badges_level      ON charvak_badges(level);
CREATE INDEX IF NOT EXISTS idx_badges_type       ON charvak_badges(badge_type);
CREATE INDEX IF NOT EXISTS idx_badges_valid      ON charvak_badges(valid_until);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================