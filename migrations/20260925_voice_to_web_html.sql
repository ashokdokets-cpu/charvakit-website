-- Voice-to-Web Option 2: store generated HTML + human-readable slug
-- Idempotent. Safe to run multiple times.

ALTER TABLE charvak_voice_to_web_sites
  ADD COLUMN IF NOT EXISTS html_content TEXT,
  ADD COLUMN IF NOT EXISTS slug TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS idx_v2w_sites_slug
  ON charvak_voice_to_web_sites(slug)
  WHERE slug IS NOT NULL;