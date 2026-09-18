-- ============================================================================
-- Charvak IT Consulting - AI Question Generator Persistence (Tier 3, Session J/6)
-- Migration: 20260918_ai_question_generator_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist question_cache + daily_ai_usage.
--            used_questions is a dead field (declared, never used) - no table.
--            topic_fallback / variation_prefixes stay in code (static).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_aiqg_daily_usage;
--            DROP TABLE IF EXISTS charvak_aiqg_question_cache;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_aiqg_question_cache (
    cache_key    TEXT PRIMARY KEY,
    questions    JSONB NOT NULL DEFAULT '[]'::jsonb,
    timestamp    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_aiqg_cache_ts ON charvak_aiqg_question_cache(timestamp);

CREATE TABLE IF NOT EXISTS charvak_aiqg_daily_usage (
    email        TEXT NOT NULL,
    usage_date   DATE NOT NULL,
    count        INTEGER DEFAULT 0,
    PRIMARY KEY (email, usage_date)
);
CREATE INDEX IF NOT EXISTS idx_aiqg_usage_date ON charvak_aiqg_daily_usage(usage_date);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================