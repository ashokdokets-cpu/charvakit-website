-- 20260930_lms_enrollments.sql
-- LMS course enrollment. Reuses the charvak_courses catalog (25 courses).
-- Credits charged = course price_inr / 5.

CREATE TABLE IF NOT EXISTS charvak_lms_enrollments (
    enrollment_id   TEXT PRIMARY KEY,
    email           TEXT NOT NULL,
    course_id       TEXT NOT NULL,
    course_name     TEXT,
    price_inr       INTEGER,
    credits_used    INTEGER NOT NULL DEFAULT 0,
    enrolled_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP,
    UNIQUE (email, course_id)
);

CREATE INDEX IF NOT EXISTS idx_lms_enrollments_email
    ON charvak_lms_enrollments (email, enrolled_at DESC);
CREATE INDEX IF NOT EXISTS idx_lms_enrollments_course
    ON charvak_lms_enrollments (course_id);
