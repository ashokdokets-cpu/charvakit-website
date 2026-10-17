-- Session 46-B: Skill Twin Challenges
-- Viral loop that brings challengers into the passport funnel.

CREATE TABLE IF NOT EXISTS charvak_skill_twin_challenges (
    challenge_id    TEXT PRIMARY KEY,
    owner_email     TEXT NOT NULL,
    owner_handle    TEXT NOT NULL,
    owner_score     INTEGER NOT NULL,
    role            TEXT,
    industry        TEXT,
    level           TEXT,
    status          TEXT NOT NULL DEFAULT 'pending',
    challenger_email TEXT,
    challenger_score INTEGER,
    challenger_pct   INTEGER,
    challenger_assessment_id TEXT,
    winner          TEXT,
    credits_owner   INTEGER NOT NULL DEFAULT 0,
    credits_challenger INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at     TIMESTAMP,
    expires_at      TIMESTAMP,
    clicked_count   INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_skill_twin_owner ON charvak_skill_twin_challenges (owner_email, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_skill_twin_handle ON charvak_skill_twin_challenges (owner_handle, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_skill_twin_status ON charvak_skill_twin_challenges (status);