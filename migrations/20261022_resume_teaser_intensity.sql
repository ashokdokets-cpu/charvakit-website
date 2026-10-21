-- Session 73+ (2026-10-22): Add intensity selector to resume teasers
-- Tracks which intensity level (clean/mild/savage) was requested.
-- Enables analytics: which intensity converts best? Which drives more shares?

ALTER TABLE charvak_resume_teasers 
ADD COLUMN IF NOT EXISTS intensity TEXT DEFAULT 'mild';

-- Index for analytics queries (which intensity drives most shares/unlocks?)
CREATE INDEX IF NOT EXISTS idx_resume_teasers_intensity 
ON charvak_resume_teasers (intensity);
