-- ============================================================
-- Session 48: Cohort Mode (final Wave 1 layer, batch virality)
-- ============================================================
-- Enables batch leaderboards for college cohorts, coaching groups,
-- and training batches. See cohorts_engine.py for the engine.
--
-- All tables are idempotent (IF NOT EXISTS).
-- Composite score = passport.score*0.6 + streak*5 + weekly_drills*10
-- Weekly reset: leaderboard cached per ISO week (Monday).

CREATE TABLE IF NOT EXISTS charvak_cohorts (
    cohort_id       TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT DEFAULT '',
    join_code       TEXT NOT NULL UNIQUE,
    created_by      TEXT NOT NULL,
    member_count    INTEGER NOT NULL DEFAULT 1,
    is_public       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_refresh    TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cohorts_join_code
    ON charvak_cohorts (join_code);
CREATE INDEX IF NOT EXISTS idx_cohorts_creator
    ON charvak_cohorts (created_by);
CREATE INDEX IF NOT EXISTS idx_cohorts_public
    ON charvak_cohorts (is_public) WHERE is_public = TRUE;

CREATE TABLE IF NOT EXISTS charvak_cohort_members (
    cohort_id       TEXT NOT NULL,
    member_email    TEXT NOT NULL,
    role            TEXT NOT NULL DEFAULT 'member',
    joined_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cohort_id, member_email)
);

CREATE INDEX IF NOT EXISTS idx_cohort_members_email
    ON charvak_cohort_members (member_email);

CREATE TABLE IF NOT EXISTS charvak_cohort_leaderboard (
    cohort_id       TEXT NOT NULL,
    member_email    TEXT NOT NULL,
    composite_score INTEGER NOT NULL,
    rank            INTEGER NOT NULL,
    week_start      DATE NOT NULL,
    refreshed_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cohort_id, member_email, week_start)
);

CREATE INDEX IF NOT EXISTS idx_cohort_lb_week
    ON charvak_cohort_leaderboard (cohort_id, week_start, rank);