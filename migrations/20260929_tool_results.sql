-- 20260929_tool_results.sql
-- Persist every AI Tools Suite run so users can browse history.
-- Non-fatal: if this table doesn't exist, tools still work.

CREATE TABLE IF NOT EXISTS charvak_tool_results (
    result_id     TEXT PRIMARY KEY,
    email         TEXT NOT NULL,
    tool_name     TEXT NOT NULL,
    inputs_json   JSONB,
    result_json   JSONB,
    credits_used  INTEGER NOT NULL DEFAULT 0,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tool_results_email
    ON charvak_tool_results (email);

CREATE INDEX IF NOT EXISTS idx_tool_results_email_created
    ON charvak_tool_results (email, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_tool_results_email_tool
    ON charvak_tool_results (email, tool_name, created_at DESC);
