-- Session 27 - Anti-Cheating Layer A
-- Assessment integrity events (environment signals, Layer A only)
-- Self-healing: also created at runtime by integrity_engine._ensure_tables()
-- This file exists for documentation and manual application via Render Shell.

CREATE TABLE IF NOT EXISTS charvak_assessment_integrity_events (
    event_id      TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    email         TEXT NOT NULL,
    event_type    TEXT NOT NULL,
    metadata      JSONB DEFAULT '{}'::jsonb,
    occurred_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_integrity_events_assessment
    ON charvak_assessment_integrity_events (assessment_id, occurred_at DESC);

CREATE INDEX IF NOT EXISTS idx_integrity_events_email
    ON charvak_assessment_integrity_events (email);

ALTER TABLE charvak_career_assessments
    ADD COLUMN IF NOT EXISTS integrity_summary JSONB DEFAULT '{}'::jsonb;