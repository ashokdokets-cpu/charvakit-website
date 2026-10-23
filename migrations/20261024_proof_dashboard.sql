-- 20261024_proof_dashboard.sql
-- Proof Dashboard: certificate view tracking + institution rollup
-- Idempotent. Safe to run multiple times.

CREATE TABLE IF NOT EXISTS charvak_certificate_views (
    view_id TEXT PRIMARY KEY,
    certificate_id TEXT NOT NULL,
    viewer_ip_hash TEXT,
    viewer_type TEXT DEFAULT 'anonymous',   -- anonymous | employer | dean | admin
    viewer_email TEXT,
    user_agent TEXT,
    referrer TEXT,
    university_id TEXT,                     -- if known (from cert's owning institution)
    viewed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cert_views_cert
    ON charvak_certificate_views (certificate_id, viewed_at DESC);

CREATE INDEX IF NOT EXISTS idx_cert_views_university
    ON charvak_certificate_views (university_id, viewed_at DESC);

CREATE INDEX IF NOT EXISTS idx_cert_views_type
    ON charvak_certificate_views (viewer_type, viewed_at DESC);

-- Optional: link student email -> institution for faster rollups
CREATE INDEX IF NOT EXISTS idx_univ_students_email
    ON charvak_university_students (email) WHERE email IS NOT NULL;