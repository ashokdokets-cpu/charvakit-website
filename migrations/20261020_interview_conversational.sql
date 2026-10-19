-- Session 65a: Interview Prep conversational mode support
-- Adds mode, turn_count, max_turns columns. All idempotent.

ALTER TABLE charvak_interview_sessions
    ADD COLUMN IF NOT EXISTS mode TEXT DEFAULT 'static';

ALTER TABLE charvak_interview_sessions
    ADD COLUMN IF NOT EXISTS turn_count INTEGER DEFAULT 0;

ALTER TABLE charvak_interview_sessions
    ADD COLUMN IF NOT EXISTS max_turns INTEGER DEFAULT 12;
