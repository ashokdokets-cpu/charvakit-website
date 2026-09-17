-- ============================================================================
-- Charvak IT Consulting - LMS Engine Persistence (Session A/4)
-- Migration: 20260918_lms_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist LMS ratings, quizzes, quiz attempts, certificates,
--            lesson progress, discussions, lessons, and payouts.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_lms_payouts;
--            DROP TABLE IF EXISTS charvak_lms_lessons;
--            DROP TABLE IF EXISTS charvak_lms_discussions;
--            DROP TABLE IF EXISTS charvak_lms_lesson_progress;
--            DROP TABLE IF EXISTS charvak_lms_certificates;
--            DROP TABLE IF EXISTS charvak_lms_quiz_attempts;
--            DROP TABLE IF EXISTS charvak_lms_quizzes;
--            DROP TABLE IF EXISTS charvak_lms_ratings;
-- Notes:     charvak_lms_certificates and charvak_lms_lessons are distinct
--            from charvak_certificates and charvak_course_lessons (AI Courses).
--            The "order" column is renamed to lesson_order (reserved word).
-- ============================================================================

-- 1. Ratings
CREATE TABLE IF NOT EXISTS charvak_lms_ratings (
    rating_id       TEXT PRIMARY KEY,
    course_id       TEXT NOT NULL,
    student_email   TEXT NOT NULL,
    rating          INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review          TEXT DEFAULT '',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_lms_ratings_course  ON charvak_lms_ratings(course_id);
CREATE INDEX IF NOT EXISTS idx_lms_ratings_student ON charvak_lms_ratings(student_email);

-- 2. Quizzes
CREATE TABLE IF NOT EXISTS charvak_lms_quizzes (
    quiz_id     TEXT PRIMARY KEY,
    course_id   TEXT NOT NULL,
    title       TEXT DEFAULT 'Course Quiz',
    questions   JSONB DEFAULT '[]'::jsonb,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_lms_quizzes_course ON charvak_lms_quizzes(course_id);

-- 3. Quiz attempts (includes quiz_id/course_id for queryability)
CREATE TABLE IF NOT EXISTS charvak_lms_quiz_attempts (
    attempt_id      TEXT PRIMARY KEY,
    quiz_id         TEXT,
    course_id       TEXT,
    student_email   TEXT NOT NULL,
    score           INTEGER NOT NULL DEFAULT 0,
    passed          BOOLEAN DEFAULT FALSE,
    attempted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_lms_attempts_student ON charvak_lms_quiz_attempts(student_email);
CREATE INDEX IF NOT EXISTS idx_lms_attempts_quiz    ON charvak_lms_quiz_attempts(quiz_id);
CREATE INDEX IF NOT EXISTS idx_lms_attempts_course  ON charvak_lms_quiz_attempts(course_id);

-- 4. Certificates (distinct from AI Courses)
CREATE TABLE IF NOT EXISTS charvak_lms_certificates (
    certificate_id   TEXT PRIMARY KEY,
    course_name      TEXT,
    student_email    TEXT NOT NULL,
    student_name     TEXT DEFAULT 'Student',
    issued_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verification_url TEXT
);
CREATE INDEX IF NOT EXISTS idx_lms_certs_student ON charvak_lms_certificates(student_email);

-- 5. Lesson progress
CREATE TABLE IF NOT EXISTS charvak_lms_lesson_progress (
    progress_id        TEXT PRIMARY KEY,
    enrollment_id      TEXT NOT NULL,
    lesson_id          TEXT NOT NULL,
    completed          BOOLEAN DEFAULT TRUE,
    time_spent_minutes INTEGER DEFAULT 0,
    updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_lms_progress_enrollment ON charvak_lms_lesson_progress(enrollment_id);
CREATE INDEX IF NOT EXISTS idx_lms_progress_lesson     ON charvak_lms_lesson_progress(lesson_id);

-- 6. Discussions (replies as JSONB)
CREATE TABLE IF NOT EXISTS charvak_lms_discussions (
    discussion_id  TEXT PRIMARY KEY,
    course_id      TEXT NOT NULL,
    author         TEXT,
    title          TEXT,
    content        TEXT,
    replies        JSONB DEFAULT '[]'::jsonb,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_lms_disc_course ON charvak_lms_discussions(course_id);

-- 7. Lessons (per course; "order" renamed to lesson_order)
CREATE TABLE IF NOT EXISTS charvak_lms_lessons (
    lesson_id        TEXT PRIMARY KEY,
    course_id        TEXT NOT NULL,
    title            TEXT DEFAULT 'Lesson',
    video_url        TEXT DEFAULT '',
    duration_minutes INTEGER DEFAULT 10,
    lesson_order     INTEGER DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_lms_lessons_course ON charvak_lms_lessons(course_id);
CREATE INDEX IF NOT EXISTS idx_lms_lessons_order  ON charvak_lms_lessons(course_id, lesson_order);

-- 8. Payouts
CREATE TABLE IF NOT EXISTS charvak_lms_payouts (
    payout_id      TEXT PRIMARY KEY,
    trainer_email  TEXT NOT NULL,
    amount         NUMERIC(10,2) NOT NULL DEFAULT 0,
    status         TEXT DEFAULT 'pending',
    requested_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_lms_payouts_trainer ON charvak_lms_payouts(trainer_email);
CREATE INDEX IF NOT EXISTS idx_lms_payouts_status  ON charvak_lms_payouts(status);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================