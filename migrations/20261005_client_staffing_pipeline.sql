-- 20261005_client_staffing_pipeline.sql
-- Session 22: Charvak-mediated staffing pipeline (CBREX-ready).
-- Idempotent. Safe to run multiple times.

-- 1. Client roles -------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_client_roles (
    role_id              TEXT PRIMARY KEY,
    client_name          TEXT NOT NULL,
    client_type          TEXT DEFAULT 'direct',
    vendor_portal        TEXT,
    vendor_role_ref      TEXT,
    title                TEXT NOT NULL,
    location             TEXT,
    experience_min_years INTEGER,
    experience_max_years INTEGER,
    skills_required      TEXT,
    budget_min_inr       INTEGER,
    budget_max_inr       INTEGER,
    job_type             TEXT DEFAULT 'Permanent',
    submission_deadline  DATE,
    priority             TEXT DEFAULT 'normal',
    status               TEXT DEFAULT 'sourcing',
    source               TEXT DEFAULT 'email',
    source_email_ref     TEXT,
    jd_text              TEXT,
    posted_by            TEXT DEFAULT 'charvak-staffing',
    created_by           TEXT,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_client_roles_status
    ON charvak_client_roles (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_client_roles_client
    ON charvak_client_roles (client_name);

-- 2. Role screening questions -------------------------------------
CREATE TABLE IF NOT EXISTS charvak_role_screening_questions (
    question_id    TEXT PRIMARY KEY,
    role_id        TEXT NOT NULL,
    question_num   INTEGER NOT NULL,
    question_text  TEXT NOT NULL,
    answer_type    TEXT NOT NULL,
    choices_json   JSONB,
    fill_source    TEXT NOT NULL DEFAULT 'candidate',
    required       BOOLEAN DEFAULT TRUE,
    sort_order     INTEGER,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_screening_questions_role
    ON charvak_role_screening_questions (role_id, sort_order);

-- 3. Screening answers --------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_role_screening_answers (
    answer_id    TEXT PRIMARY KEY,
    role_id      TEXT NOT NULL,
    candidate_id TEXT NOT NULL,
    question_id  TEXT NOT NULL,
    answer_text  TEXT,
    answered_by  TEXT,
    answered_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(candidate_id, question_id)
);
CREATE INDEX IF NOT EXISTS idx_screening_answers_cand
    ON charvak_role_screening_answers (candidate_id, role_id);

-- 4. Candidate documents ------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_candidate_documents (
    document_id    TEXT PRIMARY KEY,
    candidate_id   TEXT NOT NULL,
    email          TEXT,
    document_type  TEXT NOT NULL,
    filename       TEXT NOT NULL,
    content_type   TEXT,
    size_bytes     INTEGER,
    storage_path   TEXT,
    content_base64 TEXT,
    uploaded_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_cand_docs_candidate
    ON charvak_candidate_documents (candidate_id, document_type);

-- 5. Candidate consents -------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_candidate_consents (
    consent_id     TEXT PRIMARY KEY,
    candidate_id   TEXT NOT NULL,
    email          TEXT NOT NULL,
    role_id        TEXT NOT NULL,
    vendor         TEXT,
    consent_method TEXT,
    consented_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address     TEXT,
    user_agent     TEXT,
    consent_proof_doc_id TEXT,
    UNIQUE(candidate_id, role_id)
);

-- 6. Extend charvak_candidates ------------------------------------
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS first_name TEXT;
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS last_name TEXT;
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS additional_email TEXT;
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS additional_phone TEXT;
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS current_company TEXT;
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS current_salary_inr NUMERIC;
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS current_salary_currency TEXT DEFAULT 'INR';
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS relevant_experience_years INTEGER;
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS expected_hike_percent INTEGER;
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS variable_component TEXT;
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS other_benefits TEXT;
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS serving_notice_last_day DATE;
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS notice_period TEXT;
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS candidate_summary TEXT;
ALTER TABLE charvak_candidates
    ADD COLUMN IF NOT EXISTS country TEXT DEFAULT 'India';

-- 7. Extend charvak_applications ----------------------------------
ALTER TABLE charvak_applications
    ADD COLUMN IF NOT EXISTS client_role_id TEXT;
ALTER TABLE charvak_applications
    ADD COLUMN IF NOT EXISTS certificate_id TEXT;
ALTER TABLE charvak_applications
    ADD COLUMN IF NOT EXISTS readiness_score INTEGER;
ALTER TABLE charvak_applications
    ADD COLUMN IF NOT EXISTS submission_status TEXT DEFAULT 'pending';
ALTER TABLE charvak_applications
    ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMP;
ALTER TABLE charvak_applications
    ADD COLUMN IF NOT EXISTS submission_notes TEXT;
ALTER TABLE charvak_applications
    ADD COLUMN IF NOT EXISTS recruiter_notes TEXT;
