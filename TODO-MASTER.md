# Charvak - Master TODO List

**Created:** 2026-09-17
**Last updated:** 2026-09-18 (after Session D)
**Purpose:** Single source of truth for all flagged / deferred / pending work
**See also:** KNOWN-ISSUES.md (bug registry), TIER3-PERSISTENCE-PROJECT.md (persistence plan), DEV-SETUP.md (local dev workflow), MASTER-REFERENCE.md (system reference)

---

## URGENT

- [ ] Rotate PayPal client secret (leaked in session chat)

---

## PERSISTENCE PROJECT (26 / 41 engines)

See `TIER3-PERSISTENCE-PROJECT.md` for the full plan.

### Tier A - Revenue-critical

- [x] kyc_engine (Session A - PR #5)
- [x] candidate_engine (Session A - PR #6)
- [x] training_engine (Session A - PR #7)
- [x] lms_engine (Session A - PR #8)
- [ ] enterprise_engine (Session B)
- [ ] ats_engine (Session B)
- [ ] voice_to_web_engine (Session B)
- [x] career_v2_engine (Session C - PR #10)
- [x] exam_prep_engine (Session C - PR #11 engine, #12 routes)
- [x] events_engine (Session C - PR #9)

### Tier B - User-facing

- [x] messaging_engine (Session D - PR #19)
- [x] profile_network_engine (Session D - PR #19)
- [x] badge_engine (Session D - PR #19)
- [x] university_engine (Session D - PR #19)
- [x] brand_engine (Session D - PR #19)
- [x] final_year_project_engine (Session E - PR #16)
- [x] student_suite_engine (Session E - PR #14)
- [x] ai_internship_engine (Session E - PR #15)
- [x] team_engine (Session E - PR #13)
- [x] outreach_engine (Session F - PR #18)
- [x] marketing_ai_engine (Session F - PR #18)
- [x] exam_analytics_engine (Session F - PR #18)
- [x] dynamic_role_engine (Session F - PR #18)

### Tier C - NA module B2B

- [x] na_module/charvak_vms.py (Session G - PR #17)
- [x] na_module/revenue_engine.py (Session G - PR #17)
- [x] na_module/work_auth.py (Session G - PR #17)
- [x] na_module/vms_connector.py (Session G - PR #17)
- [x] na_module/resume_engine.py (Session G - PR #17)
- [x] na_module/vector_matcher.py (Session G - PR #17)

### Tier D - Ephemeral (tolerable loss)

- [ ] chatbot_engine (Session H)
- [ ] bridge_engine (Session H)
- [ ] ai_bridge_engine (Session H)
- [ ] advanced_assessment_engine (Session H - was Session 5C)
- [ ] enhanced_assessment_engine (Session H)
- [ ] company_content_engine (Session H)
- [ ] assessment_report_engine (Session H)
- [ ] training_mapping_engine (Session H)

### Tier E - Internal (skip - verify each)

- [ ] payment_engine - verify log-only is fine
- [ ] notification_engine - verify email log is fine
- [ ] products_engine - logic only (Beta labels done)
- [ ] tools_engine - analytics log

---

## TIER 3 - Genuinely Outstanding

- [ ] **Analytics Dashboards** - was UNKNOWN in audit. Needs its own audit + completion.
- [ ] **University Portal FEATURE completeness** - verify signup flow + dashboard exist
- [ ] **WhatsApp bot** - Meta number registration (external block); also has AI JSON bug at whatsapp_bot.py:92
- [ ] **Exam prep frontend mock-test UI** - backend + routes are live; UI not built
- [ ] **Session I - Final Tier 3 cleanup:**
  - Root directory reorg (move one-off scripts, consolidate docs)
  - Delete root .bak-* files (if any remain)
  - Backfill migrations/20260916_charvak_enrollments.sql
  - Fix 20260916_course_payments.sql FK ordering
  - Consolidate doc sprawl (TODO-MASTER, TIER3-MASTER-PLAN, TIER3-PERSISTENCE-PROJECT, COMPLETION-PLAN overlap)
  - Archive old-*.txt, CHAT_CONTEXT.md, SESSION_LOG_*.md, DEPLOY_TRIGGER.md
  - Final audit re-run
  - Tag v3.0-tier3-complete-YYYYMMDD
  - Final backup

---

## HOUSEKEEPING

- [ ] Delete GitHub branches: feat-course-fee-emi, feat-mock-drives, feat-micro-internship-escrow
- [ ] Delete local feat-micro-internship-escrow branch
- [ ] Rename old folder to charvakit-new-OLD (OneDrive lock issue)
- [ ] Delete old location after a few days
- [ ] pip install sendgrid locally (email notifications failed locally)
- [ ] Document full charvak_* schema in MASTER-REFERENCE.md
- [ ] Fix heading order on remaining pages (accessibility)
- [ ] TBT ~1,900ms mobile - conditional script loading

---

## OPTIONAL / FUTURE FEATURES

- [ ] RazorpayX integration - automate escrow payouts (currently manual bank/UPI)
- [ ] AI Products real integrations - pick 2-3 flagships to make real
  - Lock-In Breaker - real AWS/GCP/Azure billing
  - Design-Token Sentinel - real GitHub + Figma
  - AuditBot - real code analysis (semgrep/bandit)
- [ ] Enterprise Option B - public engine pages (salary benchmarks, employers, resume books, kiosk)
- [ ] Per-level curriculum quality verification (tiers built, content quality not audited)
- [ ] International EMI via PayPal invoicing (deferred from v2.0)
- [ ] Verify /mock-test route (we built /mock-drive instead)

---

## PROCESS / HYGIENE

- [ ] Add git status check to session start checklist
- [ ] Update STATUS.md at end of every session
- [ ] Keep TIER3-PERSISTENCE-PROJECT.md in sync as sessions complete
- [ ] **Append to KNOWN-ISSUES.md every session** - if you preserve a bug, note it
- [ ] Run local smoke tests against local Postgres (see DEV-SETUP.md), never against prod

---

## How to use this file

- **Before each session:** review open items
- **During:** mark items in-progress
- **After:** mark done, move to "Completed" section below
- **Committed to git** so it survives across machines

---

## Completed - 2026-09-18 (Session D)

- [x] Session D - Tier B user-facing engines (5 engines, 11 tables) - PR #19
- [x] Fixed: missing `timedelta` import in brand_engine.promote_job (would NameError)
- [x] Fixed: mojibake in badge_engine share_text (trophy emoji)
- [x] Preserved JSONB dict.update() semantics via Postgres `||` operator
- [x] Normalized messaging conversation_key (sorted pair)

## Completed - 2026-09-18 (Session F)

- [x] Session F - Tier B engines (4 engines, 11 tables) - PR #18
- [x] Fixed: mojibake in marketing_ai_engine templates (emoji rendering)
- [x] Fixed: dynamic_role_engine custom roles now persist across restarts
- [x] Closed Session C loop: exam_analytics routes now DB-backed

## Completed - 2026-09-18 (Session G)

- [x] Session G - NA module persistence (6 engines, 13 tables) - PR #17
- [x] Fixed: hash() ID generation bug in vms_connector (job_id)
- [x] Fixed: hash() ID generation bug in resume_engine (vendor_id)
- [x] Fixed: PII phone regex corruption in resume_engine
- [x] Gated demo data behind env vars (CHARVAK_LOAD_DEMO_*)
- [x] Created KNOWN-ISSUES.md registry
- [x] Local Postgres 15 dev workflow established (DEV-SETUP.md)

## Completed - 2026-09-18 (Session E)

- [x] Session E - User-facing persistence (4 engines) - PRs #13, #14, #15, #16
- [x] Fixed: AI JSON parsing bug in final_year_project_engine (response_format)
- [x] Installed local Postgres 15 + created DEV-SETUP.md
- [x] Created .env.local + smoke test workflow

## Completed - 2026-09-17 (Session C)

- [x] Session C - events, career_v2, exam_prep persistence - PRs #9, #10, #11, #12
- [x] Exam prep API routes + route ordering fix
- [x] Beta Preview badge on 15 product pages
- [x] Root directory cleanup (32 orphans, 15 .bak files)
- [x] Stale branch cleanup (local + remote)
- [x] Rotate Render Postgres password
- [x] Docs sync + DEV-SETUP.md created

## Completed - 2026-09-17 (earlier session)

- [x] Session 5A - Micro-Internship + Escrow persistence + integration
- [x] Session 5B - Company Mock Drives persistence + frontend fixes
- [x] AI Course Fee + India EMI + Global Pricing (v2.0)
- [x] Basic/Intermediate/Advanced Tiered Pricing (v2.1)
- [x] All 5 master docs updated to v2.2
- [x] Complete backup (Charvak_Complete_Backup_20260917_021435.zip)
- [x] Working repo moved out of OneDrive
- [x] UTF-8 console fixed
- [x] Full system audit - 41 in-memory engines identified
- [x] Nav verification - all 19 URLs return 200
- [x] Audit files saved to audits/
- [x] TIER3-PERSISTENCE-PROJECT.md created
