-- 20261002_silent_killer.sql
CREATE TABLE IF NOT EXISTS charvak_silent_killer_watches (
    watch_id         TEXT PRIMARY KEY,
    email            TEXT NOT NULL,
    url              TEXT NOT NULL,
    name             TEXT,
    interval_minutes INTEGER NOT NULL DEFAULT 5,
    active           BOOLEAN NOT NULL DEFAULT TRUE,
    last_scan_at     TIMESTAMP,
    last_status      TEXT,
    last_status_code INTEGER,
    last_error       TEXT,
    alert_count      INTEGER NOT NULL DEFAULT 0,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sk_watches_email_active
    ON charvak_silent_killer_watches (email, active, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sk_watches_active_lastscan
    ON charvak_silent_killer_watches (active, last_scan_at);

CREATE TABLE IF NOT EXISTS charvak_silent_killer_scans (
    scan_id      TEXT PRIMARY KEY,
    watch_id     TEXT NOT NULL,
    email        TEXT NOT NULL,
    url          TEXT NOT NULL,
    status_code  INTEGER,
    response_ms  INTEGER,
    ok           BOOLEAN NOT NULL,
    error        TEXT,
    checked_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sk_scans_watch_time
    ON charvak_silent_killer_scans (watch_id, checked_at DESC);
CREATE INDEX IF NOT EXISTS idx_sk_scans_email_time
    ON charvak_silent_killer_scans (email, checked_at DESC);
