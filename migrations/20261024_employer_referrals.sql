-- 20261024_employer_referrals.sql
-- Session 81 A1 v0.2 — employer referral flow
-- Separate from charvak_referrals (which is user-to-user referral codes)

CREATE TABLE IF NOT EXISTS charvak_employer_referrals (
    referral_id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    candidate_handle TEXT NOT NULL,
    candidate_email TEXT,
    candidate_name TEXT,
    candidate_score INTEGER,
    candidate_tier TEXT,
    referred_by TEXT,                     -- referrer email (TPO/admin)
    referrer_type TEXT DEFAULT 'public', -- public | tpo | admin
    referrer_ip_hash TEXT,
    notes TEXT,
    status TEXT DEFAULT 'pending',        -- pending | sent_to_employer | shortlisted | hired | rejected
    admin_notified_at TIMESTAMP WITHOUT TIME ZONE,
    candidate_notified_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, candidate_handle)
);

CREATE INDEX IF NOT EXISTS idx_emp_ref_role ON charvak_employer_referrals (role_id, status);
CREATE INDEX IF NOT EXISTS idx_emp_ref_candidate ON charvak_employer_referrals (candidate_handle);
CREATE INDEX IF NOT EXISTS idx_emp_ref_created ON charvak_employer_referrals (created_at DESC);