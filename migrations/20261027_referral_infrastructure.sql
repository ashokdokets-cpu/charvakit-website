-- ============================================================
-- Referral Program — unified infrastructure (Session 92)
-- Idempotent, safe to re-run.
-- ============================================================

-- 1. Master referrer accounts (unified across student/institution/employer/affiliate)
CREATE TABLE IF NOT EXISTS charvak_referrer_accounts (
    referrer_id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    phone TEXT,
    country TEXT DEFAULT 'IN',
    referral_code TEXT UNIQUE NOT NULL,
    tier TEXT DEFAULT 'starter',              -- starter | pro | partner | elite
    program_type TEXT NOT NULL DEFAULT 'student', -- student | institution | employer | affiliate
    total_referrals INTEGER DEFAULT 0,
    total_revenue_referred_inr INTEGER DEFAULT 0,
    total_commissions_earned_inr INTEGER DEFAULT 0,
    total_commissions_paid_inr INTEGER DEFAULT 0,
    payment_method TEXT,                      -- razorpay | paypal | wire | stripe
    payment_details JSONB,                    -- account details per method
    status TEXT DEFAULT 'active',             -- active | suspended | banned
    fraud_flags INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_referrer_code ON charvak_referrer_accounts(referral_code);
CREATE INDEX IF NOT EXISTS idx_referrer_email ON charvak_referrer_accounts(email);
CREATE INDEX IF NOT EXISTS idx_referrer_tier ON charvak_referrer_accounts(tier);
CREATE INDEX IF NOT EXISTS idx_referrer_status ON charvak_referrer_accounts(status);

-- 2. Every attributed conversion (signup, cert paid, institution deal, employer sub)
CREATE TABLE IF NOT EXISTS charvak_referral_conversions (
    conversion_id TEXT PRIMARY KEY,
    referrer_id TEXT NOT NULL REFERENCES charvak_referrer_accounts(referrer_id),
    referred_email TEXT NOT NULL,
    referred_ip_hash TEXT,
    conversion_type TEXT NOT NULL,            -- signup | cert_paid | institution_deal | employer_sub | affiliate_deal
    conversion_value_inr INTEGER NOT NULL DEFAULT 0,
    commission_rate NUMERIC(5,4) NOT NULL DEFAULT 0,
    commission_amount_inr INTEGER NOT NULL DEFAULT 0,
    status TEXT DEFAULT 'pending',            -- pending | approved | paid | refunded | fraud_blocked
    approved_at TIMESTAMP,
    paid_at TIMESTAMP,
    payment_reference TEXT,
    hold_until TIMESTAMP,                     -- 30-day fraud hold
    fraud_reason TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_conv_referrer ON charvak_referral_conversions(referrer_id);
CREATE INDEX IF NOT EXISTS idx_conv_status ON charvak_referral_conversions(status);
CREATE INDEX IF NOT EXISTS idx_conv_referred ON charvak_referral_conversions(referred_email);
CREATE INDEX IF NOT EXISTS idx_conv_hold ON charvak_referral_conversions(hold_until);
CREATE INDEX IF NOT EXISTS idx_conv_type ON charvak_referral_conversions(conversion_type);

-- 3. Recurring commissions (employer + affiliate subscriptions)
CREATE TABLE IF NOT EXISTS charvak_recurring_commissions (
    recurring_id TEXT PRIMARY KEY,
    referrer_id TEXT NOT NULL REFERENCES charvak_referrer_accounts(referrer_id),
    customer_email TEXT NOT NULL,
    plan_key TEXT,
    subscription_amount_inr INTEGER NOT NULL,
    commission_rate NUMERIC(5,4) NOT NULL,
    commission_amount_inr INTEGER NOT NULL,
    billing_period TEXT NOT NULL,             -- '2026-10' (YYYY-MM)
    status TEXT DEFAULT 'pending',            -- pending | paid | refunded
    paid_at TIMESTAMP,
    payment_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(referrer_id, customer_email, billing_period)
);
CREATE INDEX IF NOT EXISTS idx_recurring_ref ON charvak_recurring_commissions(referrer_id);
CREATE INDEX IF NOT EXISTS idx_recurring_period ON charvak_recurring_commissions(billing_period);
CREATE INDEX IF NOT EXISTS idx_recurring_status ON charvak_recurring_commissions(status);

-- 4. Click tracking (attribution proof + fraud signal)
CREATE TABLE IF NOT EXISTS charvak_referral_clicks_v2 (
    click_id TEXT PRIMARY KEY,
    referral_code TEXT NOT NULL,
    ip_hash TEXT,
    user_agent TEXT,
    landing_page TEXT,
    country TEXT,
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_clicks_code ON charvak_referral_clicks_v2(referral_code);
CREATE INDEX IF NOT EXISTS idx_clicks_time ON charvak_referral_clicks_v2(clicked_at);
CREATE INDEX IF NOT EXISTS idx_clicks_ip ON charvak_referral_clicks_v2(ip_hash);

-- Seed: any existing charvak_referrals rows become referrer_accounts
INSERT INTO charvak_referrer_accounts
    (referrer_id, email, name, referral_code, program_type, tier, status)
SELECT
    'REF-' || UPPER(SUBSTRING(MD5(RANDOM()::text) FROM 1 FOR 8)),
    LOWER(referrer_email),
    referrer_name,
    referral_code,
    'student',
    'starter',
    'active'
FROM charvak_referrals
WHERE LOWER(referrer_email) NOT IN (SELECT LOWER(email) FROM charvak_referrer_accounts)
ON CONFLICT (email) DO NOTHING;