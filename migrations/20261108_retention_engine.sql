-- 20261108_retention_engine.sql
-- Retention engine for job pipeline
-- Idempotent: safe to run multiple times

-- Audit table: every retention run logged here
CREATE TABLE IF NOT EXISTS charvak_retention_runs (
    run_id VARCHAR(64) PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    dry_run BOOLEAN NOT NULL DEFAULT TRUE,
    triggered_by VARCHAR(120),
    status VARCHAR(20) NOT NULL DEFAULT 'running',
    rows_deleted_rejected_jds INTEGER DEFAULT 0,
    rows_deleted_jobs_closed INTEGER DEFAULT 0,
    rows_deleted_jobs_unmatched INTEGER DEFAULT 0,
    rows_deleted_sync_runs INTEGER DEFAULT 0,
    total_rows_deleted INTEGER DEFAULT 0,
    error_message TEXT,
    details_json JSONB
);

CREATE INDEX IF NOT EXISTS idx_retention_runs_started
    ON charvak_retention_runs (started_at DESC);

-- Retention config: one row per table, editable by admin
CREATE TABLE IF NOT EXISTS charvak_retention_config (
    config_key VARCHAR(80) PRIMARY KEY,
    retention_days INTEGER NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    min_rows_to_keep INTEGER NOT NULL DEFAULT 0,
    description TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed defaults (idempotent)
INSERT INTO charvak_retention_config
    (config_key, retention_days, enabled, min_rows_to_keep, description)
VALUES
    ('rejected_jds', 30, TRUE, 100,
     'Bench-relevance rejected JDs audit trail'),
    ('jobs_closed', 90, TRUE, 50,
     'Jobs with status=closed or status=expired'),
    ('jobs_unmatched_open', 60, TRUE, 100,
     'Jobs still open but unmatched for N days'),
    ('sync_runs', 90, TRUE, 20,
     'Job sync execution logs')
ON CONFLICT (config_key) DO NOTHING;

-- Mark matched jobs closed when all their matches are old
-- (used by the engine to identify "closed" candidates for purge)
ALTER TABLE charvak_jobs
    ADD COLUMN IF NOT EXISTS last_matched_at TIMESTAMPTZ;

-- Index to speed up retention queries
CREATE INDEX IF NOT EXISTS idx_jobs_created_at
    ON charvak_jobs (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_jobs_status_created
    ON charvak_jobs (status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_rejected_jds_rejected_at
    ON charvak_rejected_jds (rejected_at DESC);