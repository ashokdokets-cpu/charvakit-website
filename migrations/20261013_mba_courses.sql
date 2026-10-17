-- ============================================================
-- Session 43-C: 10 MBA-relevant catalog courses
-- ============================================================
-- Adds the Business category to the AI course catalog. These are
-- the courses MBA students need for placement season — case study,
-- consulting math, business communication, and more.

-- Session 47.5: ensure generated-course columns exist before the INSERT.
-- These are normally added by ai_courses._ensure_tables() at runtime on
-- prod, but on a fresh DB they may be missing. All adds are idempotent.

DO $mba$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema='public' AND table_name='charvak_courses'
                     AND column_name='is_custom') THEN
        ALTER TABLE charvak_courses ADD COLUMN is_custom BOOLEAN DEFAULT FALSE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema='public' AND table_name='charvak_courses'
                     AND column_name='generated_for_email') THEN
        ALTER TABLE charvak_courses ADD COLUMN generated_for_email TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema='public' AND table_name='charvak_courses'
                     AND column_name='generated_from_topic') THEN
        ALTER TABLE charvak_courses ADD COLUMN generated_from_topic TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema='public' AND table_name='charvak_courses'
                     AND column_name='generated_at') THEN
        ALTER TABLE charvak_courses ADD COLUMN generated_at TIMESTAMP;
    END IF;
END $mba$;

INSERT INTO charvak_courses
    (course_id, course_name, category, level, description, price_inr, duration_weeks, status, is_custom)
VALUES
    ('CRS-MBA-0001', 'Case Study Fundamentals', 'Business', 'Beginner',
     'Learn the framework for cracking consulting case interviews — market sizing, profitability, and business situations. Directly prepares for Deloitte, KPMG, EY, and PwC interview rounds.',
     1999, 4, 'active', FALSE),
    ('CRS-MBA-0002', 'Consulting Case Frameworks', 'Business', 'Intermediate',
     'Master the 3C, 4P, profitability, and value-chain frameworks used in top-tier consulting interviews. Includes 20+ practice cases with AI-scored solutions.',
     2999, 6, 'active', FALSE),
    ('CRS-MBA-0003', 'Business Communication', 'Business', 'Beginner',
     'Write clearer emails, deliver stronger presentations, and speak with confidence in client-facing situations. Core skill for every placement interview.',
     1499, 3, 'active', FALSE),
    ('CRS-MBA-0004', 'Data Interpretation for Managers', 'Business', 'Beginner',
     'Read charts, tables, and dashboards with confidence. Interpret data to make faster, better business decisions — the most tested skill in MBA placement aptitude rounds.',
     1499, 3, 'active', FALSE),
    ('CRS-MBA-0005', 'Marketing Analytics', 'Business', 'Intermediate',
     'Measure campaign ROI, build attribution models, and use analytics to grow D2C and FMCG businesses. Prepares for marketing roles at top consumer brands.',
     2499, 5, 'active', FALSE),
    ('CRS-MBA-0006', 'Financial Modelling in Excel', 'Business', 'Intermediate',
     'Build three-statement financial models, DCF valuations, and scenario analyses. Prepares for finance analyst, investment banking, and PE/VC roles.',
     3499, 6, 'active', FALSE),
    ('CRS-MBA-0007', 'Product Management Fundamentals', 'Business', 'Beginner',
     'Frameworks for product discovery, prioritisation, roadmapping, and metrics. Directly prepares for Product Manager interviews at Amazon, Google, and Microsoft.',
     2499, 4, 'active', FALSE),
    ('CRS-MBA-0008', 'Consulting Math', 'Business', 'Beginner',
     'Fast, accurate calculation for consulting interviews — market sizing, profitability math, break-even analysis, and estimation questions.',
     1499, 3, 'active', FALSE),
    ('CRS-MBA-0009', 'Strategy Frameworks', 'Business', 'Intermediate',
     'Porter''s 5 Forces, SWOT, value chain, and competitive positioning. The frameworks every strategy interview expects you to know cold.',
     2499, 4, 'active', FALSE),
    ('CRS-MBA-0010', 'Business Ethics & Compliance', 'Business', 'Beginner',
     'Understand corporate governance, compliance frameworks, and ethical decision-making. Prepares for compliance rounds at MNCs and financial services firms.',
     1999, 3, 'active', FALSE)
ON CONFLICT DO NOTHING;