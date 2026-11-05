-- Vendor JD Inbox Parser
-- Session 1 — Bench-Placement Agent

CREATE TABLE IF NOT EXISTS charvak_vendor_jds (
    jd_id TEXT PRIMARY KEY,
    source_email TEXT,
    vendor_name TEXT,
    vendor_contact TEXT,
    role_title TEXT NOT NULL,
    skills_required JSONB DEFAULT '[]'::jsonb,
    rate_min NUMERIC,
    rate_max NUMERIC,
    location TEXT,
    work_auth_required TEXT,
    duration TEXT,
    client_name TEXT,
    jd_text TEXT,
    parsed_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'active'
);

CREATE INDEX IF NOT EXISTS idx_vendor_jds_status 
    ON charvak_vendor_jds(status);

CREATE INDEX IF NOT EXISTS idx_vendor_jds_work_auth 
    ON charvak_vendor_jds(work_auth_required);

CREATE INDEX IF NOT EXISTS idx_vendor_jds_parsed_at 
    ON charvak_vendor_jds(parsed_at DESC);

CREATE INDEX IF NOT EXISTS idx_vendor_jds_vendor 
    ON charvak_vendor_jds(vendor_name);