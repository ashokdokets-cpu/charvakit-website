-- ============================================================================
-- Charvak IT Consulting - Exam Prep Engine Persistence (Tier 3, Session C/3)
-- Migration: 20260918_exam_prep_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist exam prep user-state (mock tests, answers, progress,
--            study plans) and cache AI-generated questions in a question bank.
--            Static exam catalog (83 exams) stays in code.
-- Safety:    All CREATE TABLE IF NOT EXISTS. Adds tables only. No existing
--            table altered.
-- Rollback:  DROP TABLE IF EXISTS charvak_exam_study_plans;
--            DROP TABLE IF EXISTS charvak_exam_user_progress;
--            DROP TABLE IF EXISTS charvak_exam_test_answers;
--            DROP TABLE IF EXISTS charvak_exam_mock_tests;
--            DROP TABLE IF EXISTS charvak_exam_question_bank;
-- ============================================================================

-- 1. QUESTION BANK (caches AI + seeded questions per exam/topic)
CREATE TABLE IF NOT EXISTS charvak_exam_question_bank (
    question_id      TEXT PRIMARY KEY,
    exam_id          TEXT NOT NULL,
    topic            TEXT NOT NULL,
    question_text    TEXT NOT NULL,
    options          JSONB NOT NULL DEFAULT '[]'::jsonb,
    correct_index    INTEGER NOT NULL DEFAULT 0,
    explanation      TEXT DEFAULT '',
    difficulty       TEXT DEFAULT 'Medium',
    generated_by     TEXT DEFAULT 'ai',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(exam_id, topic, question_text)
);
CREATE INDEX IF NOT EXISTS idx_exam_qb_exam_topic ON charvak_exam_question_bank(exam_id, topic);
CREATE INDEX IF NOT EXISTS idx_exam_qb_difficulty ON charvak_exam_question_bank(difficulty);

-- 2. MOCK TESTS (one row per attempt)
CREATE TABLE IF NOT EXISTS charvak_exam_mock_tests (
    test_id          TEXT PRIMARY KEY,
    email            TEXT NOT NULL,
    exam_id          TEXT NOT NULL,
    topic            TEXT DEFAULT '',
    status           TEXT NOT NULL DEFAULT 'in_progress',
    total_questions  INTEGER DEFAULT 0,
    correct_count    INTEGER DEFAULT 0,
    score_pct        NUMERIC(5,2) DEFAULT 0,
    started_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at     TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_exam_tests_email ON charvak_exam_mock_tests(email);
CREATE INDEX IF NOT EXISTS idx_exam_tests_exam  ON charvak_exam_mock_tests(exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_tests_status ON charvak_exam_mock_tests(status);

-- 3. TEST ANSWERS (one row per answered question; idempotent per test+question)
CREATE TABLE IF NOT EXISTS charvak_exam_test_answers (
    answer_id        TEXT PRIMARY KEY,
    test_id          TEXT NOT NULL,
    question_id      TEXT NOT NULL,
    selected_index   INTEGER,
    is_correct       BOOLEAN DEFAULT FALSE,
    answered_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(test_id, question_id)
);
CREATE INDEX IF NOT EXISTS idx_exam_answers_test ON charvak_exam_test_answers(test_id);

-- 4. USER PROGRESS (one row per email+exam+topic)
CREATE TABLE IF NOT EXISTS charvak_exam_user_progress (
    email               TEXT NOT NULL,
    exam_id             TEXT NOT NULL,
    topic               TEXT NOT NULL DEFAULT '',
    questions_attempted INTEGER DEFAULT 0,
    questions_correct   INTEGER DEFAULT 0,
    tests_completed     INTEGER DEFAULT 0,
    best_score_pct      NUMERIC(5,2) DEFAULT 0,
    last_practiced_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (email, exam_id, topic)
);
CREATE INDEX IF NOT EXISTS idx_exam_prog_email ON charvak_exam_user_progress(email);

-- 5. STUDY PLANS
CREATE TABLE IF NOT EXISTS charvak_exam_study_plans (
    plan_id          TEXT PRIMARY KEY,
    email            TEXT NOT NULL,
    exam_id          TEXT NOT NULL,
    target_date      TEXT,
    daily_minutes    INTEGER DEFAULT 60,
    topics           JSONB DEFAULT '[]'::jsonb,
    status           TEXT NOT NULL DEFAULT 'active',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_exam_plans_email ON charvak_exam_study_plans(email);
CREATE INDEX IF NOT EXISTS idx_exam_plans_status ON charvak_exam_study_plans(status);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================