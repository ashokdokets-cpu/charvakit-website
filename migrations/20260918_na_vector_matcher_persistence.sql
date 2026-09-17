-- ============================================================================
-- Charvak IT Consulting - NA Vector Matcher Persistence (Tier 3, Session G/1)
-- Migration: 20260918_na_vector_matcher_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist match history to Postgres.
--            SKILL_EMBEDDINGS stays in code (static).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_na_match_history;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_na_match_history (
    match_id         TEXT PRIMARY KEY,
    candidate_id     TEXT,
    matches_count    INTEGER DEFAULT 0,
    top_score        INTEGER DEFAULT 0,
    matched_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_na_match_candidate ON charvak_na_match_history(candidate_id);
CREATE INDEX IF NOT EXISTS idx_na_match_time      ON charvak_na_match_history(matched_at);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================