-- Migration: 20261030_question_rotation
-- Purpose: Speed up prior-question hash lookups for rotation.
-- Idempotent. Safe to re-run.

CREATE INDEX IF NOT EXISTS idx_ca_rotation_lookup
    ON charvak_career_assessments (email, role, industry, level, format)
    WHERE questions_json IS NOT NULL;