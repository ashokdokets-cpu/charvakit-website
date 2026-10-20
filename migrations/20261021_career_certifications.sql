-- Session 69: Career Assessment Certifications
-- Standalone credential earned by high scorers on Career Assessments.
-- Distinct from readiness certificates (which are benchmarked).

CREATE TABLE IF NOT EXISTS charvak_career_certifications (
    cert_id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    assessment_id TEXT NOT NULL,
    role TEXT NOT NULL,
    industry TEXT NOT NULL,
    level TEXT NOT NULL,
    score INTEGER NOT NULL,
    badge_tier TEXT NOT NULL,
    certification_hash TEXT NOT NULL UNIQUE,
    credits_charged INTEGER DEFAULT 0,
    integrity_summary JSONB,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_career_cert_assessment
    ON charvak_career_certifications(assessment_id);
CREATE INDEX IF NOT EXISTS idx_career_cert_email
    ON charvak_career_certifications(email, issued_at DESC);
CREATE INDEX IF NOT EXISTS idx_career_cert_hash
    ON charvak_career_certifications(certification_hash);
CREATE INDEX IF NOT EXISTS idx_career_cert_tier
    ON charvak_career_certifications(badge_tier);
