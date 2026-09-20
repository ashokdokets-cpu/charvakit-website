-- migrations/20260921_user_ability.sql
-- Session G2 (C4): Per-user, per-skill ability tracking for adaptive difficulty.
-- Elo-style scoring. Start value 1000 (neutral). Bands:
--   < 900     -> Beginner
--   900-1100  -> Intermediate
--   >= 1100   -> Advanced

CREATE TABLE IF NOT EXISTS charvak_user_ability (
    email           TEXT NOT NULL,
    skill           TEXT NOT NULL,
    ability_score   NUMERIC(7,2) NOT NULL DEFAULT 1000.0,
    attempts        INTEGER NOT NULL DEFAULT 0,
    correct_total   INTEGER NOT NULL DEFAULT 0,
    question_total  INTEGER NOT NULL DEFAULT 0,
    last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (email, skill)
);

CREATE INDEX IF NOT EXISTS idx_user_ability_email ON charvak_user_ability(email);
CREATE INDEX IF NOT EXISTS idx_user_ability_skill ON charvak_user_ability(skill);
CREATE INDEX IF NOT EXISTS idx_user_ability_score ON charvak_user_ability(ability_score);