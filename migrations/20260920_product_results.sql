-- ============================================================================
-- Charvak IT Consulting - Product Audit Trail (#86)
-- Migration: 20260920_product_results.sql
-- Created:   2026-09-20
-- Purpose:   Log every call to the 11 product methods in products_engine.py
--            Enables analytics, audit trail, debugging of AI product usage.
-- Safety:    All CREATE ... IF NOT EXISTS. Idempotent.
-- Rollback:  DROP TABLE IF EXISTS charvak_product_results;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_product_results (
    result_id     TEXT PRIMARY KEY,
    product_type  TEXT NOT NULL,
    email         TEXT,
    input_data    JSONB NOT NULL DEFAULT '{}'::jsonb,
    result_data   JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_product_results_type
    ON charvak_product_results(product_type);

CREATE INDEX IF NOT EXISTS idx_product_results_email
    ON charvak_product_results(email);

CREATE INDEX IF NOT EXISTS idx_product_results_created
    ON charvak_product_results(created_at);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
