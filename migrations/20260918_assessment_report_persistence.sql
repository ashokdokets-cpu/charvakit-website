-- ============================================================================
-- Charvak IT Consulting - Assessment Report Persistence (Tier 3, Session H/1)
-- Migration: 20260918_assessment_report_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist assessment reports + verification IDs.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_assessment_reports;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_assessment_reports (
    report_id          TEXT PRIMARY KEY,
    verification_id    TEXT UNIQUE NOT NULL,
    assessment_type    TEXT DEFAULT 'general',
    candidate_name     TEXT,
    candidate_email    TEXT,
    employer_email     TEXT DEFAULT '',
    score              NUMERIC(5,2) DEFAULT 0,
    passed             BOOLEAN DEFAULT FALSE,
    skills_tested      JSONB DEFAULT '[]'::jsonb,
    total_questions    INTEGER DEFAULT 0,
    correct_answers    INTEGER DEFAULT 0,
    strengths          JSONB DEFAULT '[]'::jsonb,
    improvements       JSONB DEFAULT '[]'::jsonb,
    recommendations    JSONB DEFAULT '[]'::jsonb,
    generated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_asr_candidate_email ON charvak_assessment_reports(candidate_email);
CREATE INDEX IF NOT EXISTS idx_asr_verification    ON charvak_assessment_reports(verification_id);
CREATE INDEX IF NOT EXISTS idx_asr_passed          ON charvak_assessment_reports(passed);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================