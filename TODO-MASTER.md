# Charvak — Consolidated TODO (Master List)

**Created:** 2026-09-17
**Purpose:** Single source of truth for all flagged / deferred / pending work
**Context:** Captures everything from Session 2026-09-16/17

---

## 🔴 URGENT — Do Soon (10–30 min total)

- [ ] Rotate Render Postgres password (leaked in session chat)
- [ ] Rotate PayPal client secret (leaked in session chat)
- [ ] Add "Beta Preview" labels to 15 AI Products (products_engine has no real backend)
- [ ] Soften overstated product claims ("24/7 monitoring" etc.)

## 🟡 PERSISTENCE PROJECT — Sessions A–H (~32 hr)

See `TIER3-PERSISTENCE-PROJECT.md` for the full plan.

### Tier A — Revenue-critical
- [ ] kyc_engine (Session A)
- [ ] candidate_engine (Session A)
- [ ] training_engine (Session A)
- [ ] lms_engine (Session A)
- [ ] enterprise_engine (Session B)
- [ ] ats_engine (Session B)
- [ ] voice_to_web_engine (Session B)
- [ ] career_v2_engine (Session C)
- [ ] exam_prep_engine (Session C)
- [ ] events_engine (Session C)

### Tier B — User-facing
- [ ] messaging_engine (Session C/D)
- [ ] profile_network_engine (Session D)
- [ ] badge_engine (Session D)
- [ ] university_engine (Session D)
- [ ] brand_engine (Session D)
- [ ] final_year_project_engine (Session E)
- [ ] student_suite_engine (Session E)
- [ ] ai_internship_engine (Session E)
- [ ] team_engine (Session E)
- [ ] outreach_engine (Session F)
- [ ] marketing_ai_engine (Session F)
- [ ] exam_analytics_engine (Session F)
- [ ] dynamic_role_engine (Session F)

### Tier C — NA module B2B
- [ ] na_module/charvak_vms.py (Session F)
- [ ] na_module/revenue_engine.py (Session G)
- [ ] na_module/work_auth.py (Session G)
- [ ] na_module/vms_connector.py (Session G)
- [ ] na_module/resume_engine.py (Session G)
- [ ] na_module/vector_matcher.py (Session G)

### Tier D — Ephemeral (tolerable loss)
- [ ] chatbot_engine (Session H)
- [ ] bridge_engine (Session H)
- [ ] ai_bridge_engine (Session H)
- [ ] advanced_assessment_engine (Session H — was Session 5C)
- [ ] enhanced_assessment_engine (Session H)
- [ ] company_content_engine (Session H)
- [ ] assessment_report_engine (Session H)
- [ ] training_mapping_engine (Session H)

### Tier E — Internal (skip — verify each)
- [ ] payment_engine — verify log-only is fine
- [ ] notification_engine — verify email log is fine
- [ ] products_engine — logic only (needs Beta label, not persistence)
- [ ] tools_engine — analytics log

## 🟠 TIER 3 — Genuinely Outstanding Items

- [ ] **Analytics Dashboards** — was UNKNOWN in audit. Needs its own audit + completion.
- [ ] **University Portal FEATURE completeness** — verify signup flow + dashboard exist; persistence is in Session D
- [ ] **WhatsApp bot** — Meta number registration (external); verify bot E2E when unblocked
- [ ] **Session I — Final Tier 3 cleanup:**
  - Root directory reorg (move one-off scripts to scripts/one-off/)
  - Delete root .bak-* files
  - Delete wget.exe (6.88 MB unused)
  - Final audit re-run
  - Tag v3.0-tier3-complete-YYYYMMDD
  - Final backup

## 🟢 HOUSEKEEPING

- [ ] Delete GitHub branches: feat-course-fee-emi, feat-tiered-pricing, feat-mock-drives, feat-micro-internship-escrow
- [ ] Delete local feat-micro-internship-escrow branch
- [ ] Rename old folder to charvakit-new-OLD (OneDrive lock issue)
- [ ] Delete old location after a few days
- [ ] `pip install sendgrid` locally (email notifications failed locally)
- [ ] Document full charvak_* schema in MASTER-REFERENCE.md

## 🔵 OPTIONAL / FUTURE FEATURES

- [ ] RazorpayX integration — automate escrow payouts (currently manual bank/UPI)
- [ ] AI Products real integrations — pick 2-3 flagships to make real
  - Lock-In Breaker — real AWS/GCP/Azure billing
  - Design-Token Sentinel — real GitHub + Figma
  - AuditBot — real code analysis (semgrep/bandit)
- [ ] Enterprise Option B — public engine pages (salary benchmarks, employers, resume books, kiosk)
- [ ] Per-level curriculum quality verification (tiers built, content quality not audited)
- [ ] International EMI via PayPal invoicing (deferred from v2.0)
- [ ] Verify /mock-test route (we built /mock-drive instead)

## 🟣 PROCESS / HYGIENE

- [ ] Add git status check to session start checklist
- [ ] Update STATUS.md at end of every session
- [ ] Keep TIER3-PERSISTENCE-PROJECT.md in sync as sessions complete

---

## How to use this file

- **Before each session:** review open items
- **During:** mark items in-progress
- **After:** mark done, move to "Completed" section below
- **Committed to git** so it survives across machines

## Completed (this session — 2026-09-16/17)

- [x] Session 5A — Micro-Internship + Escrow persistence + integration
- [x] Session 5B — Company Mock Drives persistence + frontend fixes
- [x] AI Course Fee + India EMI + Global Pricing (v2.0)
- [x] Basic/Intermediate/Advanced Tiered Pricing (v2.1)
- [x] All 5 master docs updated to v2.2
- [x] Complete backup (Charvak_Complete_Backup_20260917_021435.zip)
- [x] Working repo moved out of OneDrive
- [x] UTF-8 console fixed
- [x] Full system audit — 41 in-memory engines identified
- [x] Nav verification — all 19 URLs return 200
- [x] Audit files saved to audits/
- [x] TIER3-PERSISTENCE-PROJECT.md created
