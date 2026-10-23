-- 20261024_engagement_engine.sql
-- Session 81 A3 v1.0 — Engagement Dashboard

CREATE TABLE IF NOT EXISTS charvak_student_preferences (
    email TEXT PRIMARY KEY,
    email_enabled BOOLEAN DEFAULT TRUE,
    in_app_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS charvak_student_badges (
    badge_id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    badge_key TEXT NOT NULL,
    badge_name TEXT NOT NULL,
    badge_icon TEXT DEFAULT '🏆',
    description TEXT,
    awarded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(email, badge_key)
);

CREATE INDEX IF NOT EXISTS idx_badges_email ON charvak_student_badges (email, awarded_at DESC);

CREATE TABLE IF NOT EXISTS charvak_engagement_events (
    event_id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_data JSONB DEFAULT '{}'::jsonb,
    points INTEGER DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_email ON charvak_engagement_events (email, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_type ON charvak_engagement_events (event_type, created_at DESC);