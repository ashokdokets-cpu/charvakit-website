-- Voice-to-Web Pro Engine persistence (C2, 2026-09-25)
-- Migrates 5 in-memory stores to Postgres.

CREATE TABLE IF NOT EXISTS charvak_voice_to_web_sites (
    website_id       TEXT PRIMARY KEY,
    email            TEXT NOT NULL,
    business_name    TEXT NOT NULL,
    plan             TEXT DEFAULT 'free',
    transcript       TEXT DEFAULT '',
    custom_domain    TEXT,
    branding         TEXT DEFAULT 'charvak',
    seo_enabled      BOOLEAN DEFAULT FALSE,
    updates_enabled  BOOLEAN DEFAULT FALSE,
    priority_support BOOLEAN DEFAULT FALSE,
    status           TEXT DEFAULT 'live',
    url              TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_v2w_sites_email ON charvak_voice_to_web_sites(email);
CREATE INDEX IF NOT EXISTS idx_v2w_sites_plan  ON charvak_voice_to_web_sites(plan);

CREATE TABLE IF NOT EXISTS charvak_voice_to_web_domains (
    website_id     TEXT PRIMARY KEY REFERENCES charvak_voice_to_web_sites(website_id) ON DELETE CASCADE,
    domain         TEXT NOT NULL,
    status         TEXT DEFAULT 'pending_setup',
    dns_configured BOOLEAN DEFAULT FALSE,
    ssl_active     BOOLEAN DEFAULT FALSE,
    setup_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS charvak_voice_to_web_updates (
    update_id            TEXT PRIMARY KEY,
    website_id           TEXT NOT NULL REFERENCES charvak_voice_to_web_sites(website_id) ON DELETE CASCADE,
    type                 TEXT,
    details              TEXT,
    email                TEXT DEFAULT '',
    status               TEXT DEFAULT 'queued',
    priority             TEXT DEFAULT 'normal',
    requested_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estimated_completion TEXT DEFAULT '24 hours'
);
CREATE INDEX IF NOT EXISTS idx_v2w_updates_site ON charvak_voice_to_web_updates(website_id);

CREATE TABLE IF NOT EXISTS charvak_voice_to_web_tickets (
    ticket_id     TEXT PRIMARY KEY,
    email         TEXT NOT NULL,
    issue         TEXT NOT NULL,
    website_id    TEXT REFERENCES charvak_voice_to_web_sites(website_id) ON DELETE SET NULL,
    priority      TEXT DEFAULT 'normal',
    status        TEXT DEFAULT 'open',
    response_time TEXT DEFAULT '24 hours',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_v2w_tickets_site  ON charvak_voice_to_web_tickets(website_id);
CREATE INDEX IF NOT EXISTS idx_v2w_tickets_email ON charvak_voice_to_web_tickets(email);

CREATE TABLE IF NOT EXISTS charvak_voice_to_web_seo (
    website_id       TEXT PRIMARY KEY REFERENCES charvak_voice_to_web_sites(website_id) ON DELETE CASCADE,
    meta_title       TEXT,
    meta_description TEXT,
    keywords         JSONB DEFAULT '[]'::jsonb,
    og_tags          BOOLEAN DEFAULT TRUE,
    twitter_cards    BOOLEAN DEFAULT TRUE,
    sitemap          BOOLEAN DEFAULT TRUE,
    robots_txt       BOOLEAN DEFAULT TRUE,
    structured_data  JSONB DEFAULT '{}'::jsonb,
    enabled_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);