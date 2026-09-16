-- ============================================================================
-- Charvak IT Consulting - Course Levels (Beginner / Intermediate / Advanced)
-- Migration: 20260916_course_levels.sql
-- Created:   2026-09-16
-- Purpose:   Add per-level course variants with distinct price and duration.
-- Safety:    CREATE TABLE IF NOT EXISTS. No existing table altered.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Per-course level variants (India price source of truth)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_course_levels (
    course_name     TEXT NOT NULL,
    level           TEXT NOT NULL,           -- 'beginner' | 'intermediate' | 'advanced'
    price_inr       INTEGER NOT NULL,
    duration_weeks  INTEGER NOT NULL,
    description     TEXT DEFAULT '',
    status          TEXT NOT NULL DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (course_name, level)
);

CREATE INDEX IF NOT EXISTS idx_course_levels_level
    ON charvak_course_levels(level);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================