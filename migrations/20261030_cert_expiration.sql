-- Migration: 20261030_cert_expiration
-- Session 104b: Add expires_at to certifications. Default 365-day validity.

ALTER TABLE charvak_career_certifications
    ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;

-- Backfill: existing certs expire 365 days from issue date
UPDATE charvak_career_certifications
SET expires_at = issued_at + INTERVAL '365 days'
WHERE expires_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_cert_expires
    ON charvak_career_certifications (expires_at)
    WHERE expires_at IS NOT NULL;