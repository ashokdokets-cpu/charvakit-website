-- ============================================================================
-- Charvak IT Consulting - KYC Engine Persistence (Tier 3, Session A/1)
-- Migration: 20260918_kyc_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist KYC verifications, partners, and verified-user badges
--            to Postgres so they survive Render restarts.
-- Safety:    All CREATE TABLE IF NOT EXISTS. Adds tables only. No existing
--            table altered.
-- Rollback:  DROP TABLE IF EXISTS charvak_kyc_verified_users;
--            DROP TABLE IF EXISTS charvak_kyc_partners;
--            DROP TABLE IF EXISTS charvak_kyc_verifications;
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. KYC verifications (one row per initiated verification)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_kyc_verifications (
    verification_id      TEXT PRIMARY KEY,
    user_name            TEXT,
    user_email           TEXT NOT NULL,
    user_phone           TEXT,
    verification_type    TEXT NOT NULL DEFAULT 'identity',
    country              TEXT DEFAULT 'India',
    documents_requested  JSONB DEFAULT '[]'::jsonb,
    documents_submitted  JSONB DEFAULT '[]'::jsonb,
    status               TEXT NOT NULL DEFAULT 'pending',
    price_inr            INTEGER DEFAULT 499,
    price_usd            INTEGER DEFAULT 6,
    payment_status       TEXT DEFAULT 'pending',
    payment_order_id     TEXT,
    assigned_to          TEXT,
    results              JSONB DEFAULT '{}'::jsonb,
    notes                TEXT DEFAULT '',
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at         TIMESTAMP,
    valid_until          TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_kyc_verif_email    ON charvak_kyc_verifications(user_email);
CREATE INDEX IF NOT EXISTS idx_kyc_verif_status   ON charvak_kyc_verifications(status);
CREATE INDEX IF NOT EXISTS idx_kyc_verif_assigned ON charvak_kyc_verifications(assigned_to);
CREATE INDEX IF NOT EXISTS idx_kyc_verif_type     ON charvak_kyc_verifications(verification_type);

-- ---------------------------------------------------------------------------
-- 2. KYC partners (verification agency companies)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_kyc_partners (
    partner_id              TEXT PRIMARY KEY,
    agency_name             TEXT NOT NULL,
    contact_person          TEXT,
    email                   TEXT NOT NULL,
    phone                   TEXT,
    services                JSONB DEFAULT '[]'::jsonb,
    coverage                TEXT DEFAULT '',
    status                  TEXT NOT NULL DEFAULT 'pending_review',
    verifications_completed INTEGER DEFAULT 0,
    revenue_earned          NUMERIC(12,2) DEFAULT 0,
    rating                  NUMERIC(3,1),
    registered_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at             TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_kyc_partners_status ON charvak_kyc_partners(status);
CREATE INDEX IF NOT EXISTS idx_kyc_partners_email  ON charvak_kyc_partners(email);

-- ---------------------------------------------------------------------------
-- 3. Verified users (powers the badge system)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_kyc_verified_users (
    email              TEXT PRIMARY KEY,
    name               TEXT,
    verification_id    TEXT,
    verification_type  TEXT,
    verified_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until        TIMESTAMP,
    badge_id           TEXT UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_kyc_verified_badge ON charvak_kyc_verified_users(badge_id);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================