-- ============================================================================
-- Charvak IT Consulting - Brand Engine Persistence (Tier 3, Session D/2)
-- Migration: 20260918_brand_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist brand pages, reviews, promoted jobs to Postgres.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_brand_promoted_jobs;
--            DROP TABLE IF EXISTS charvak_brand_reviews;
--            DROP TABLE IF EXISTS charvak_brands;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_brands (
    brand_id        TEXT PRIMARY KEY,
    company_name    TEXT,
    industry        TEXT DEFAULT '',
    description     TEXT DEFAULT '',
    logo_url        TEXT DEFAULT '',
    website         TEXT DEFAULT '',
    location        TEXT DEFAULT '',
    size            TEXT DEFAULT '',
    culture_tags    JSONB DEFAULT '[]'::jsonb,
    average_rating  NUMERIC(3,1) DEFAULT 0,
    review_count    INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_brands_company ON charvak_brands(company_name);
CREATE INDEX IF NOT EXISTS idx_brands_industry ON charvak_brands(industry);

CREATE TABLE IF NOT EXISTS charvak_brand_reviews (
    review_id        TEXT PRIMARY KEY,
    company_id       TEXT NOT NULL,
    reviewer_name    TEXT,
    reviewer_type    TEXT DEFAULT 'candidate',
    rating           INTEGER DEFAULT 5,
    title            TEXT DEFAULT '',
    review           TEXT DEFAULT '',
    would_recommend  BOOLEAN DEFAULT TRUE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_brand_reviews_company  ON charvak_brand_reviews(company_id);
CREATE INDEX IF NOT EXISTS idx_brand_reviews_rating   ON charvak_brand_reviews(rating);

CREATE TABLE IF NOT EXISTS charvak_brand_promoted_jobs (
    promotion_id  TEXT PRIMARY KEY,
    job_id        TEXT,
    company_id    TEXT,
    starts_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ends_at       TIMESTAMP,
    views         INTEGER DEFAULT 0,
    clicks        INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_brand_promos_company ON charvak_brand_promoted_jobs(company_id);
CREATE INDEX IF NOT EXISTS idx_brand_promos_job     ON charvak_brand_promoted_jobs(job_id);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================