-- Session 45-A4 security: share claim deduplication + rate limiting

CREATE TABLE IF NOT EXISTS charvak_share_claims (
    claim_id        TEXT PRIMARY KEY,
    share_id        TEXT NOT NULL,
    ip_hash         TEXT,
    user_email      TEXT,
    claimed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_share_claims_share ON charvak_share_claims (share_id);
CREATE INDEX IF NOT EXISTS idx_share_claims_ip_date ON charvak_share_claims (ip_hash, claimed_at DESC);
CREATE INDEX IF NOT EXISTS idx_share_claims_share_ip ON charvak_share_claims (share_id, ip_hash);

-- Track the sharer so we can block self-claims and cap daily earnings
ALTER TABLE charvak_share_rewards
    ADD COLUMN IF NOT EXISTS owner_ip_hash TEXT,
    ADD COLUMN IF NOT EXISTS last_claimed_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS claim_window_start TIMESTAMP;