-- Migration: 20261030_cert_coding_sql_backfill
-- Purpose: Add coding/SQL columns that exist on prod but were missing on
--          local DBs (schema drift from Session 73/84d).
--
-- Idempotent. Safe to re-run.

ALTER TABLE charvak_career_certifications
    ADD COLUMN IF NOT EXISTS format TEXT,
    ADD COLUMN IF NOT EXISTS language TEXT,
    ADD COLUMN IF NOT EXISTS database_name TEXT,
    ADD COLUMN IF NOT EXISTS task_classes JSONB,
    ADD COLUMN IF NOT EXISTS runtime_info TEXT;