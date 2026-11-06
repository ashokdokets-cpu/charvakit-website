-- Session 3: Bench Matching Engine
-- Scores every vendor JD × every bench candidate

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