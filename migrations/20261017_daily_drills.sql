-- Session 47: Daily Drills + Streaks
-- Habit loop for Wave 1 of the flywheel.

CREATE TABLE IF NOT EXISTS charvak_daily_drills (
    drill_id        TEXT PRIMARY KEY,
    email           TEXT NOT NULL,
    drill_date      DATE NOT NULL,
    topic           TEXT NOT NULL,
    role_context    TEXT,
    industry_context TEXT,
    level_context   TEXT,
    questions_json  JSONB NOT NULL,
    answers_json    JSONB,
    score           INTEGER,
    correct_count   INTEGER,
    total_questions INTEGER NOT NULL DEFAULT 5,
    completed       BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at    TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(email, drill_date)
);

CREATE INDEX IF NOT EXISTS idx_drills_email_date
    ON charvak_daily_drills (email, drill_date DESC);
CREATE INDEX IF NOT EXISTS idx_drills_completed
    ON charvak_daily_drills (email, completed, drill_date DESC);

CREATE TABLE IF NOT EXISTS charvak_user_streaks (
    email            TEXT PRIMARY KEY,
    current_streak   INTEGER NOT NULL DEFAULT 0,
    longest_streak   INTEGER NOT NULL DEFAULT 0,
    last_drill_date  DATE,
    total_drills     INTEGER NOT NULL DEFAULT 0,
    total_correct    INTEGER NOT NULL DEFAULT 0,
    total_questions  INTEGER NOT NULL DEFAULT 0,
    streak_credits   INTEGER NOT NULL DEFAULT 0,
    updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_streaks_current
    ON charvak_user_streaks (current_streak DESC);