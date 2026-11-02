-- Migration: 20261102_cert_identity_prod
-- Purpose: Apply Session 103a identity columns that never made it to production
-- Idempotent. Safe to re-run.

ALTER TABLE charvak_career_certifications
    ADD COLUMN IF NOT EXISTS candidate_name TEXT,
    ADD COLUMN IF NOT EXISTS candidate_email_masked TEXT,
    ADD COLUMN IF NOT EXISTS candidate_email_fingerprint TEXT,
    ADD COLUMN IF NOT EXISTS attempt_number INTEGER DEFAULT 1,
    ADD COLUMN IF NOT EXISTS attempt_max INTEGER DEFAULT 3,
    ADD COLUMN IF NOT EXISTS identity_signature TEXT;

-- Also ensure the coding/SQL columns from Session 84d are present
ALTER TABLE charvak_career_certifications
    ADD COLUMN IF NOT EXISTS format TEXT,
    ADD COLUMN IF NOT EXISTS language TEXT,
    ADD COLUMN IF NOT EXISTS database_name TEXT,
    ADD COLUMN IF NOT EXISTS task_classes JSONB,
    ADD COLUMN IF NOT EXISTS runtime_info TEXT,
    ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;

-- Backfill expires_at for existing certs (365 days from issue)
UPDATE charvak_career_certifications
SET expires_at = issued_at + INTERVAL '365 days'
WHERE expires_at IS NULL AND issued_at IS NOT NULL;

-- Backfill identity columns with safe defaults for existing certs
UPDATE charvak_career_certifications
SET candidate_name = 'Candidate'
WHERE candidate_name IS NULL;

UPDATE charvak_career_certifications
SET candidate_email_masked = email
WHERE candidate_email_masked IS NULL;

UPDATE charvak_career_certifications
SET attempt_number = 1
WHERE attempt_number IS NULL;

UPDATE charvak_career_certifications
SET attempt_max = 3
WHERE attempt_max IS NULL;

-- Index for the new columns
CREATE INDEX IF NOT EXISTS idx_cert_identity_fingerprint
    ON charvak_career_certifications (candidate_email_fingerprint)
    WHERE candidate_email_fingerprint IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_cert_expires
    ON charvak_career_certifications (expires_at)
    WHERE expires_at IS NOT NULL;