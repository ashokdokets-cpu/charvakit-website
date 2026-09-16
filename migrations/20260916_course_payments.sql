-- ============================================================================
-- Charvak IT Consulting - Course Fee + EMI (Tier 3)
-- Migration: 20260916_course_payments.sql
-- Created:   2026-09-16
-- Purpose:   Persist course payments + installment schedules.
--            Fixes: in-memory payment_enrollment.py losing data on restart.
-- Safety:    All CREATE ... IF NOT EXISTS / ON CONFLICT DO NOTHING.
--            Safe to re-run. Adds tables only; touches no existing table.
-- Rollback:  DROP TABLE IF EXISTS charvak_course_installments;
--            DROP TABLE IF EXISTS charvak_course_payments;
--            DROP TABLE IF EXISTS charvak_course_prices;
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Tier-1 fixed regional prices (7 markets). Rest of world converts from
--    charvak_courses.price_inr via payment_engine.INR_RATES.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_course_prices (
    course_name     TEXT        NOT NULL,
    country_code    TEXT        NOT NULL,
    currency        TEXT        NOT NULL,
    amount_local    NUMERIC(10,2) NOT NULL,
    razorpay_paise  INTEGER,
    created_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (course_name, country_code)
);
CREATE INDEX IF NOT EXISTS idx_course_prices_country
    ON charvak_course_prices(country_code);

-- ---------------------------------------------------------------------------
-- 2. Course payments - one row per successful gateway payment.
--    razorpay_payment_id is the idempotency anchor (UNIQUE).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_course_payments (
    payment_id          TEXT PRIMARY KEY,
    enrollment_id       TEXT,
    email               TEXT        NOT NULL,
    course_name         TEXT        NOT NULL,
    country_code        TEXT,
    currency            TEXT        NOT NULL,
    amount_local        NUMERIC(10,2) NOT NULL,
    amount_inr          INTEGER     NOT NULL,
    payment_type        TEXT        NOT NULL,     -- 'full' | 'emi_installment'
    installment_num     INTEGER,                  -- NULL for full payment
    razorpay_payment_id TEXT UNIQUE,
    razorpay_order_id   TEXT,
    paypal_order_id     TEXT,
    gateway             TEXT        NOT NULL,     -- 'razorpay' | 'paypal'
    status              TEXT        NOT NULL DEFAULT 'pending',
    created_at          TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_course_payments_email
    ON charvak_course_payments(email);
CREATE INDEX IF NOT EXISTS idx_course_payments_enrollment
    ON charvak_course_payments(enrollment_id);
CREATE INDEX IF NOT EXISTS idx_course_payments_rzp
    ON charvak_course_payments(razorpay_payment_id);

-- ---------------------------------------------------------------------------
-- 3. Installment schedule - India EMI only. Each row unlocks a block of weeks.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS charvak_course_installments (
    installment_id      TEXT PRIMARY KEY,
    enrollment_id       TEXT    NOT NULL,
    email               TEXT    NOT NULL,
    installment_num     INTEGER NOT NULL,
    total_installments  INTEGER NOT NULL,
    amount_inr          INTEGER NOT NULL,
    unlocks_from_week   INTEGER NOT NULL,
    unlocks_to_week     INTEGER NOT NULL,
    due_week            INTEGER NOT NULL,
    due_date            DATE    NOT NULL,
    status              TEXT    NOT NULL DEFAULT 'pending',  -- pending|paid|overdue|paused
    paid_at             TIMESTAMP,
    payment_id          TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(enrollment_id, installment_num)
);
CREATE INDEX IF NOT EXISTS idx_course_installments_email
    ON charvak_course_installments(email);
CREATE INDEX IF NOT EXISTS idx_course_installments_status
    ON charvak_course_installments(status);

-- ============================================================================
-- SEED - Tier-1 fixed prices (25 courses x 7 markets)
-- INR is the catalog price (source of truth). Non-IN are PPP-rounded.
-- REVIEW these before running. Edit any row you disagree with.
-- ============================================================================
INSERT INTO charvak_course_prices (course_name, country_code, currency, amount_local, razorpay_paise) VALUES
-- Full Stack Web Development (INR 4999)
('Full Stack Web Development','IN','INR',4999,499900),
('Full Stack Web Development','US','USD',59.99,NULL),
('Full Stack Web Development','GB','GBP',44.99,NULL),
('Full Stack Web Development','EU','EUR',54.99,NULL),
('Full Stack Web Development','AE','AED',219.00,NULL),
('Full Stack Web Development','SG','SGD',79.99,NULL),
('Full Stack Web Development','AU','AUD',89.99,NULL),
-- Data Science & ML (INR 5999)
('Data Science & ML','IN','INR',5999,599900),
('Data Science & ML','US','USD',69.99,NULL),
('Data Science & ML','GB','GBP',54.99,NULL),
('Data Science & ML','EU','EUR',64.99,NULL),
('Data Science & ML','AE','AED',259.00,NULL),
('Data Science & ML','SG','SGD',94.99,NULL),
('Data Science & ML','AU','AUD',104.99,NULL),
-- Python Programming (INR 999)
('Python Programming','IN','INR',999,99900),
('Python Programming','US','USD',12.99,NULL),
('Python Programming','GB','GBP',9.99,NULL),
('Python Programming','EU','EUR',11.99,NULL),
('Python Programming','AE','AED',49.00,NULL),
('Python Programming','SG','SGD',16.99,NULL),
('Python Programming','AU','AUD',18.99,NULL),
-- AWS Cloud Computing (INR 3999)
('AWS Cloud Computing','IN','INR',3999,399900),
('AWS Cloud Computing','US','USD',49.99,NULL),
('AWS Cloud Computing','GB','GBP',37.99,NULL),
('AWS Cloud Computing','EU','EUR',45.99,NULL),
('AWS Cloud Computing','AE','AED',179.00,NULL),
('AWS Cloud Computing','SG','SGD',64.99,NULL),
('AWS Cloud Computing','AU','AUD',74.99,NULL),
-- DevOps Engineering (INR 4999)
('DevOps Engineering','IN','INR',4999,499900),
('DevOps Engineering','US','USD',59.99,NULL),
('DevOps Engineering','GB','GBP',44.99,NULL),
('DevOps Engineering','EU','EUR',54.99,NULL),
('DevOps Engineering','AE','AED',219.00,NULL),
('DevOps Engineering','SG','SGD',79.99,NULL),
('DevOps Engineering','AU','AUD',89.99,NULL),
-- Cybersecurity (INR 4999)
('Cybersecurity','IN','INR',4999,499900),
('Cybersecurity','US','USD',59.99,NULL),
('Cybersecurity','GB','GBP',44.99,NULL),
('Cybersecurity','EU','EUR',54.99,NULL),
('Cybersecurity','AE','AED',219.00,NULL),
('Cybersecurity','SG','SGD',79.99,NULL),
('Cybersecurity','AU','AUD',89.99,NULL),
-- Java Development (INR 2999)
('Java Development','IN','INR',2999,299900),
('Java Development','US','USD',34.99,NULL),
('Java Development','GB','GBP',27.99,NULL),
('Java Development','EU','EUR',32.99,NULL),
('Java Development','AE','AED',129.00,NULL),
('Java Development','SG','SGD',47.99,NULL),
('Java Development','AU','AUD',54.99,NULL),
-- React & Frontend (INR 2499)
('React & Frontend','IN','INR',2499,249900),
('React & Frontend','US','USD',29.99,NULL),
('React & Frontend','GB','GBP',22.99,NULL),
('React & Frontend','EU','EUR',27.99,NULL),
('React & Frontend','AE','AED',109.00,NULL),
('React & Frontend','SG','SGD',39.99,NULL),
('React & Frontend','AU','AUD',44.99,NULL),
-- SQL & Database (INR 999)
('SQL & Database','IN','INR',999,99900),
('SQL & Database','US','USD',12.99,NULL),
('SQL & Database','GB','GBP',9.99,NULL),
('SQL & Database','EU','EUR',11.99,NULL),
('SQL & Database','AE','AED',49.00,NULL),
('SQL & Database','SG','SGD',16.99,NULL),
('SQL & Database','AU','AUD',18.99,NULL),
-- Docker & Kubernetes (INR 2499)
('Docker & Kubernetes','IN','INR',2499,249900),
('Docker & Kubernetes','US','USD',29.99,NULL),
('Docker & Kubernetes','GB','GBP',22.99,NULL),
('Docker & Kubernetes','EU','EUR',27.99,NULL),
('Docker & Kubernetes','AE','AED',109.00,NULL),
('Docker & Kubernetes','SG','SGD',39.99,NULL),
('Docker & Kubernetes','AU','AUD',44.99,NULL),
-- AI & Deep Learning (INR 6999)
('AI & Deep Learning','IN','INR',6999,699900),
('AI & Deep Learning','US','USD',79.99,NULL),
('AI & Deep Learning','GB','GBP',62.99,NULL),
('AI & Deep Learning','EU','EUR',74.99,NULL),
('AI & Deep Learning','AE','AED',299.00,NULL),
('AI & Deep Learning','SG','SGD',109.99,NULL),
('AI & Deep Learning','AU','AUD',119.99,NULL),
-- Mobile App Development (INR 3999)
('Mobile App Development','IN','INR',3999,399900),
('Mobile App Development','US','USD',49.99,NULL),
('Mobile App Development','GB','GBP',37.99,NULL),
('Mobile App Development','EU','EUR',45.99,NULL),
('Mobile App Development','AE','AED',179.00,NULL),
('Mobile App Development','SG','SGD',64.99,NULL),
('Mobile App Development','AU','AUD',74.99,NULL),
-- Blockchain Development (INR 4999)
('Blockchain Development','IN','INR',4999,499900),
('Blockchain Development','US','USD',59.99,NULL),
('Blockchain Development','GB','GBP',44.99,NULL),
('Blockchain Development','EU','EUR',54.99,NULL),
('Blockchain Development','AE','AED',219.00,NULL),
('Blockchain Development','SG','SGD',79.99,NULL),
('Blockchain Development','AU','AUD',89.99,NULL),
-- Data Analytics (INR 2999)
('Data Analytics','IN','INR',2999,299900),
('Data Analytics','US','USD',34.99,NULL),
('Data Analytics','GB','GBP',27.99,NULL),
('Data Analytics','EU','EUR',32.99,NULL),
('Data Analytics','AE','AED',129.00,NULL),
('Data Analytics','SG','SGD',47.99,NULL),
('Data Analytics','AU','AUD',54.99,NULL),
-- UI/UX Design (INR 1999)
('UI/UX Design','IN','INR',1999,199900),
('UI/UX Design','US','USD',24.99,NULL),
('UI/UX Design','GB','GBP',18.99,NULL),
('UI/UX Design','EU','EUR',22.99,NULL),
('UI/UX Design','AE','AED',89.00,NULL),
('UI/UX Design','SG','SGD',32.99,NULL),
('UI/UX Design','AU','AUD',37.99,NULL),
-- Cloud Architecture (INR 5999)
('Cloud Architecture','IN','INR',5999,599900),
('Cloud Architecture','US','USD',69.99,NULL),
('Cloud Architecture','GB','GBP',54.99,NULL),
('Cloud Architecture','EU','EUR',64.99,NULL),
('Cloud Architecture','AE','AED',259.00,NULL),
('Cloud Architecture','SG','SGD',94.99,NULL),
('Cloud Architecture','AU','AUD',104.99,NULL),
-- Node.js Backend (INR 2499)
('Node.js Backend','IN','INR',2499,249900),
('Node.js Backend','US','USD',29.99,NULL),
('Node.js Backend','GB','GBP',22.99,NULL),
('Node.js Backend','EU','EUR',27.99,NULL),
('Node.js Backend','AE','AED',109.00,NULL),
('Node.js Backend','SG','SGD',39.99,NULL),
('Node.js Backend','AU','AUD',44.99,NULL),
-- Python for Data Science (INR 3999)
('Python for Data Science','IN','INR',3999,399900),
('Python for Data Science','US','USD',49.99,NULL),
('Python for Data Science','GB','GBP',37.99,NULL),
('Python for Data Science','EU','EUR',45.99,NULL),
('Python for Data Science','AE','AED',179.00,NULL),
('Python for Data Science','SG','SGD',64.99,NULL),
('Python for Data Science','AU','AUD',74.99,NULL),
-- Machine Learning Ops (INR 4999)
('Machine Learning Ops','IN','INR',4999,499900),
('Machine Learning Ops','US','USD',59.99,NULL),
('Machine Learning Ops','GB','GBP',44.99,NULL),
('Machine Learning Ops','EU','EUR',54.99,NULL),
('Machine Learning Ops','AE','AED',219.00,NULL),
('Machine Learning Ops','SG','SGD',79.99,NULL),
('Machine Learning Ops','AU','AUD',89.99,NULL),
-- Spring Boot (INR 2499)
('Spring Boot','IN','INR',2499,249900),
('Spring Boot','US','USD',29.99,NULL),
('Spring Boot','GB','GBP',22.99,NULL),
('Spring Boot','EU','EUR',27.99,NULL),
('Spring Boot','AE','AED',109.00,NULL),
('Spring Boot','SG','SGD',39.99,NULL),
('Spring Boot','AU','AUD',44.99,NULL),
-- Angular Development (INR 1999)
('Angular Development','IN','INR',1999,199900),
('Angular Development','US','USD',24.99,NULL),
('Angular Development','GB','GBP',18.99,NULL),
('Angular Development','EU','EUR',22.99,NULL),
('Angular Development','AE','AED',89.00,NULL),
('Angular Development','SG','SGD',32.99,NULL),
('Angular Development','AU','AUD',37.99,NULL),
-- Ethical Hacking (INR 5999)
('Ethical Hacking','IN','INR',5999,599900),
('Ethical Hacking','US','USD',69.99,NULL),
('Ethical Hacking','GB','GBP',54.99,NULL),
('Ethical Hacking','EU','EUR',64.99,NULL),
('Ethical Hacking','AE','AED',259.00,NULL),
('Ethical Hacking','SG','SGD',94.99,NULL),
('Ethical Hacking','AU','AUD',104.99,NULL),
-- Big Data (INR 4999)
('Big Data','IN','INR',4999,499900),
('Big Data','US','USD',59.99,NULL),
('Big Data','GB','GBP',44.99,NULL),
('Big Data','EU','EUR',54.99,NULL),
('Big Data','AE','AED',219.00,NULL),
('Big Data','SG','SGD',79.99,NULL),
('Big Data','AU','AUD',89.99,NULL),
-- Software Testing (INR 999)
('Software Testing','IN','INR',999,99900),
('Software Testing','US','USD',12.99,NULL),
('Software Testing','GB','GBP',9.99,NULL),
('Software Testing','EU','EUR',11.99,NULL),
('Software Testing','AE','AED',49.00,NULL),
('Software Testing','SG','SGD',16.99,NULL),
('Software Testing','AU','AUD',18.99,NULL),
-- Git & DevOps Tools (INR 499)
('Git & DevOps Tools','IN','INR',499,49900),
('Git & DevOps Tools','US','USD',6.99,NULL),
('Git & DevOps Tools','GB','GBP',5.99,NULL),
('Git & DevOps Tools','EU','EUR',6.99,NULL),
('Git & DevOps Tools','AE','AED',29.00,NULL),
('Git & DevOps Tools','SG','SGD',8.99,NULL),
('Git & DevOps Tools','AU','AUD',9.99,NULL)
ON CONFLICT (course_name, country_code) DO NOTHING;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 4. Race-safety + lifecycle indexes (added 2026-09-16)
-- ---------------------------------------------------------------------------
-- Prevent a webhook+callback race from double-marking an installment paid.
CREATE UNIQUE INDEX IF NOT EXISTS uq_course_installment_paid
    ON charvak_course_installments(enrollment_id, installment_num)
    WHERE status = 'paid';

-- Fast lookup of abandoned pending enrollments (cleanup sweep).
CREATE INDEX IF NOT EXISTS idx_course_enrollments_pending
    ON charvak_enrollments(status) WHERE status = 'pending_payment';

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
-- ---------------------------------------------------------------------------
-- 5. Reminder dedupe (added 2026-09-16)
-- Tracks which reminder stage (t_minus_3, due, overdue_1, overdue_3, overdue_7)
-- was last sent for each installment so the cron doesn't spam.
-- ---------------------------------------------------------------------------
ALTER TABLE charvak_course_installments
    ADD COLUMN IF NOT EXISTS last_reminder_stage TEXT;

CREATE INDEX IF NOT EXISTS idx_course_installments_reminder
    ON charvak_course_installments(status, due_date)
    WHERE status IN ('pending', 'overdue');
-- ---------------------------------------------------------------------------
-- 6. Access-attempt reminder throttle (added 2026-09-16)
-- Tracks when we last sent the "you tried to open a locked week" email so
-- we throttle to at most one per 24h per installment.
-- ---------------------------------------------------------------------------
ALTER TABLE charvak_course_installments
    ADD COLUMN IF NOT EXISTS last_access_reminder_at TIMESTAMP;