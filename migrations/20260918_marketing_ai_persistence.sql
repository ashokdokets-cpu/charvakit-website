-- ============================================================================
-- Charvak IT Consulting - Marketing AI Persistence (Tier 3, Session F/3)
-- Migration: 20260918_marketing_ai_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist generated job ads, social posts, lead drips.
--            Templates stay in code; generate_booking_link is stateless.
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds tables only.
-- Rollback:  DROP TABLE IF EXISTS charvak_marketing_lead_drips;
--            DROP TABLE IF EXISTS charvak_marketing_social_posts;
--            DROP TABLE IF EXISTS charvak_marketing_job_ads;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_marketing_job_ads (
    ad_id       TEXT PRIMARY KEY,
    job_title   TEXT,
    company     TEXT,
    ad_text     TEXT,
    platforms   JSONB DEFAULT '[]'::jsonb,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_marketing_ads_company ON charvak_marketing_job_ads(company);
CREATE INDEX IF NOT EXISTS idx_marketing_ads_title   ON charvak_marketing_job_ads(job_title);

CREATE TABLE IF NOT EXISTS charvak_marketing_social_posts (
    post_id     TEXT PRIMARY KEY,
    topic       TEXT,
    platform    TEXT,
    audience    TEXT,
    post_text   TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_marketing_posts_platform ON charvak_marketing_social_posts(platform);

CREATE TABLE IF NOT EXISTS charvak_marketing_lead_drips (
    drip_id     TEXT PRIMARY KEY,
    lead_name   TEXT,
    lead_email  TEXT,
    service     TEXT,
    sequence    JSONB DEFAULT '[]'::jsonb,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_marketing_drips_email   ON charvak_marketing_lead_drips(lead_email);
CREATE INDEX IF NOT EXISTS idx_marketing_drips_service ON charvak_marketing_lead_drips(service);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================