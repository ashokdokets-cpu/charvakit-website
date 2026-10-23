-- 20261024_employer_accounts.sql
-- Session 81 A1 v0.3 — employer self-signup + admin approval

CREATE TABLE IF NOT EXISTS charvak_employer_accounts (
    account_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    contact_name TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    contact_phone TEXT,
    website TEXT,
    industry TEXT,
    company_size TEXT,
    hiring_roles TEXT,
    message TEXT,
    status TEXT DEFAULT 'pending',  -- pending | approved | rejected
    approved_by TEXT,
    approved_at TIMESTAMP WITHOUT TIME ZONE,
    rejection_reason TEXT,
    ip_hash TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_employer_email UNIQUE (contact_email)
);

CREATE INDEX IF NOT EXISTS idx_employer_accounts_status ON charvak_employer_accounts (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_employer_accounts_email ON charvak_employer_accounts (contact_email);

-- Add status update tracking to referrals
ALTER TABLE charvak_employer_referrals
    ADD COLUMN IF NOT EXISTS status_updated_at TIMESTAMP WITHOUT TIME ZONE,
    ADD COLUMN IF NOT EXISTS status_updated_by TEXT,
    ADD COLUMN IF NOT EXISTS status_notes TEXT;