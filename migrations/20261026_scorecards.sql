-- 20261026_scorecards.sql
-- F1: Public shareable candidate scorecards
-- Idempotent.

CREATE TABLE IF NOT EXISTS charvak_scorecards (
  scorecard_id TEXT PRIMARY KEY,
  assessment_id TEXT NOT NULL,
  email TEXT NOT NULL,
  role TEXT,
  industry TEXT,
  level TEXT,
  format TEXT,
  overall_score INTEGER,
  overall_percentile INTEGER,
  passed BOOLEAN,
  payload_json JSONB NOT NULL,
  integrity_risk TEXT DEFAULT 'clean',
  certificate_id TEXT,
  certificate_verify_hash TEXT,
  shares_count INTEGER DEFAULT 0,
  views_count INTEGER DEFAULT 0,
  last_shared_at TIMESTAMP,
  last_viewed_at TIMESTAMP,
  public BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_scorecards_email ON charvak_scorecards(LOWER(email));
CREATE INDEX IF NOT EXISTS idx_scorecards_assessment ON charvak_scorecards(assessment_id);
CREATE INDEX IF NOT EXISTS idx_scorecards_public ON charvak_scorecards(public) WHERE public = TRUE;