-- ============================================================================
-- Charvak IT Consulting - Training Mapping Persistence (Tier 3, Session H/5)
-- Migration: 20260918_training_mapping_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist training plans (whole dict as JSONB) keyed by email.
--            skill_matrix + insights stay in code (static).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_training_plans;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_training_plans (
    email        TEXT PRIMARY KEY,
    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_training_created ON charvak_training_plans(created_at);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================