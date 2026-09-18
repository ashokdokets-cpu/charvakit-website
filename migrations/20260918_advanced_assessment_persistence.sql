-- ============================================================================
-- Charvak IT Consulting - Advanced Assessment Persistence (Tier 3, Session H/8)
-- Migration: 20260918_advanced_assessment_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist AI sessions, mock drives, skill-gap analyses.
--            user_scores is a dead field (never written) - no table.
--            assessments / training_modules catalogs stay in code (static).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_advanced_skill_gaps;
--            DROP TABLE IF EXISTS charvak_advanced_mock_drives;
--            DROP TABLE IF EXISTS charvak_advanced_ai_sessions;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_advanced_ai_sessions (
    session_id   TEXT PRIMARY KEY,
    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_adv_sessions_started ON charvak_advanced_ai_sessions(started_at);

CREATE TABLE IF NOT EXISTS charvak_advanced_mock_drives (
    drive_id     TEXT PRIMARY KEY,
    email        TEXT,
    company      TEXT,
    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_adv_drives_email   ON charvak_advanced_mock_drives(email);
CREATE INDEX IF NOT EXISTS idx_adv_drives_company ON charvak_advanced_mock_drives(company);

CREATE TABLE IF NOT EXISTS charvak_advanced_skill_gaps (
    email        TEXT PRIMARY KEY,
    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
    analyzed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_adv_skill_gaps_analyzed ON charvak_advanced_skill_gaps(analyzed_at);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================