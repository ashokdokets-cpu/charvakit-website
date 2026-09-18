-- ============================================================================
-- Charvak IT Consulting - Company Content Persistence (Tier 3, Session H/7)
-- Migration: 20260918_company_content_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist per-user per-company placement progress (running aggregates).
--            Company catalog stays in code (static 3-company structure).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_company_content_progress;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_company_content_progress (
    email               TEXT NOT NULL,
    company_id          TEXT NOT NULL,
    sections_completed  INTEGER DEFAULT 0,
    total_score         NUMERIC(10,2) DEFAULT 0,
    mock_tests          INTEGER DEFAULT 0,
    started_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (email, company_id)
);
CREATE INDEX IF NOT EXISTS idx_ccp_email   ON charvak_company_content_progress(email);
CREATE INDEX IF NOT EXISTS idx_ccp_company ON charvak_company_content_progress(company_id);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================