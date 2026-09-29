-- 20260930_micro_squad_leads.sql
-- Lead capture for the Micro-Squads Rs 49,999 sales tier.
-- Not a paid feature - a sales conversation flow.

CREATE TABLE IF NOT EXISTS charvak_micro_squad_leads (
    lead_id         TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    email           TEXT NOT NULL,
    phone           TEXT,
    company         TEXT,
    requirement     TEXT,
    project_type    TEXT,
    duration_days   INTEGER,
    budget          INTEGER,
    squad_id        TEXT,
    source          TEXT DEFAULT 'micro-squads',
    status          TEXT DEFAULT 'new',
    contacted_at    TIMESTAMP,
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_micro_squad_leads_email
    ON charvak_micro_squad_leads (email, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_micro_squad_leads_status
    ON charvak_micro_squad_leads (status, created_at DESC);
