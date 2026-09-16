# Charvak Persistence Project — Master Plan

**Created:** 2026-09-17
**Purpose:** Persist all 41 in-memory engines to Postgres
**Total estimate:** ~32 hours across 8 sessions

## Tier A — Revenue + user-critical (fix first)

| # | Engine | Sessions | Status |
|---|---|---|---|
| 1 | kyc_engine | A | pending |
| 2 | candidate_engine | A | pending |
| 3 | training_engine | A | pending |
| 4 | lms_engine | A | pending |
| 5 | enterprise_engine | B | pending |
| 6 | ats_engine | B | pending |
| 7 | voice_to_web_engine | B | pending |
| 8 | career_v2_engine | C | pending |
| 9 | exam_prep_engine | C | pending |
| 10 | events_engine | C | pending |

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

## Pattern (proven 4x)

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
