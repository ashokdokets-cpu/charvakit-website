-- ============================================================================
-- Charvak IT Consulting - NA Work Auth Persistence (Tier 3, Session G/5)
-- Migration: 20260918_na_work_auth_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist verified candidates to Postgres.
--            Enums, VISA_VALIDITY, CLIENT_RESTRICTIONS, doc maps stay in code.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_na_verified_candidates;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_na_verified_candidates (
    candidate_id            TEXT PRIMARY KEY,
    visa_type               TEXT,
    visa_validity_years     TEXT,
    auth_status             TEXT,
    can_submit              BOOLEAN DEFAULT FALSE,
    compatibility           JSONB DEFAULT '{}'::jsonb,
    required_documents      JSONB DEFAULT '[]'::jsonb,
    compliance_requirements JSONB DEFAULT '[]'::jsonb,
    restrictions            JSONB DEFAULT '[]'::jsonb,
    client_type             TEXT DEFAULT 'corporate',
    verified_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_na_wa_candidates_visa   ON charvak_na_verified_candidates(visa_type);
CREATE INDEX IF NOT EXISTS idx_na_wa_candidates_status ON charvak_na_verified_candidates(auth_status);
CREATE INDEX IF NOT EXISTS idx_na_wa_candidates_submit ON charvak_na_verified_candidates(can_submit);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================