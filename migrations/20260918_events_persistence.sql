-- ============================================================================
-- Charvak IT Consulting - Events Engine Persistence (Tier 3, Session C/1)
-- Migration: 20260918_events_persistence.sql
-- Created:   2026-09-18
-- Purpose:   Persist events + RSVPs to Postgres so they survive Render restarts.
-- Safety:    All CREATE TABLE IF NOT EXISTS. Adds tables only. No existing
--            table altered.
-- Rollback:  DROP TABLE IF EXISTS charvak_event_rsvps;
--            DROP TABLE IF EXISTS charvak_events;
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Events (career fairs, webinars, info sessions, workshops)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_events (
    event_id          TEXT PRIMARY KEY,
    title             TEXT,
    description       TEXT DEFAULT '',
    event_type        TEXT DEFAULT 'webinar',
    organizer_id      TEXT,
    organizer_name    TEXT,
    date              TEXT,
    duration_minutes  INTEGER DEFAULT 60,
    platform          TEXT DEFAULT 'zoom',
    location          TEXT DEFAULT '',
    link              TEXT DEFAULT '',
    max_attendees     INTEGER DEFAULT 100,
    target_audience   TEXT DEFAULT 'All',
    rsvp_count        INTEGER DEFAULT 0,
    status            TEXT NOT NULL DEFAULT 'upcoming',
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_events_status ON charvak_events(status);
CREATE INDEX IF NOT EXISTS idx_events_type   ON charvak_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_date   ON charvak_events(date);

-- ---------------------------------------------------------------------------
-- 2. RSVPs (one row per attendee per event; idempotent on email+event)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_event_rsvps (
    rsvp_id         TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL,
    user_id         TEXT,
    user_name       TEXT,
    user_email      TEXT NOT NULL,
    user_type       TEXT DEFAULT 'student',
    checked_in      BOOLEAN DEFAULT FALSE,
    checked_in_at   TIMESTAMP,
    rsvp_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_id, user_email)
);
CREATE INDEX IF NOT EXISTS idx_rsvps_event_id ON charvak_event_rsvps(event_id);
CREATE INDEX IF NOT EXISTS idx_rsvps_email    ON charvak_event_rsvps(user_email);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================