-- 20260929_auditbot_paid.sql
-- AuditBot paid tiers: one-time fix + continuous subscription.

CREATE TABLE IF NOT EXISTS charvak_auditbot_fixes (
    fix_id        TEXT PRIMARY KEY,
    email         TEXT NOT NULL,
    scan_id       TEXT,
    repo_url      TEXT,
    language      TEXT,
    scan_type     TEXT,
    findings_json JSONB,
    guide_json    JSONB,
    credits_used  INTEGER NOT NULL DEFAULT 0,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_auditbot_fixes_email ON charvak_auditbot_fixes (email, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_auditbot_fixes_scan  ON charvak_auditbot_fixes (scan_id);

CREATE TABLE IF NOT EXISTS charvak_auditbot_subscriptions (
    email          TEXT PRIMARY KEY,
    tier           TEXT NOT NULL DEFAULT 'continuous',
    started_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at     TIMESTAMP NOT NULL,
    scans_used     INTEGER NOT NULL DEFAULT 0,
    last_scan_at   TIMESTAMP,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_auditbot_subs_expires ON charvak_auditbot_subscriptions (expires_at);
