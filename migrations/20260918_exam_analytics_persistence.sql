-- ============================================================================
-- Charvak IT Consulting - Exam Analytics Persistence (Tier 3, Session F/1)
-- Migration: 20260918_exam_analytics_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist per-topic performance + answer history to Postgres.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_exam_analytics_history;
--            DROP TABLE IF EXISTS charvak_exam_analytics_performance;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_exam_analytics_performance (
    email       TEXT NOT NULL,
    exam_id     TEXT NOT NULL,
    topic       TEXT NOT NULL,
    total       INTEGER DEFAULT 0,
    correct     INTEGER DEFAULT 0,
    wrong       INTEGER DEFAULT 0,
    accuracy    NUMERIC(5,2) DEFAULT 0,
    avg_time    NUMERIC(8,2) DEFAULT 0,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (email, exam_id, topic)
);
CREATE INDEX IF NOT EXISTS idx_exam_analytics_perf_email ON charvak_exam_analytics_performance(email);

CREATE TABLE IF NOT EXISTS charvak_exam_analytics_history (
    history_id   TEXT PRIMARY KEY,
    email        TEXT NOT NULL,
    exam_id      TEXT NOT NULL,
    topic        TEXT NOT NULL,
    question_id  INTEGER,
    correct      BOOLEAN DEFAULT FALSE,
    time_taken   INTEGER DEFAULT 0,
    recorded_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_exam_analytics_hist_email ON charvak_exam_analytics_history(email);
CREATE INDEX IF NOT EXISTS idx_exam_analytics_hist_date  ON charvak_exam_analytics_history(recorded_at);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================