-- Session 52 (2026-10-19): CAS API key table
-- Idempotent. Backed up by cas_engine._ensure_tables() self-healing DDL.

CREATE TABLE IF NOT EXISTS charvak_cas_api_keys (
    key_id TEXT PRIMARY KEY,
    institution_name TEXT NOT NULL,
    contact_name TEXT,
    contact_email TEXT NOT NULL,
    api_key_hash TEXT UNIQUE NOT NULL,
    tier TEXT DEFAULT 'pilot',
    monthly_quota INTEGER DEFAULT 500,
    calls_this_month INTEGER DEFAULT 0,
    last_call_at TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cas_keys_hash
ON charvak_cas_api_keys(api_key_hash);

CREATE INDEX IF NOT EXISTS idx_cas_keys_active
ON charvak_cas_api_keys(is_active) WHERE is_active = TRUE;