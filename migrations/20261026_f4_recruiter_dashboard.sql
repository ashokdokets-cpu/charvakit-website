-- F4 Recruiter Dashboard — v1+v2+v3 schema (idempotent)
ALTER TABLE charvak_client_roles ADD COLUMN IF NOT EXISTS level text DEFAULT 'mid';

ALTER TABLE charvak_applications
  ADD COLUMN IF NOT EXISTS candidate_email text,
  ADD COLUMN IF NOT EXISTS candidate_name text,
  ADD COLUMN IF NOT EXISTS hired_at timestamp,
  ADD COLUMN IF NOT EXISTS hired_company text,
  ADD COLUMN IF NOT EXISTS hired_ctc_inr integer;

UPDATE charvak_applications
SET candidate_email = user_id
WHERE candidate_email IS NULL
  AND user_id IS NOT NULL
  AND user_id LIKE '%@%';

CREATE TABLE IF NOT EXISTS charvak_career_certifications (
  certification_id text PRIMARY KEY,
  assessment_id text NOT NULL,
  email text NOT NULL,
  display_name text,
  role text NOT NULL,
  industry text,
  level text,
  score integer NOT NULL,
  tier text,
  cert_hash text NOT NULL,
  integrity_summary jsonb DEFAULT '{}'::jsonb,
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_career_cert_email ON charvak_career_certifications(email);
CREATE INDEX IF NOT EXISTS idx_career_cert_hash ON charvak_career_certifications(cert_hash);

UPDATE charvak_client_roles
SET level = CASE
  WHEN experience_min_years IS NULL THEN 'mid'
  WHEN experience_min_years = 0 THEN 'fresher'
  WHEN experience_min_years <= 2 THEN 'junior'
  WHEN experience_min_years <= 5 THEN 'mid'
  WHEN experience_min_years <= 10 THEN 'senior'
  ELSE 'staff'
END
WHERE level IS NULL OR level = 'mid';