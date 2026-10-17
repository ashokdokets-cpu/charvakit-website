-- Session 45-A4: Share-for-credits rewards
-- Track shares; reward referrer when a friend completes a free teaser

CREATE TABLE IF NOT EXISTS charvak_share_rewards (
    reward_id        TEXT PRIMARY KEY,
    share_id         TEXT NOT NULL UNIQUE,
    owner_email      TEXT,
    owner_token      TEXT,
    tool_name        TEXT NOT NULL,
    clicks           INTEGER DEFAULT 0,
    completions      INTEGER DEFAULT 0,
    credits_earned   INTEGER DEFAULT 0,
    claimed          BOOLEAN DEFAULT FALSE,
    claimed_at       TIMESTAMP,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_share_rewards_share ON charvak_share_rewards (share_id);
CREATE INDEX IF NOT EXISTS idx_share_rewards_owner ON charvak_share_rewards (owner_email) WHERE owner_email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_share_rewards_token ON charvak_share_rewards (owner_token) WHERE owner_token IS NOT NULL;