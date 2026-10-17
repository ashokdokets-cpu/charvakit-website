-- Session 46: Career Passport v1
-- Public, verifiable, aggregate identity artifact per user.

CREATE TABLE IF NOT EXISTS charvak_passports (
    passport_id       TEXT PRIMARY KEY,
    handle            TEXT UNIQUE NOT NULL,
    email             TEXT NOT NULL UNIQUE,
    display_name      TEXT,
    headline          TEXT,
    charvak_score     INTEGER DEFAULT 0,
    score_tier        TEXT DEFAULT 'foundation',
    score_updated_at  TIMESTAMP,
    is_public         BOOLEAN DEFAULT TRUE,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_passports_handle ON charvak_passports (handle);
CREATE INDEX IF NOT EXISTS idx_passports_email ON charvak_passports (email);
CREATE INDEX IF NOT EXISTS idx_passports_score ON charvak_passports (charvak_score DESC);
CREATE INDEX IF NOT EXISTS idx_passports_public ON charvak_passports (is_public) WHERE is_public = TRUE;