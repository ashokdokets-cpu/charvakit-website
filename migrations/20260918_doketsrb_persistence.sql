-- ============================================================================
-- Charvak IT Consulting - DoketsRB Integration Persistence (Tier 3, Session J/1)
-- Migration: 20260918_doketsrb_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist bundle subscriptions (email + bundle).
--            FEATURES / BUNDLES stay in code (static catalogs).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_doketsrb_bundle_subs;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_doketsrb_bundle_subs (
    subscription_id  TEXT PRIMARY KEY,
    email            TEXT,
    bundle           TEXT,
    bundle_name      TEXT,
    price            NUMERIC(10,2) DEFAULT 0,
    includes         JSONB DEFAULT '[]'::jsonb,
    subscribed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_doketsrb_subs_email  ON charvak_doketsrb_bundle_subs(email);
CREATE INDEX IF NOT EXISTS idx_doketsrb_subs_bundle ON charvak_doketsrb_bundle_subs(bundle);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================