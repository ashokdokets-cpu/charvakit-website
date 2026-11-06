-- Migration: 20261107_job_sources.sql
-- Purpose: Extend charvak_jobs and charvak_bench_matches for multi-source job board ingestion
-- Session: 107
-- Idempotent: Safe to run multiple times

-- Add source tracking columns to charvak_jobs
ALTER TABLE charvak_jobs
    ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual',
    ADD COLUMN IF NOT EXISTS external_job_id TEXT,
    ADD COLUMN IF NOT EXISTS raw_json JSONB,
    ADD COLUMN IF NOT EXISTS is_us_eligible BOOLEAN DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS location TEXT;

-- Unique index prevents duplicate ingestion of the same external job
CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_source_external
    ON charvak_jobs (source, external_job_id)
    WHERE external_job_id IS NOT NULL;

-- Index for fast US-eligible filtering
CREATE INDEX IF NOT EXISTS idx_jobs_us_eligible
    ON charvak_jobs (is_us_eligible, source);

-- Extend charvak_bench_matches to track source (vendor JD vs job board)
ALTER TABLE charvak_bench_matches
    ADD COLUMN IF NOT EXISTS job_id TEXT,
    ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'vendor_jd';

-- Index for filtering by source
CREATE INDEX IF NOT EXISTS idx_bench_matches_source
    ON charvak_bench_matches (source);

-- Source registry table (for admin UI + enable/disable)
CREATE TABLE IF NOT EXISTS charvak_job_sources (
    source_name TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    api_url TEXT,
    attribution_text TEXT,
    active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP,
    last_sync_status TEXT,
    last_sync_error TEXT,
    total_jobs_fetched INTEGER DEFAULT 0,
    total_jobs_inserted INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed the two sources we are building now
INSERT INTO charvak_job_sources (source_name, display_name, api_url, attribution_text, active)
VALUES
    ('remotive', 'Remotive', 'https://remotive.com/api/remote-jobs',
     'Job data from Remotive (https://remotive.com)', TRUE),
    ('arbeitnow', 'Arbeitnow', 'https://www.arbeitnow.com/api/job-board-api',
     'Job data from Arbeitnow (https://www.arbeitnow.com)', TRUE)
ON CONFLICT (source_name) DO NOTHING;
