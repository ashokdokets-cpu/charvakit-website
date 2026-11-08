-- 20261109_college_dashboard.sql
-- TPO / College Placement Readiness Dashboard

-- Add institution tracking to candidates (idempotent)
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS institution_name TEXT,
    ADD COLUMN IF NOT EXISTS batch_id TEXT;

CREATE INDEX IF NOT EXISTS idx_candidates_institution
    ON charvak_candidates (institution_name) WHERE institution_name IS NOT NULL;

-- Table for bulk invites
CREATE TABLE IF NOT EXISTS charvak_college_invites (
    invite_id TEXT PRIMARY KEY,
    institution_name TEXT NOT NULL,
    student_email TEXT NOT NULL,
    student_name TEXT,
    target_role TEXT,
    status TEXT DEFAULT 'pending', -- pending, sent, clicked, completed
    invited_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    UNIQUE(institution_name, student_email)
);

CREATE INDEX IF NOT EXISTS idx_invites_institution
    ON charvak_college_invites (institution_name);