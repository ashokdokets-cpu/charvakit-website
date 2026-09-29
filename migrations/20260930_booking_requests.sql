-- 20260930_booking_requests.sql
-- Hosted booking page: slug/host_email columns on kits + request capture.

ALTER TABLE charvak_marketing_booking_kits
    ADD COLUMN IF NOT EXISTS slug TEXT;
ALTER TABLE charvak_marketing_booking_kits
    ADD COLUMN IF NOT EXISTS host_email TEXT;
ALTER TABLE charvak_marketing_booking_kits
    ADD COLUMN IF NOT EXISTS booking_url TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS idx_booking_kits_slug
    ON charvak_marketing_booking_kits (slug)
    WHERE slug IS NOT NULL;

CREATE TABLE IF NOT EXISTS charvak_booking_requests (
    request_id       TEXT PRIMARY KEY,
    slug             TEXT NOT NULL,
    kit_id           TEXT NOT NULL,
    host_email       TEXT NOT NULL,
    prospect_name    TEXT NOT NULL,
    prospect_email   TEXT NOT NULL,
    preferred_time   TEXT,
    notes            TEXT,
    status           TEXT NOT NULL DEFAULT 'pending',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_booking_requests_slug
    ON charvak_booking_requests (slug, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_booking_requests_host
    ON charvak_booking_requests (host_email, created_at DESC);
