-- Session 27 - Anti-Cheating Layer A
-- Assessment integrity events (environment signals, Layer A only)
-- Self-healing: also created at runtime by integrity_engine._ensure_tables()
-- This file exists for documentation and manual application via Render Shell.
--
-- Session 47.5 follow-up: the ALTER TABLE references
-- charvak_career_assessments, which is created by
-- career_assessment_engine._ensure_tables() on first assessment start,
-- not by any migration. On a fresh DB, the table does not exist yet.
-- Guard the ALTER so the migration succeeds either way. The CREATE TABLE
-- and CREATE INDEX statements run unconditionally (that is the real work
-- of this migration).

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

-- Conditional: only add the column if the parent table exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'charvak_career_assessments'
    ) THEN
        ALTER TABLE charvak_career_assessments
            ADD COLUMN IF NOT EXISTS integrity_summary JSONB DEFAULT '{}'::jsonb;
    END IF;
END $$;