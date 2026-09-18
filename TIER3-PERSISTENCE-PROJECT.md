# Charvak Persistence Project — Master Plan

**Created:** 2026-09-17
**Updated:** 2026-09-18 (after Session H)
**Purpose:** Persist all in-memory engines to Postgres
**Total estimate:** ~32 hours across 8+ sessions
**Progress:** 41/62 engines DB-backed; 9 verified skip; ~11 remaining (Sessions B, J)
**Note:** the original audit ("41 in-memory engines") counted only URL-reachable engines. A 2026-09-18 re-audit found ~62 engine-like files total, of which some were already DB-backed and others are stateless. See "Audit reconciliation" below.

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

## Tier E — Internal (verified 2026-09-18)

| Engine | Verdict |
|---|---|
| payment_engine | ⚠️ Fixed — see PR (log now persisted to `charvak_payment_log`) |
| notification_engine | ✅ Verified skip — SendGrid is the durable state |
| products_engine | ✅ Verified skip — `self.results` is a dead field |
| tools_ai_backend | ✅ Verified skip — completely stateless |


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
| H | chatbot, bridge, ai_bridge, advanced_assessment, enhanced_assessment, company_content, assessment_report, training_mapping | ✅ done (PR #21) |

## Lessons learned

1. **PowerShell + `curl.exe` + JSON body** → always use `--data-binary @file.json`. Single-quoted JSON still gets mangled by PowerShell's native-arg passing.
2. **PowerShell + `python -c "..."`** with nested quotes → always write a temp `.py` file (and strip the BOM if you used `Out-File -Encoding utf8`).
3. **`Out-File -Encoding utf8` adds a BOM** → Python will choke on it. Use `[System.IO.File]::WriteAllText(path, content, (New-Object System.Text.UTF8Encoding($false)))` or strip bytes 0–2.
4. **Smoke tests against prod are dangerous** → we now have a local Postgres 15. See `DEV-SETUP.md`.
5. **Migration file ordering** — `20260916_course_payments.sql` references `charvak_enrollments` which no migration creates (was created by an ad-hoc script on prod). Fresh-clone / DR restore will fail. Backfill this migration in Session I.


## Audit reconciliation (2026-09-18)

**Original count:** 41 in-memory engines
**Real total:** ~62 engine-like files across root + na_module + service/manager patterns

### What the original audit missed

1. `na_module/` wasn't fully walked - we did `vector_matcher`, `vms_connector`, `revenue_engine`, `resume_engine`, `work_auth`, `charvak_vms` in Session G. Total 6.
2. Two engines were mis-classified as IN-MEMORY but were already DB-backed: `job_board_engine`, `interview_prep_engine`.
3. Referral, escrow, ai_credit, micro_internship - already DB-backed before this project.
4. A handful of small engines were never classified at all (see Session J below).

### Reconciled remaining work

| Session | Engines | Count |
|---|---|---|
| B | enterprise, ats, voice_to_web | 3 |
| H | chatbot, bridge, ai_bridge, advanced_assessment, enhanced_assessment, company_content, assessment_report, training_mapping | 8 |
| **J (new)** | doketsrb_integration, indian_language_ai, role_manager, ai_question_generator, content_generator, monitor_service | 6 |
| **TOTAL** | | **17** |

### Session J - Backlog (audit gap)

Engines with real in-memory state that were never assigned a session:

| # | Engine | State | Verdict |
|---|---|---|---|
| J/1 | `doketsrb_integration.py` | `bundle_subscriptions = []` | persist |
| J/2 | `indian_language_ai.py` | `assessments = []`, `translations = []` | persist |
| J/3 | `role_manager.py` | `custom_roles = {}` | persist (may overlap with F/4) |
| J/4 | `ai_question_generator.py` | `used_questions`, `question_cache`, `daily_ai_usage` | persist caches |
| J/5 | `content_generator.py` | `content_cache = {}` | persist (cache) |
| J/6 | `monitor_service.py` | `issues = []` | persist (log) |

Estimate: ~2-3 hours.

### Verified skip - no persistence needed

| Engine | Reason |
|---|---|
| `blog_engine` | stateless / already DB-backed |
| `email_engine` | stateless (SendGrid) |
| `global_exams_engine` | static catalog |
| `invoice_engine` | stateless |
| `sso_engine` | stateless |
| `ai_service` | stateless |
| `admin_role_manager` | hardcoded config list |
| `tools_ai_backend` | stateless (Tier E) |
| `products_engine` | dead field (Tier E) |
| `notification_engine` | SendGrid is state (Tier E) |
| `whatsapp_bot` | external block (Meta number) |


## Session K — Bug cleanup (new, after Session H)

Dedicated pass to resolve open KNOWN-ISSUES.md items that no other session owns.

### Security (from KNOWN-ISSUES items 5, 5a, 5c)

- K/1: Add auth check to `/api/exam/progress`, `/api/exam/history`, `/api/exam/study-plan` (currently open)
- K/2: Trim `/api/payment/status` response to bools only (remove `razorpay_key_id`, `paypal_client_id`)
- K/3: Restrict `dynamic_role_engine.recommend_custom_role` to admin-only

### Data integrity (items 1, 2, 3, 5b, 6e)

- K/4: `revenue_engine.create_subscription` — prevent double-count on resubscribe
- K/5: `resume_engine.SubVendorManager.track_submission` — only bump counter on new insert
- K/6: `charvak_vms.approve_timecard` — guard repeated approvals
- K/7: `outreach_engine` — add UNIQUE or document as designed
- K/8: `messaging_engine.unread_messages` — decide on `replied` inclusion

### Formal deferrals (items 5d, 6c, 6d, 9)

Document as "won't fix / by design" in KNOWN-ISSUES with rationale.

### Estimate

~2 hours. Run after Session H, before Session I.

## Session I — Final cleanup (existing, unchanged)

- Backfill `migrations/20260916_charvak_enrollments.sql`
- Delete dead fields (items 6a, 6b)
- Emoji cleanup in docstrings (item 18)
- Doc consolidation (TODO-MASTER, TIER3-MASTER-PLAN, COMPLETION-PLAN, etc.)
- Final audit re-run
- Tag `v3.0-tier3-complete-YYYYMMDD`
- Final backup
