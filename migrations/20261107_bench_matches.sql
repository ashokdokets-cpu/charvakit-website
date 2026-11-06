-- Session 3: Bench Matching Engine
-- Session 4 (extended): adds fee + vendor_email tracking

CREATE TABLE IF NOT EXISTS charvak_bench_matches (
    match_id TEXT PRIMARY KEY,
    jd_id TEXT NOT NULL,
    candidate_email TEXT NOT NULL,
    candidate_id TEXT,
    candidate_name TEXT,
    match_score INTEGER NOT NULL,
    skill_score INTEGER DEFAULT 0,
    auth_score INTEGER DEFAULT 0,
    rate_score INTEGER DEFAULT 0,
    availability_score INTEGER DEFAULT 0,
    matched_skills JSONB DEFAULT '[]'::jsonb,
    missing_skills JSONB DEFAULT '[]'::jsonb,
    computed_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending',
    submitted_at TIMESTAMP,
    vendor_response TEXT,
    interviewed_at TIMESTAMP,
    placed_at TIMESTAMP,
    fee_amount_inr INTEGER,
    vendor_email_sent_id TEXT,
    notes TEXT,
    UNIQUE(jd_id, candidate_email)
);

CREATE INDEX IF NOT EXISTS idx_bench_matches_score 
    ON charvak_bench_matches(match_score DESC);
CREATE INDEX IF NOT EXISTS idx_bench_matches_jd 
    ON charvak_bench_matches(jd_id);
CREATE INDEX IF NOT EXISTS idx_bench_matches_candidate 
    ON charvak_bench_matches(candidate_email);
CREATE INDEX IF NOT EXISTS idx_bench_matches_status 
    ON charvak_bench_matches(status);

-- Session 4 additions (idempotent for existing tables)
ALTER TABLE charvak_bench_matches ADD COLUMN IF NOT EXISTS fee_amount_inr INTEGER;
ALTER TABLE charvak_bench_matches ADD COLUMN IF NOT EXISTS vendor_email_sent_id TEXT;