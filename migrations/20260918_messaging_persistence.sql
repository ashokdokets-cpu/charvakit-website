-- ============================================================================
-- Charvak IT Consulting - Messaging Persistence (Tier 3, Session D/5)
-- Migration: 20260918_messaging_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist messages to Postgres. Conversations are derived from
--            message set (no separate table) using a normalized conversation_key.
--            Templates stay in code (static 5-template catalog).
-- Safety:    CREATE TABLE IF NOT EXISTS. Adds table only.
-- Rollback:  DROP TABLE IF EXISTS charvak_messages;
-- ============================================================================

CREATE TABLE IF NOT EXISTS charvak_messages (
    message_id        TEXT PRIMARY KEY,
    sender_id         TEXT NOT NULL,
    sender_type       TEXT,
    recipient_id      TEXT NOT NULL,
    recipient_type    TEXT,
    subject           TEXT DEFAULT 'New Message',
    body              TEXT DEFAULT '',
    job_id            TEXT,
    application_id    TEXT,
    status            TEXT DEFAULT 'sent',
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at           TIMESTAMP,
    conversation_key  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_sender       ON charvak_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_recipient    ON charvak_messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_messages_convo        ON charvak_messages(conversation_key);
CREATE INDEX IF NOT EXISTS idx_messages_status       ON charvak_messages(status);
CREATE INDEX IF NOT EXISTS idx_messages_created      ON charvak_messages(created_at);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================