-- 20260930_skill_twin_badge.sql
-- Skill-Twin badge purchase flow (AA4d Phases B-D).

-- Ensure the results table has badge columns (idempotent)
ALTER TABLE charvak_skill_twin_results
    ADD COLUMN IF NOT EXISTS badge_issued BOOLEAN DEFAULT FALSE;
ALTER TABLE charvak_skill_twin_results
    ADD COLUMN IF NOT EXISTS badge_id TEXT;
ALTER TABLE charvak_skill_twin_results
    ADD COLUMN IF NOT EXISTS badge_issued_at TIMESTAMP;

-- Idempotency: one badge per check_id
CREATE UNIQUE INDEX IF NOT EXISTS idx_skill_twin_badge_unique
    ON charvak_skill_twin_results (check_id)
    WHERE badge_issued = TRUE;

-- Public badge page: fast lookup by badge_id
CREATE INDEX IF NOT EXISTS idx_skill_twin_badge_id
    ON charvak_skill_twin_results (badge_id)
    WHERE badge_id IS NOT NULL;
