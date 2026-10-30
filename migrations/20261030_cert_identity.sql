-- Migration: 20261030_cert_identity
-- Purpose: Add identity + attempt tracking columns to career certifications.
-- This is part of Session 103a (abuse protection layer).
--
-- Idempotent. Safe to re-run.

ALTER TABLE charvak_career_certifications
    ADD COLUMN IF NOT EXISTS candidate_name TEXT,
    ADD COLUMN IF NOT EXISTS candidate_email_masked TEXT,
    ADD COLUMN IF NOT EXISTS candidate_email_fingerprint TEXT,
    ADD COLUMN IF NOT EXISTS attempt_number INTEGER DEFAULT 1,
    ADD COLUMN IF NOT EXISTS attempt_max INTEGER DEFAULT 3,
    ADD COLUMN IF NOT EXISTS identity_signature TEXT;

-- Index for identity lookups (recruiter verifying by fingerprint)
CREATE INDEX IF NOT EXISTS idx_cert_identity_fingerprint
    ON charvak_career_certifications (candidate_email_fingerprint)
    WHERE candidate_email_fingerprint IS NOT NULL;

-- Index for attempt count queries
CREATE INDEX IF NOT EXISTS idx_cert_attempts
    ON charvak_career_certifications (email, attempt_number)
    WHERE attempt_number IS NOT NULL;