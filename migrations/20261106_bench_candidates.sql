-- Session 2: Bench Candidate Profile
-- Extends charvak_candidates with US staffing fields.
-- Split into individual ALTER statements because Postgres
-- does not reliably support multi-column ADD COLUMN IF NOT EXISTS.
-- NOTE: availability already exists as a legacy column, do not touch it.

ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS work_auth_status TEXT;
ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS rate_min NUMERIC;
ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS rate_max NUMERIC;
ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS visa_expiry DATE;
ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS has_verified_cert BOOLEAN DEFAULT FALSE;
ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS bench_since TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_candidates_work_auth 
    ON charvak_candidates(work_auth_status) 
    WHERE work_auth_status IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_candidates_bench_since 
    ON charvak_candidates(bench_since DESC) 
    WHERE bench_since IS NOT NULL;

ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS employer_email TEXT;
ALTER TABLE charvak_candidates ADD COLUMN IF NOT EXISTS employer_phone TEXT;