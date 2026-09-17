-- ============================================================================
-- Charvak IT Consulting - Training Engine Persistence (Session A/3)
-- Migration: 20260918_training_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist trainer-posted courses and student enrollments to
--            Postgres. Distinct from AI Courses (fixed catalog + EMI).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_training_enrollments;
--            DROP TABLE IF EXISTS charvak_training_courses;
-- Notes:     self.trainers and self.classrooms in training_engine.py are
--            dead code (never written, never read) and have no tables.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Trainer-posted courses
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_training_courses (
    course_id         TEXT PRIMARY KEY,
    course_name       TEXT NOT NULL,
    trainer_name      TEXT,
    trainer_email     TEXT NOT NULL,
    category          TEXT DEFAULT 'Programming',
    duration_weeks    INTEGER DEFAULT 4,
    price_inr         NUMERIC(10,2) NOT NULL DEFAULT 0,
    platform_fee      NUMERIC(10,2) DEFAULT 0,
    trainer_payout    NUMERIC(10,2) DEFAULT 0,
    description       TEXT DEFAULT '',
    skills            JSONB DEFAULT '[]'::jsonb,
    schedule          TEXT DEFAULT 'Flexible',
    status            TEXT DEFAULT 'published',
    enrolled_count    INTEGER DEFAULT 0,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_training_courses_trainer     ON charvak_training_courses(trainer_email);
CREATE INDEX IF NOT EXISTS idx_training_courses_status      ON charvak_training_courses(status);
CREATE INDEX IF NOT EXISTS idx_training_courses_category    ON charvak_training_courses(category);
CREATE INDEX IF NOT EXISTS idx_training_courses_skills_gin  ON charvak_training_courses USING GIN (skills);

-- ---------------------------------------------------------------------------
-- 2. Student enrollments
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_training_enrollments (
    enrollment_id     TEXT PRIMARY KEY,
    course_id         TEXT NOT NULL,
    student_name      TEXT,
    student_email     TEXT NOT NULL,
    payment_status    TEXT DEFAULT 'pending',
    payment_id        TEXT,
    progress_percent  INTEGER DEFAULT 0,
    enrolled_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at      TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_training_enrollments_course  ON charvak_training_enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_training_enrollments_student ON charvak_training_enrollments(student_email);
CREATE INDEX IF NOT EXISTS idx_training_enrollments_payment ON charvak_training_enrollments(payment_status);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================