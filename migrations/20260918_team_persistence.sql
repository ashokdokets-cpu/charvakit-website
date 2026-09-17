-- ============================================================================
-- Charvak IT Consulting - Team Engine Persistence (Tier 3, Session E/1)
-- Migration: 20260918_team_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist teams + members to Postgres.
-- Safety:    All CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_team_members;
--            DROP TABLE IF EXISTS charvak_teams;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_teams (
    team_id        TEXT PRIMARY KEY,
    company_name   TEXT,
    admin_email    TEXT,
    admin_name     TEXT,
    member_count   INTEGER DEFAULT 1,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_teams_admin_email ON charvak_teams(admin_email);

CREATE TABLE IF NOT EXISTS charvak_team_members (
    member_id   TEXT PRIMARY KEY,
    team_id     TEXT NOT NULL,
    name        TEXT,
    email       TEXT NOT NULL,
    role        TEXT NOT NULL DEFAULT 'recruiter',
    joined_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, email)
);
CREATE INDEX IF NOT EXISTS idx_team_members_team  ON charvak_team_members(team_id);
CREATE INDEX IF NOT EXISTS idx_team_members_email ON charvak_team_members(email);
CREATE INDEX IF NOT EXISTS idx_team_members_role  ON charvak_team_members(role);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================