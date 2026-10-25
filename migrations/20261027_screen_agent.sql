-- 20261027_screen_agent.sql
-- F3: Enterprise AI recruiter screen agent
-- Idempotent. Run on both local and prod.

CREATE TABLE IF NOT EXISTS charvak_screen_sessions (
  session_id TEXT PRIMARY KEY,
  recruiter_email TEXT NOT NULL,
  role_id TEXT,
  jd_text TEXT,
  parsed_jd JSONB,
  role_title TEXT,
  company_name TEXT,
  status TEXT DEFAULT 'active',
  candidates_invited INTEGER DEFAULT 0,
  candidates_responded INTEGER DEFAULT 0,
  candidates_qualified INTEGER DEFAULT 0,
  budget_max_inr INTEGER,
  consent_text TEXT,
  language TEXT DEFAULT 'en',
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_screen_sessions_recruiter ON charvak_screen_sessions(LOWER(recruiter_email));
CREATE INDEX IF NOT EXISTS idx_screen_sessions_status ON charvak_screen_sessions(status);

CREATE TABLE IF NOT EXISTS charvak_screen_candidates (
  candidate_screen_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES charvak_screen_sessions(session_id),
  token TEXT UNIQUE NOT NULL,
  candidate_email TEXT NOT NULL,
  candidate_name TEXT,
  status TEXT DEFAULT 'invited',
  invited_at TIMESTAMP DEFAULT NOW(),
  first_response_at TIMESTAMP,
  completed_at TIMESTAMP,
  captured_data JSONB,
  qualification_score INTEGER,
  qualified BOOLEAN,
  disqualify_reason TEXT,
  language TEXT DEFAULT 'en',
  consent_given_at TIMESTAMP,
  consent_ip TEXT
);
CREATE INDEX IF NOT EXISTS idx_screen_candidates_token ON charvak_screen_candidates(token);
CREATE INDEX IF NOT EXISTS idx_screen_candidates_session ON charvak_screen_candidates(session_id);
CREATE INDEX IF NOT EXISTS idx_screen_candidates_status ON charvak_screen_candidates(status);

CREATE TABLE IF NOT EXISTS charvak_screen_messages (
  message_id TEXT PRIMARY KEY,
  candidate_screen_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  field_name TEXT,
  field_value TEXT,
  language TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_screen_messages_candidate ON charvak_screen_messages(candidate_screen_id, created_at);

CREATE TABLE IF NOT EXISTS charvak_screen_schedules (
  schedule_id TEXT PRIMARY KEY,
  candidate_screen_id TEXT NOT NULL,
  proposed_slots JSONB,
  selected_slot JSONB,
  scheduled_at TIMESTAMP,
  calendar_link TEXT,
  recruiter_notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_screen_schedules_candidate ON charvak_screen_schedules(candidate_screen_id);

CREATE TABLE IF NOT EXISTS charvak_screen_events (
  event_id TEXT PRIMARY KEY,
  candidate_screen_id TEXT,
  session_id TEXT,
  event_type TEXT NOT NULL,
  event_data JSONB,
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_screen_events_candidate ON charvak_screen_events(candidate_screen_id);
CREATE INDEX IF NOT EXISTS idx_screen_events_type ON charvak_screen_events(event_type);