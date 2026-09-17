# Charvak Persistence Project — Master Plan

**Created:** 2026-09-17
**Updated:** 2026-09-18 (after Session D)
**Purpose:** Persist all 41 in-memory engines to Postgres
**Total estimate:** ~32 hours across 8 sessions
**Progress:** 26/41 engines persisted (Sessions A, C, D, E, F, G complete)

## Tier A — Revenue + user-critical (fix first)

| # | Engine | Sessions | Status |
|---|---|---|---|
| 1 | kyc_engine | A | ✅ merged (#5) |
| 2 | candidate_engine | A | ✅ merged (#6) |
| 3 | training_engine | A | ✅ merged (#7) |
| 4 | lms_engine | A | ✅ merged (#8) |
| 5 | enterprise_engine | B | pending |
| 6 | ats_engine | B | pending |
| 7 | voice_to_web_engine | B | pending |
| 8 | career_v2_engine | C | ✅ merged (#10) |
| 9 | exam_prep_engine | C | ✅ merged (#11 engine, #12 routes) |
| 10 | events_engine | C | ✅ merged (#9) |

## Tier B — User-facing (fix next)

| # | Engine | Session |
|---|---|---|
| 11-15 | messaging, profile_network, badge, university, brand | D |
| 16-19 | final_year_project, student_suite, ai_internship, team | E |
| 20-23 | outreach, marketing_ai, exam_analytics, dynamic_role | F |

## Tier C — NA module (B2B)

| # | Engine | Session |
|---|---|---|
| 24-29 | 6 NA module engines | G |

## Tier D — Ephemeral (tolerable loss)

| # | Engine | Session |
|---|---|---|
| 30-37 | chatbot, bridges, assessment engines, training_mapping | H |

## Tier E — Internal (skip)

- payment_engine (log only — real data in DB)
- notification_engine (email log)
- products_engine (logic only)
- tools_engine (analytics log)

## Pattern (proven 7x)

For each engine:
1. Read current file, identify in-memory vars
2. Design Postgres tables (2-4 per engine)
3. Write migration SQL
4. Apply migration + verify
5. Refactor engine methods (whole-method replacement via Python patch)
6. E2E test
7. Commit + PR + deploy + verify

## Session A — Start here

Engines: kyc, candidate, training, lms
Estimate: 4 hours
Branch: persist-batch-a

## Session status

| Session | Engines | Status |
|---|---|---|
| A | kyc, candidate, training, lms | ✅ done (PRs #5–8) |
| B | enterprise, ats, voice_to_web | ⏳ |
| C | events, career_v2, exam_prep | ✅ done (PRs #9–12) |
| D | messaging, profile_network, badge, university, brand | ✅ done (PR #19) |
| E | final_year_project, student_suite, ai_internship, team | ✅ done (PRs #13–16) |
| F | outreach, marketing_ai, exam_analytics, dynamic_role | ✅ done (PR #18) |
| G | na_module: vector_matcher, vms_connector, revenue_engine, resume_engine, work_auth, charvak_vms | ✅ done (PR #17) |
| H | 8 ephemeral engines | ⏳ |

## Lessons learned

1. **PowerShell + `curl.exe` + JSON body** → always use `--data-binary @file.json`. Single-quoted JSON still gets mangled by PowerShell's native-arg passing.
2. **PowerShell + `python -c "..."`** with nested quotes → always write a temp `.py` file (and strip the BOM if you used `Out-File -Encoding utf8`).
3. **`Out-File -Encoding utf8` adds a BOM** → Python will choke on it. Use `[System.IO.File]::WriteAllText(path, content, (New-Object System.Text.UTF8Encoding($false)))` or strip bytes 0–2.
4. **Smoke tests against prod are dangerous** → we now have a local Postgres 15. See `DEV-SETUP.md`.
5. **Migration file ordering** — `20260916_course_payments.sql` references `charvak_enrollments` which no migration creates (was created by an ad-hoc script on prod). Fresh-clone / DR restore will fail. Backfill this migration in Session I.
