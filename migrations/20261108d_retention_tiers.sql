-- 20261108d_retention_tiers.sql
-- Granular retention tiers for rejected JDs
-- Aggressive purge for useless rejections, patient retention for tuning signals

INSERT INTO charvak_retention_config
    (config_key, retention_days, enabled, min_rows_to_keep, description)
VALUES
    ('rejected_low_skill_0', 2, TRUE, 0,
     'Rejected JDs with 0% skill overlap — useless after 2 days'),
    ('rejected_non_us_location', 3, TRUE, 0,
     'Rejected JDs with non-US location — filter is stable, purge after 3 days'),
    ('rejected_visa_mismatch', 7, TRUE, 0,
     'Rejected JDs with visa mismatch — worth reviewing for visa-list tuning'),
    ('rejected_partial_overlap', 14, TRUE, 0,
     'Rejected JDs with 1-29% overlap — tuning value, keep 14 days'),
    ('rejected_low_skill_0_special', 2, FALSE, 0,
     'Reserved: 0% overlap from tech-only sources'),
    ('rejected_old_cutoff', 30, TRUE, 0,
     'Absolute max age for any rejection row — safety net')
ON CONFLICT (config_key) DO NOTHING;