-- ============================================================
-- Affiliate Program (Session 95)
-- Idempotent, safe to re-run.
-- ============================================================

-- 1. Affiliate applications
CREATE TABLE IF NOT EXISTS charvak_affiliate_applications (
    application_id TEXT PRIMARY KEY,
    referrer_id TEXT REFERENCES charvak_referrer_accounts(referrer_id),
    applicant_email TEXT NOT NULL,
    applicant_name TEXT,
    company_name TEXT,
    website TEXT,
    country TEXT DEFAULT 'IN',
    affiliate_type TEXT,                     -- individual | agency | consultant | recruiter | coach
    expected_monthly_referrals INTEGER,
    expected_deal_size_inr INTEGER,
    why_interested TEXT,
    tax_id_type TEXT,                        -- pan | gst | w9 | none
    tax_id TEXT,
    -- Approval
    status TEXT DEFAULT 'auto_approved',     -- auto_approved (Bronze) | pending (Silver+) | approved | rejected
    tier_requested TEXT DEFAULT 'bronze',    -- bronze | silver | gold | platinum
    tier_granted TEXT,                       -- set on approval
    reviewed_by TEXT,
    reviewed_at TIMESTAMP,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_aff_app_email ON charvak_affiliate_applications(applicant_email);
CREATE INDEX IF NOT EXISTS idx_aff_app_status ON charvak_affiliate_applications(status);
CREATE INDEX IF NOT EXISTS idx_aff_app_referrer ON charvak_affiliate_applications(referrer_id);

-- 2. Affiliate contracts (signed agreements)
CREATE TABLE IF NOT EXISTS charvak_affiliate_contracts (
    contract_id TEXT PRIMARY KEY,
    referrer_id TEXT NOT NULL REFERENCES charvak_referrer_accounts(referrer_id),
    tier TEXT NOT NULL,                      -- bronze | silver | gold | platinum
    commission_first_year NUMERIC(5,4) NOT NULL,
    commission_recurring NUMERIC(5,4) NOT NULL,
    -- Signed state
    signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signed_by_name TEXT,
    signed_by_email TEXT,
    signed_by_ip_hash TEXT,
    -- Validity
    effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_until TIMESTAMP,               -- NULL = auto-renew
    status TEXT DEFAULT 'active',            -- active | expired | terminated
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_aff_contract_referrer ON charvak_affiliate_contracts(referrer_id);
CREATE INDEX IF NOT EXISTS idx_aff_contract_status ON charvak_affiliate_contracts(status);

-- 3. Add affiliate fields to referrer_accounts
ALTER TABLE charvak_referrer_accounts
    ADD COLUMN IF NOT EXISTS is_affiliate BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS affiliate_tier TEXT,              -- bronze | silver | gold | platinum
    ADD COLUMN IF NOT EXISTS affiliate_applied_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS affiliate_approved_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS custom_landing_slug TEXT,         -- for /r/{slug} co-branded pages
    ADD COLUMN IF NOT EXISTS co_brand_logo_url TEXT;
CREATE INDEX IF NOT EXISTS idx_referrer_affiliate ON charvak_referrer_accounts(is_affiliate);
CREATE INDEX IF NOT EXISTS idx_referrer_landing ON charvak_referrer_accounts(custom_landing_slug);