-- migrations/20260919_lang_and_kiosk.sql
-- K-2 batch:
--   K/29: persist language assessment submissions (with score)
--   #37b: log kiosk check-in events (who checked in, not just count)

-- === Table 1: language assessment submissions (K/29) ===
CREATE TABLE IF NOT EXISTS charvak_lang_ai_submissions (
    submission_id   TEXT PRIMARY KEY,
    assessment_id   TEXT NOT NULL,
    email           TEXT,
    answers         JSONB DEFAULT '[]'::jsonb,
    score           INTEGER DEFAULT 0,
    passed          BOOLEAN DEFAULT FALSE,
    submitted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lang_ai_subs_assessment
    ON charvak_lang_ai_submissions(assessment_id);

CREATE INDEX IF NOT EXISTS idx_lang_ai_subs_email
    ON charvak_lang_ai_submissions(email);

CREATE INDEX IF NOT EXISTS idx_lang_ai_subs_submitted
    ON charvak_lang_ai_submissions(submitted_at);

-- === Table 2: kiosk check-in events (#37b) ===
CREATE TABLE IF NOT EXISTS charvak_enterprise_kiosk_events (
    event_id        TEXT PRIMARY KEY,
    kiosk_id        TEXT NOT NULL,
    student_id      TEXT NOT NULL,
    checked_in_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kiosk_events_kiosk
    ON charvak_enterprise_kiosk_events(kiosk_id);

CREATE INDEX IF NOT EXISTS idx_kiosk_events_student
    ON charvak_enterprise_kiosk_events(student_id);

CREATE INDEX IF NOT EXISTS idx_kiosk_events_time
    ON charvak_enterprise_kiosk_events(checked_in_at);