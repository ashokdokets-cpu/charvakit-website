-- ============================================================
-- Session 40b - IELTS reading/listening tables
-- ============================================================
-- ielts_engine.py referenced these four tables but no migration
-- ever created them. Every attempt hit "relation does not exist"
-- silently (swallowed by try/except).
--
--   charvak_ielts_reading_passages    - passage catalog
--   charvak_ielts_listening_sections  - lecture catalog
--   charvak_ielts_reading_attempts    - per-attempt results
--   charvak_ielts_listening_attempts  - per-attempt results
--
-- Verified against ielts_engine.py:
--   get_reading_passage:      SELECT passage_id, passage_num, title,
--                             topic, content, word_count, questions_json,
--                             use_count
--   evaluate_reading:         SELECT passage_num, title, topic,
--                             questions_json; INSERT attempts
--   get_listening_section:    SELECT section_id, section_num, title,
--                             topic, transcript, duration_sec,
--                             questions_json, use_count
--   evaluate_listening:       INSERT attempts
-- ============================================================

CREATE TABLE IF NOT EXISTS charvak_ielts_reading_passages (
    passage_id     TEXT PRIMARY KEY,
    passage_num    INTEGER NOT NULL,
    title          TEXT NOT NULL DEFAULT '',
    topic          TEXT NOT NULL DEFAULT '',
    content        TEXT NOT NULL DEFAULT '',
    word_count     INTEGER DEFAULT 0,
    questions_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    use_count      INTEGER NOT NULL DEFAULT 0,
    last_used_at   TIMESTAMP WITHOUT TIME ZONE,
    created_at     TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ielts_reading_passages_num
    ON charvak_ielts_reading_passages (passage_num);


CREATE TABLE IF NOT EXISTS charvak_ielts_listening_sections (
    section_id     TEXT PRIMARY KEY,
    section_num    INTEGER NOT NULL,
    title          TEXT NOT NULL DEFAULT '',
    topic          TEXT NOT NULL DEFAULT '',
    transcript     TEXT NOT NULL DEFAULT '',
    duration_sec   INTEGER DEFAULT 180,
    questions_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    use_count      INTEGER NOT NULL DEFAULT 0,
    last_used_at   TIMESTAMP WITHOUT TIME ZONE,
    created_at     TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ielts_listening_sections_num
    ON charvak_ielts_listening_sections (section_num);


CREATE TABLE IF NOT EXISTS charvak_ielts_reading_attempts (
    attempt_id      BIGSERIAL PRIMARY KEY,
    passage_id      TEXT NOT NULL,
    email           TEXT NOT NULL,
    answers_json    JSONB NOT NULL DEFAULT '[]'::jsonb,
    correct_count   INTEGER NOT NULL DEFAULT 0,
    total_questions INTEGER NOT NULL DEFAULT 0,
    band_score      NUMERIC,
    attempted_at    TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ielts_reading_attempts_email
    ON charvak_ielts_reading_attempts (email);


CREATE TABLE IF NOT EXISTS charvak_ielts_listening_attempts (
    attempt_id      BIGSERIAL PRIMARY KEY,
    section_id      TEXT NOT NULL,
    email           TEXT NOT NULL,
    answers_json    JSONB NOT NULL DEFAULT '[]'::jsonb,
    correct_count   INTEGER NOT NULL DEFAULT 0,
    total_questions INTEGER NOT NULL DEFAULT 0,
    band_score      NUMERIC,
    attempted_at    TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ielts_listening_attempts_email
    ON charvak_ielts_listening_attempts (email);