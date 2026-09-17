-- ============================================================================
-- Charvak IT Consulting - Dynamic Role Persistence (Tier 3, Session F/4)
-- Migration: 20260918_dynamic_role_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist user role-analysis profiles + custom role catalog.
--            Base 15-role catalog stays in code.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_dynamic_custom_roles;
--            DROP TABLE IF EXISTS charvak_dynamic_role_profiles;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_dynamic_role_profiles (
    email             TEXT PRIMARY KEY,
    skills            JSONB DEFAULT '[]'::jsonb,
    interests         JSONB DEFAULT '[]'::jsonb,
    experience_level  TEXT DEFAULT 'fresher',
    recommendations   JSONB DEFAULT '[]'::jsonb,
    ai_insights       JSONB DEFAULT '[]'::jsonb,
    analyzed_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_dynrole_profiles_level ON charvak_dynamic_role_profiles(experience_level);

CREATE TABLE IF NOT EXISTS charvak_dynamic_custom_roles (
    role_id         TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    category        TEXT DEFAULT 'Custom',
    skills          JSONB DEFAULT '[]'::jsonb,
    tools           JSONB DEFAULT '[]'::jsonb,
    certifications  JSONB DEFAULT '[]'::jsonb,
    created_by      TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_dynrole_custom_created_by ON charvak_dynamic_custom_roles(created_by);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================