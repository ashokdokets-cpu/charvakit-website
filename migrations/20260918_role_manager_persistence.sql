-- ============================================================================
-- Charvak IT Consulting - Role Manager Persistence (Tier 3, Session J/4)
-- Migration: 20260918_role_manager_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist role_manager's custom_roles dict.
--            NOTE: this overlaps with charvak_dynamic_custom_roles (Session F/4).
--            Keeping them separate per Session J scope; consolidation is a
--            future Session K/I task.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_role_manager_custom_roles;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_role_manager_custom_roles (
    role_id       TEXT PRIMARY KEY,
    name          TEXT,
    category      TEXT,
    skills        JSONB DEFAULT '[]'::jsonb,
    description   TEXT DEFAULT '',
    skills_count  INTEGER DEFAULT 0,
    status        TEXT DEFAULT 'active',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_rm_roles_category ON charvak_role_manager_custom_roles(category);
CREATE INDEX IF NOT EXISTS idx_rm_roles_status   ON charvak_role_manager_custom_roles(status);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================