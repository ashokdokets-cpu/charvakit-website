-- ============================================================================
-- Charvak IT Consulting - Micro-Internship + Escrow (Tier 3, Session 5A)
-- Migration: 20260917_micro_internship.sql
-- Created:   2026-09-17
-- Purpose:   Persist micro-internship projects, applications, clients, and
--            escrow transactions. Escrow uses manual payouts (RazorpayX later).
-- Safety:    All CREATE TABLE IF NOT EXISTS. Adds tables only; no existing
--            table altered.
-- Rollback:  DROP TABLE IF EXISTS charvak_micro_applications;
--            DROP TABLE IF EXISTS charvak_micro_projects;
--            DROP TABLE IF EXISTS charvak_micro_clients;
--            DROP TABLE IF EXISTS charvak_escrow_transactions;
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Micro-internship client companies
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_micro_clients (
    client_id         TEXT PRIMARY KEY,
    company_name      TEXT NOT NULL,
    contact_email     TEXT NOT NULL,
    contact_name      TEXT,
    industry          TEXT DEFAULT '',
    company_size      TEXT DEFAULT '',
    total_projects    INTEGER DEFAULT 0,
    active_projects   INTEGER DEFAULT 0,
    total_spend       NUMERIC(12,2) DEFAULT 0,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_micro_clients_email ON charvak_micro_clients(contact_email);

-- ---------------------------------------------------------------------------
-- 2. Posted projects
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_micro_projects (
    project_id        TEXT PRIMARY KEY,
    title             TEXT NOT NULL,
    category          TEXT DEFAULT 'Web Development',
    difficulty        TEXT DEFAULT 'Intermediate',
    duration_weeks    INTEGER DEFAULT 2,
    budget_inr        NUMERIC(12,2) NOT NULL,
    budget_usd        NUMERIC(12,2),
    skills_required   JSONB DEFAULT '[]'::jsonb,
    description       TEXT DEFAULT '',
    client_id         TEXT,
    company_name      TEXT,
    contact_email     TEXT,
    escrow_required   BOOLEAN DEFAULT TRUE,
    escrow_id         TEXT,
    assigned_intern   JSONB,
    status            TEXT DEFAULT 'open',
    applications_count INTEGER DEFAULT 0,
    milestones        JSONB DEFAULT '[]'::jsonb,
    submission        JSONB,
    feedback          TEXT,
    rating            INTEGER,
    deadline          TIMESTAMP,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at      TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_micro_projects_status   ON charvak_micro_projects(status);
CREATE INDEX IF NOT EXISTS idx_micro_projects_client   ON charvak_micro_projects(client_id);
CREATE INDEX IF NOT EXISTS idx_micro_projects_escrow   ON charvak_micro_projects(escrow_id);
CREATE INDEX IF NOT EXISTS idx_micro_projects_category ON charvak_micro_projects(category);

-- ---------------------------------------------------------------------------
-- 3. Applications
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_micro_applications (
    application_id    TEXT PRIMARY KEY,
    project_id        TEXT NOT NULL,
    candidate_name    TEXT,
    candidate_email   TEXT,
    skills            JSONB DEFAULT '[]'::jsonb,
    portfolio_url     TEXT DEFAULT '',
    why_interested    TEXT DEFAULT '',
    status            TEXT DEFAULT 'applied',
    ai_score          INTEGER DEFAULT 0,
    applied_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_at       TIMESTAMP,
    submitted_at      TIMESTAMP,
    approved_at       TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_micro_apps_project ON charvak_micro_applications(project_id);
CREATE INDEX IF NOT EXISTS idx_micro_apps_email   ON charvak_micro_applications(candidate_email);

-- ---------------------------------------------------------------------------
-- 4. Escrow transactions (manual payouts; RazorpayX-ready)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_escrow_transactions (
    escrow_id              TEXT PRIMARY KEY,
    client_name            TEXT,
    client_email           TEXT,
    vendor_name            TEXT,
    vendor_email           TEXT,
    amount                 NUMERIC(12,2) NOT NULL,
    currency               TEXT DEFAULT 'INR',
    platform_fee           NUMERIC(12,2) DEFAULT 0,
    vendor_payout          NUMERIC(12,2) DEFAULT 0,
    description            TEXT DEFAULT '',
    milestones             JSONB DEFAULT '[]'::jsonb,
    status                 TEXT DEFAULT 'awaiting_deposit',
    payment_method         TEXT DEFAULT 'Dokets VouchAI Escrow',
    payment_details        JSONB,
    delivery_data          JSONB,
    dispute                JSONB,
    duration_days          INTEGER DEFAULT 30,
    payout_status          TEXT DEFAULT 'not_due',
    payout_method          TEXT,
    payout_reference       TEXT,
    payout_amount          NUMERIC(12,2),
    payout_at              TIMESTAMP,
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    funded_at              TIMESTAMP,
    delivered_at           TIMESTAMP,
    released_at            TIMESTAMP,
    expires_at             TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_escrow_status       ON charvak_escrow_transactions(status);
CREATE INDEX IF NOT EXISTS idx_escrow_payout       ON charvak_escrow_transactions(payout_status);
CREATE INDEX IF NOT EXISTS idx_escrow_client_email ON charvak_escrow_transactions(client_email);
CREATE INDEX IF NOT EXISTS idx_escrow_vendor_email ON charvak_escrow_transactions(vendor_email);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================