-- 20260930_marketing_booking_kit.sql
-- Marketing AI paid tier: AI-generated outreach kit with
-- booking link, message drafts, agenda, and follow-up sequence.

CREATE TABLE IF NOT EXISTS charvak_marketing_booking_kits (
    kit_id         TEXT PRIMARY KEY,
    email          TEXT NOT NULL,
    host_name      TEXT,
    business_name  TEXT,
    meeting_type   TEXT,
    duration_min   INTEGER,
    context        TEXT,
    kit_json       JSONB,
    credits_used   INTEGER NOT NULL DEFAULT 0,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_marketing_booking_kits_email
    ON charvak_marketing_booking_kits (email, created_at DESC);
