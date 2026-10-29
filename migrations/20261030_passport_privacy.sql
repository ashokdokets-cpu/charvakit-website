-- Migration: 20261030_passport_privacy
-- Purpose: Change passport default visibility from public to private.
-- 
-- Privacy fix: New users should NOT be publicly searchable by default.
-- Existing public profiles are preserved (no data change to existing rows).
--
-- This migration is idempotent and safe to re-run.

-- 1. Set any NULL is_public to FALSE (edge case cleanup)
UPDATE charvak_passports 
SET is_public = FALSE 
WHERE is_public IS NULL;

-- 2. Add NOT NULL constraint (prevents future NULLs)
ALTER TABLE charvak_passports 
ALTER COLUMN is_public SET NOT NULL;

-- 3. Change default to FALSE (privacy by default)
ALTER TABLE charvak_passports 
ALTER COLUMN is_public SET DEFAULT FALSE;

-- 4. Existing public profiles are PRESERVED.
-- Do not run UPDATE without WHERE — that would break demo profiles.
