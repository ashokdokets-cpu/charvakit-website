-- ============================================================================
-- Charvak IT Consulting - Indian Language AI Persistence (Tier 3, Session J/3)
-- Migration: 20260918_indian_language_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist Indian-language assessments.
--            translations is a dead field (never written) - no table.
--            INDIAN_LANGUAGES + question catalogs stay in code (static).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_lang_ai_assessments;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_lang_ai_assessments (
    assessment_id     TEXT PRIMARY KEY,
    language          TEXT,
    native_name       TEXT,
    skill             TEXT,
    difficulty        TEXT DEFAULT 'Beginner',
    questions         JSONB DEFAULT '[]'::jsonb,
    total_questions   INTEGER DEFAULT 0,
    passing_score     INTEGER DEFAULT 70,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_lang_ai_language   ON charvak_lang_ai_assessments(language);
CREATE INDEX IF NOT EXISTS idx_lang_ai_skill      ON charvak_lang_ai_assessments(skill);
CREATE INDEX IF NOT EXISTS idx_lang_ai_created    ON charvak_lang_ai_assessments(created_at);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================