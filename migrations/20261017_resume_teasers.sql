-- Session 45-A4: Resume Roaster Teaser
-- Anonymous free-tier resume scanning + paid full-report unlock

CREATE TABLE IF NOT EXISTS charvak_resume_teasers (
    teaser_id         TEXT PRIMARY KEY,
    share_id          TEXT NOT NULL UNIQUE,
    ip_hash           TEXT,
    resume_preview    TEXT,
    job_title         TEXT,
    score             INTEGER,
    one_issue         TEXT,
    teaser_json       JSONB,
    email             TEXT,
    unlocked          BOOLEAN DEFAULT FALSE,
    unlocked_at       TIMESTAMP,
    unlock_payment_id TEXT,
    gateway           TEXT,
    currency          TEXT,
    amount_local      NUMERIC,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_resume_teasers_share ON charvak_resume_teasers (share_id);
CREATE INDEX IF NOT EXISTS idx_resume_teasers_ip_date ON charvak_resume_teasers (ip_hash, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_resume_teasers_email ON charvak_resume_teasers (email) WHERE email IS NOT NULL;