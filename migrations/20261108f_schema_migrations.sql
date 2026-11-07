-- 20261108f_schema_migrations.sql
-- Tracks which migration files have been applied to the DB.
-- Does NOT auto-run migrations — used by /admin/migrations UI.

CREATE TABLE IF NOT EXISTS charvak_schema_migrations (
    migration_name TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    applied_by TEXT DEFAULT 'manual',
    checksum TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_schema_migrations_applied_at
    ON charvak_schema_migrations (applied_at DESC);

-- Seed with known migrations already applied to prod
-- (These are the ones we applied manually today)
INSERT INTO charvak_schema_migrations (migration_name, applied_by, notes) VALUES
    ('20261108_relevance_filter.sql', 'manual', 'Session 108G - bench relevance filter'),
    ('20261108_retention_engine.sql', 'manual', 'Session 108C - retention engine'),
    ('20261108b_api_sources.sql', 'manual', 'Session 108B - 6 new API sources'),
    ('20261108d_retention_tiers.sql', 'manual', 'Session 108C+ - tiered rejections'),
    ('20261108f_schema_migrations.sql', 'self', 'Session 108F - this migration tracker')
ON CONFLICT (migration_name) DO NOTHING;