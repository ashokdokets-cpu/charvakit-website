-- ============================================================================
-- Charvak IT Consulting - Profile & Network Persistence (Tier 3, Session D/4)
-- Migration: 20260918_profile_network_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist master profiles (JSONB), alumni connections, network tracker.
--            referral_matches is a dead field (never written) - no table.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_network_tracker;
--            DROP TABLE IF EXISTS charvak_alumni_connections;
--            DROP TABLE IF EXISTS charvak_master_profiles;
-- ============================================================================

-- Master profile: whole dict stored as JSONB so dict.update() semantics are preserved
CREATE TABLE IF NOT EXISTS charvak_master_profiles (
    profile_id   TEXT PRIMARY KEY,
    email        TEXT UNIQUE NOT NULL,
    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_master_profiles_email ON charvak_master_profiles(email);

CREATE TABLE IF NOT EXISTS charvak_alumni_connections (
    connection_id  TEXT PRIMARY KEY,
    university     TEXT,
    name           TEXT,
    email          TEXT,
    company        TEXT,
    role           TEXT,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_alumni_university ON charvak_alumni_connections(university);
CREATE INDEX IF NOT EXISTS idx_alumni_company    ON charvak_alumni_connections(company);
CREATE INDEX IF NOT EXISTS idx_alumni_email      ON charvak_alumni_connections(email);

CREATE TABLE IF NOT EXISTS charvak_network_tracker (
    track_id          TEXT PRIMARY KEY,
    email             TEXT NOT NULL,
    connection_name   TEXT,
    company           TEXT,
    status            TEXT DEFAULT 'pending',
    tracked_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ntracker_email   ON charvak_network_tracker(email);
CREATE INDEX IF NOT EXISTS idx_ntracker_company ON charvak_network_tracker(company);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================