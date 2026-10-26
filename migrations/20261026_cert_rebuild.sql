-- Drop and recreate charvak_career_certifications with canonical schema
-- (0 rows on prod, so no data loss. Aligns with Session 69 + Session 83 code.)
DROP TABLE IF EXISTS charvak_career_certifications;

CREATE TABLE charvak_career_certifications (
  cert_id text PRIMARY KEY,
  assessment_id text NOT NULL,
  email text NOT NULL,
  display_name text,
  role text NOT NULL,
  industry text,
  level text,
  score integer NOT NULL,
  passed boolean DEFAULT true,
  badge_tier text NOT NULL,
  certification_hash text NOT NULL,
  credits_charged integer DEFAULT 0,
  integrity_summary jsonb DEFAULT '{}'::jsonb,
  issued_at timestamp DEFAULT CURRENT_TIMESTAMP,
  revoked_at timestamp,
  -- Coding/SQL extensions
  format text DEFAULT 'mcq',
  language text,
  database_name text,
  task_classes jsonb DEFAULT '[]'::jsonb,
  runtime_info text
);

CREATE INDEX idx_cert_assessment ON charvak_career_certifications(assessment_id);
CREATE INDEX idx_cert_email ON charvak_career_certifications(email);
CREATE UNIQUE INDEX idx_cert_hash ON charvak_career_certifications(certification_hash);