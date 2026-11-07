-- 20261108b_api_sources.sql
-- Adds 6 new job board API sources to the registry.
-- Idempotent: safe to run multiple times.

INSERT INTO charvak_job_sources
    (source_name, display_name, api_url, attribution_text, active)
VALUES
    ('remoteok', 'RemoteOK', 'https://remoteok.com/api',
     'Job data from RemoteOK (https://remoteok.com)', TRUE),
    ('weworkremotely', 'We Work Remotely', 'https://weworkremotely.com/categories/remote-programming-jobs.rss',
     'Job data from We Work Remotely (https://weworkremotely.com)', TRUE),
    ('jobicy', 'Jobicy', 'https://jobicy.com/api/v2/remote-jobs',
     'Job data from Jobicy (https://jobicy.com)', TRUE),
    ('himalayas', 'Himalayas', 'https://himalayas.app/jobs/api',
     'Job data from Himalayas (https://himalayas.app)', TRUE),
    ('themuse', 'The Muse', 'https://www.themuse.com/api/public/jobs',
     'Job data from The Muse (https://www.themuse.com)', TRUE),
    ('hn_hiring', 'HN Who is Hiring', 'https://hn.algolia.com/api/v1/search',
     'Job data from Hacker News "Who is Hiring" threads (https://news.ycombinator.com)', TRUE)
ON CONFLICT (source_name) DO NOTHING;