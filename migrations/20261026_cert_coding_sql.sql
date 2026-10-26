-- Coding/SQL Certificate Extension (Batch A8)
-- Idempotent — safe to re-run.
-- Applied to prod on 2026-10-26. Keep this file for fresh-clone rebuilds.

-- Ensure base cert table exists (canonical schema)
CREATE TABLE IF NOT EXISTS charvak_career_certifications (
  cert_id text PRIMARY KEY,
  assessment_id text NOT NULL,
  email text NOT NULL,
  display_name text,
  role text NOT NULL,
  industry text,
  level text,
  score integer,
  passed boolean DEFAULT true,
  badge_tier text,
  certification_hash text NOT NULL,
  credits_charged integer DEFAULT 0,
  integrity_summary jsonb DEFAULT '{}'::jsonb,
  issued_at timestamp DEFAULT CURRENT_TIMESTAMP,
  revoked_at timestamp
);

-- Add new coding/sql columns (idempotent)
ALTER TABLE charvak_career_certifications
  ADD COLUMN IF NOT EXISTS format text DEFAULT 'mcq',
  ADD COLUMN IF NOT EXISTS language text,
  ADD COLUMN IF NOT EXISTS database_name text,
  ADD COLUMN IF NOT EXISTS task_classes jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS runtime_info text;

-- Task class catalog
CREATE TABLE IF NOT EXISTS charvak_cert_task_classes (
  class_id text PRIMARY KEY,
  format text NOT NULL,
  language text,
  database_name text,
  class_key text NOT NULL,
  class_label text NOT NULL,
  description text,
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_cert_tc_format ON charvak_cert_task_classes(format);
CREATE INDEX IF NOT EXISTS idx_cert_tc_lang ON charvak_cert_task_classes(format, language);
CREATE INDEX IF NOT EXISTS idx_cert_tc_db ON charvak_cert_task_classes(format, database_name);

-- Seed coding task classes
INSERT INTO charvak_cert_task_classes
  (class_id, format, language, class_key, class_label, description)
VALUES
  ('TC-C-PY-ARRAYS','coding','python','arrays','Arrays & Lists','Array manipulation, indexing, slicing'),
  ('TC-C-PY-STRINGS','coding','python','strings','Strings','String parsing, formatting, manipulation'),
  ('TC-C-PY-DICTS','coding','python','dicts','Dictionaries & Sets','Hash-based data structures'),
  ('TC-C-PY-ALGO','coding','python','algorithms','Algorithms','Sorting, searching, complexity'),
  ('TC-C-PY-RECUR','coding','python','recursion','Recursion','Recursive problem solving'),
  ('TC-C-PY-DS','coding','python','data_structures','Data Structures','Stacks, queues, trees, graphs'),
  ('TC-C-PY-BIGNUM','coding','python','big_numbers','Big Integers','Arbitrary precision arithmetic'),
  ('TC-C-PY-EDGE','coding','python','edge_cases','Edge Case Handling','Empty input, boundary values'),
  ('TC-C-PY-CLEAN','coding','python','code_quality','Code Quality','Readability, naming, DRY'),
  ('TC-C-PY-EFF','coding','python','efficiency','Efficiency','Time/space complexity')
ON CONFLICT (class_id) DO NOTHING;

-- Seed SQL task classes
INSERT INTO charvak_cert_task_classes
  (class_id, format, database_name, class_key, class_label, description)
VALUES
  ('TC-S-SQLITE-JOIN','sql','sqlite','joins','JOIN Operations','INNER/LEFT/RIGHT/FULL joins'),
  ('TC-S-SQLITE-AGG','sql','sqlite','aggregation','Aggregation','GROUP BY, HAVING, aggregate functions'),
  ('TC-S-SQLITE-SUB','sql','sqlite','subqueries','Subqueries','Nested SELECT, correlated subqueries'),
  ('TC-S-SQLITE-WIN','sql','sqlite','window_fns','Window Functions','ROW_NUMBER, RANK, LAG/LEAD'),
  ('TC-S-SQLITE-CTE','sql','sqlite','ctes','Common Table Expressions','WITH clauses, recursive CTEs'),
  ('TC-S-SQLITE-CASE','sql','sqlite','case_when','CASE Expressions','Conditional logic in SQL'),
  ('TC-S-SQLITE-DATE','sql','sqlite','date_fns','Date Functions','Date manipulation, formatting'),
  ('TC-S-SQLITE-INDEX','sql','sqlite','optimization','Query Optimization','Index awareness, EXPLAIN awareness'),
  ('TC-S-SQLITE-EDGE','sql','sqlite','edge_cases','Edge Cases','NULL handling, empty sets')
ON CONFLICT (class_id) DO NOTHING;