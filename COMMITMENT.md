# Charvak — Commitment Tracker

**Purpose:** Track every planned-but-not-completed item. Nothing gets lost again.
**Created:** 2026-09-20
**Last updated:** 2026-09-22
**HEAD:** `00aec90`

---

## ✅ COMPLETED

### N1 — State exam smoke test + content quality fixes

- **Completed:** 2026-09-22 (Session N1) — commits `9a8ce83` through `00aec90`
- **Catalog:** `upsc_cse` + `neet_ug` added (136 → 138 exams)
- **Question bank:** 5 state PCS exams topped to 40+ per topic; ~13,600+ rows total
- **Mock test performance:** batched bank query (3 DB calls → 1); 2-4s → 0.4s
- **Connection pool:** `get_pooled_connection()` + `release_pooled_connection()` in `database.py`; `exam_prep_engine` hot paths migrated; startup warmup in `main.py`
- **Language hints:** AI prompt forces correct script for 10 language sections (Bengali, Hindi, Tamil, Telugu, Marathi, Kannada, Malayalam, Gujarati, Punjabi, Urdu)
- **Practice route fix:** `/api/exam/ai-questions` redirected from legacy `ai_question_generator` to `exam_prep_engine` — was serving wrong content for state-specific topics
- **Verified in prod (Render logs):**
  - `[startup] DB connection pool warmed` ✅
  - `bank lookup: X/Topic -> 10 rows (wanted 10)` for all 5 state PCS exams ✅
  - Bengali content serves correctly ✅
  - Credit deduction: 3 cr practice / 15 cr mock ✅
- **N1.5 Legal audit:** PASSED — all 4 pages render on `www.charvakit.com` (terms, privacy, refund, cookie-policy), plus `accessibility`
- **Follow-ups:**
  - Semantic duplicate questions (near-identical wording across topics) → C13
  - Two engines to consolidate (`exam_prep_engine` vs `ai_question_generator`)
  - Apex domain `charvakit.com` returns 404; optional Cloudflare redirect to `www`

---

### C1 — Assessment AI for global languages

- **Completed:** 2026-09-21 (Session G1) — commit `c3dc68a`
- **Discovered:** 2026-09-20 (audit was wrong; corrected 2026-09-20)
- **Reality:** `global_config.LANGUAGES` has 34 languages ✅ (config complete)
- **Real gap fixed:** `indian_language_ai._generate_questions` only handled 12 Indian languages.
  Spanish, French, German, Japanese, etc. users got English/Hinglish assessment questions.
- **What shipped:**
  - `LANG_NAME_FOR_PROMPT` (36 languages) for AI prompt naming
  - `LANG_META()` resolver: INDIAN_LANGUAGES → global_config.LANGUAGES → fallback
  - Silent-Hindi bug fixed in BOTH `create_assessment` AND `translate_job_ad`
  - Static fallback guard: non-Indian returns `[]` instead of Hinglish default
  - `_generate_questions_via_ai` now serves all 34 languages
- **Verified:** live OpenAI smoke test — es/fr/ja/ar/zh/hi/te/ta/ko/de all
  returned native-script questions (5 each)
- **Note:** `_generate_questions_static` deliberately still covers only 12 Indian
  languages. Non-Indian + AI failure returns `[]`, so caller falls back explicitly.

---

### C4 — Adaptive difficulty

- **Completed:** 2026-09-21 (Session G2) — commit `15193f9`
- **What shipped:**
  - New `charvak_user_ability` table (migration + engine self-init)
  - New `ability_engine.py` — Elo math, `get_ability`,
    `update_from_assessment`, `get_recommended_difficulty`, `recommend_difficulty`
  - `results_system.record_assessment_result` accepts optional `skill=`;
    when set, updates ability post-insert (non-fatal on failure)
  - `complete_mock_drive.complete_mock` passes `skill=mock_{company_id}`
  - `enhanced_assessment_engine.create_custom_assessment` and
    `generate_topic_questions` accept `email=` and use ability-recommended
    difficulty when caller omits it
  - `main.py` routes `/api/enhanced/*` forward `difficulty` + `email`
- **Verified:**
  - Local Elo math (8/10 → +7.2, 2/10 → −7.45)
  - Prod table exists with all columns + PK `(email, skill)` + 2 indexes
- **Not in scope (Phase 2):** mock drives still generate at fixed difficulty.
  Ability only read by `/api/enhanced/*` today.
- **Backwards compatible:** existing callers see no behavior change.


### C5 — Curated question banks

- **Completed:** 2026-09-21 (Session G3) — commit `f4a3fd3` + local seed run
- **What shipped:**
  - New `scripts/seed_exam_question_bank.py` — idempotent, resumable,
    throttled batch generator for `charvak_exam_question_bank`
  - Phases: `--phase 1` (top 10 exams, ~35 pairs), `--phase 2`
    (all 67 Indian exams, 207 pairs)
  - `--resume` skips pairs already at target count
  - Runs through `exam_prep_engine.generate_questions` — same path
    users hit, no parallel write paths
- **Verified (local):**
  - Phase 2: **207/207 pairs succeeded** in 5281s (88 min)
  - Bank now: **12,892 rows** across 67 exams, 43 distinct topics
  - **207/207 pairs cache-eligible** (≥30 questions)
  - Average 62 questions/pair (target 50; OpenAI variance + top-up)
- **Known limitations:**
  - `jssc/Math` had 30 stub rows from OpenAI timeout during batch;
    re-generated to 42 real questions.
  - `global_exams_engine` excluded (no `generate_questions` method yet)
  - Runtime 88 min vs 33 min estimate — OpenAI averaged ~25s/call
- **Backwards compatible:** no user-facing code changes.

---


### C6 — Assessment UI translations

- **Completed:** 2026-09-21 (Session G5) — commits `fa83917` through `acd450e`
- **What shipped:**
  - **`static/js/i18n.js`** — client-side loader (~5.5 KB)
    - Language priority: localStorage → `window.CHARVAK_LANG` → Accept-Language → `en`
    - Replaces `[data-i18n]`, `[data-i18n-placeholder]`, `[data-i18n-title]`
    - Exposes `window.changeLanguage()` + `window.t()` for programmatic use
    - Graceful fallback: missing keys render English
  - **`static/locales/en.json`** — 278 source strings across 16 groups
  - **17 language files** — hi, te, ta, kn, ml, mr, bn, gu, pa (Indian);
    es, fr, ar, zh, de, pt, ru, ja (Global)
  - **`scripts/translate_ui.py`** — batch translator (OpenAI gpt-4o-mini, temp 0.2)
  - **~197 data-i18n attributes** across 7 templates:
    - `base.html` — 90 (nav, footer, topbar, user menu)
    - 6 assessment templates — ~107 (reports, advanced-assessment,
      assessments, custom-assessment, mcq, exam-prep)
- **Fixed as part of G5:** base.html had double-encoded UTF-8 in 17
  language <option> values. Replaced from `global_config.LANGUAGES`.
- **Scope boundary:** static HTML only. JS-injected strings (innerHTML,
  template literals) deferred to a follow-up session.
- **Backwards compatible:** pages render English by default.

### C7 — Build 13 Category-B feature backends (post-G6)

- **Discovered:** 2026-09-21 (Session G6 revenue audit)
- **Issue:** 13 templates have `processCharvakPayment` UI + callback
  but NO backend endpoint. Currently take payment intent but deliver
  no actual feature.
- **Affected templates:**
  1. `agency-twin.html` — ₹2,999 Agency-Twin Pro
  2. `agent-ready.html` — ₹399 Agent-Ready Wrapper
  3. `ai-internship.html` — variable (weeks × program)
  4. `ai-slop-quarantine.html` — ₹149 AI-Slop Clean
  5. `auditbot.html` — ₹299 Fix + ₹999 Subscription (2 features)
  6. `design-token-sentinel.html` — ₹299 Design-Token Pro
  7. `developer-entropy.html` — ₹299 Monitoring
  8. `geo-compliance.html` — ₹199 Contract Gen + ₹999 Global Hiring (2)
  9. `legacy-shift.html` — ₹4,999 Migration
  10. `lock-in-breaker.html` — ₹4,999 + ₹4,999 (2)
  11. `marketing-ai.html` — ₹299
  12. `micro-squads.html` — ₹49,999 Assembly
  13. `reports.html` — ₹299 Premium Report
  14. `skill-twin.html` — ₹499 Verification
  15. `team-dashboard.html` — ₹1,999 Pro
  16. `skill-twin` variants
- **Temporary handling (G6):** replace payment button with
  "Notify Me" CTA. Captures intent, no fraud risk.
- **Future work per feature:**
  - Build backend engine + endpoint
  - Add `FEATURE_CREDITS` key
  - Guard with `require_credits_from_data`
  - Wire frontend to credit purchase flow
- **Est:** 3-5 hr per feature × 15 features = **~45-75 hr total**
- **Priority:** Medium — tackle top 3 by market demand first
- **Verdict:** DEFERRED (post-G6, iterative)**

- **Expanded (2026-09-21, Session G6 revenue audit):** 5 additional
  templates confirmed to have the same problem — dead
  `processCharvakPayment` callbacks + working free paths with no gate:
  1. `events.html` — RSVP works free; ₹499 button was dead
  2. `ats.html` — no form exists; ₹999 button was dead
  3. `lms.html` — no real enroll endpoint; ₹999 button was dead
  4. `micro-internship.html` — form on `/post-micro-project` ignores
     the `?payment_id=` redirect; ₹2,000 bypassed
  5. `university.html` — no form exists; ₹4,999 button was dead

  **G6 handling:** All 5 buttons replaced with `notifyMe()` (matches
  the pattern used across 13 other templates). No working flow was
  removed — the free paths remain intact for now.

  **Future work per template:**
  - Build proper form (events needs RSVP confirmation page; ats
    needs provider/api_key inputs; university needs registration form)
  - Add backend endpoint guard where one exists
  - Wire frontend to `notifyMe()` → real "Buy Credits" flow when
    the feature ships

- **Total C7 scope:** **18 templates** (~25 features across them)
- **Est (updated):** ~60-90 hr total, iterative by priority


### C9 — Catalog expansion: 12 missing exams

- **Completed:** 2026-09-22 (Session L) — commit `f15464f`, merged on main
- **Discovered:** 2026-09-21 (CBT/CAT audit against the master exam list)
- **Issue:** Catalog held 67 exams / 8 categories — missing key Indian CBT exams
  (JEE Advanced, SRMJEEE, MET, COMEDK UGET, MAT, ATMA, MAH MBA CET, IIT JAM, NIMCET)
  and had zero global exams.
- **What shipped:**
  - `engineering` +4: `jee_advanced`, `srmjeee`, `met_manipal`, `comedk_uget`
  - `management` +3: `mat`, `atma`, `mah_mba_cet`
  - `university` +2: `iit_jam`, `nimcet`
  - **NEW category `international`** +3: `gmat_focus` (Section-Adaptive CAT),
    `gre_general` (Section-Adaptive), `toefl_ibt` (CBT)
  - Single-file change: `exam_prep_engine.py`
  - Docstring updated: `67 exams, 8 categories` → `79 exams, 9 categories`
- **Verified:**
  - Local + prod: `total_categories: 9`, `total_exams: 79`
  - All 12 new exam IDs resolve via `get_exam_details`
  - Question generation works end-to-end (real AI)
  - Non-ASCII = 0
- **Follow-ups:**
  - IELTS Academic deferred — needs AI writing/speaking scoring path
  - RRB ALP CBAT (Computer-Based Aptitude Test) module — different question type
  - Adaptive engine (IRT) for GMAT/GRE/NMAT/BITSAT — longer roadmap
  - Re-seed `charvak_exam_question_bank` for the 12 new exams (currently on-demand)

---

### C8 — Revenue enablement (G6)

- **Completed:** 2026-09-21 (Session G6) — commits `0dcf2a8` through `92ce054`
- **What shipped:**
  - **`credit_guard.py`** — reusable `require_credits_from_data(data, feature)`
    + `require_credits_dep` dependency factory; 401 for missing email,
    402 for insufficient credits
  - **Pricing (repriced):** Starter ₹199/300cr, Pro ₹499/1000cr,
    Premium ₹999/2500cr, Enterprise ₹4999/15000cr
  - **8 new feature keys** in `FEATURE_CREDITS` (mock_test repriced 20→15)
  - **10 routes guarded** across exam / assessment / mock drive
  - **`exam-prep.html` rewritten** — 4 credit packages + balance banner;
    fake subscription system (subscribeExam, planLimits, canPractice,
    showUpgradeModal) removed; demo@ fallback removed
  - **`main.js` 401/402 handler** — global fetch wrapper dispatches
    `charvak:401` / `charvak:402` events
  - **`indian-language-ai.html`** — migrated to credits (2 routes guarded)
  - **18 dead payment buttons** replaced with `notifyMe()` (interest capture);
    `/api/features/notify` + `charvak_feature_interest` table added
  - **`payment-helper.js`** — region-aware modal (India → Razorpay first,
    Intl → PayPal first) with "RECOMMENDED" badge
- **Bugs found in Phase 9 testing & fixed:**
  - Free-plan credit farming (click "Start Free" repeatedly → +50 each):
    `purchase_credits` now rejects repeat free claims; UI hides Free
    card for users with credits
  - `charvak_feature_interest` table creation moved to `_ensure_tables`
- **Not in scope (deferred to C7):**
  - 13 Category-B templates still need real feature backends
  - 5 more templates (events, ats, lms, micro-internship, university)
    have working endpoints but need proper form UX
- **Backwards compatible:** pages render English by default; existing
  users unaffected

- **Batches 1-5 (final audit):** All revenue-generating routes now guarded:
  - Batch 1: Voice + AI tools (14 routes)
  - Batch 2: Marketing + Outreach (7 routes)
  - Batch 3: Student + FYP + Interview + Bridge + Tutor (14 routes)
  - Batch 4: Products + Company + AI-Course + Versant + LMS (39 routes)
  - Batch 5: Background verification + Roles + Content + Internship (5 routes)
  - **System total: 92 routes guarded**
  - **Audit result:** only auth / payment-flow / credits meta / admin /
    mid-session routes remain free (by design).
  - **Nothing AI-powered or feature-unlocking is free.**


### M-1 — IELTS Academic (Listening/Reading/Writing)

- **Completed:** 2026-09-22 — commit `3c7e664` (merge of `15482f6`)
- **What shipped:**
  - `ielts_academic` added to `exam_prep_engine` catalog (80 exams, 9 categories)
  - NEW `ielts_engine.py` (~311 lines) — stateless orchestration:
    - AI prompt generation (Task 1 + Task 2, JSON-mode)
    - AI band scoring on 4 official IELTS criteria
    - Persists to `charvak_assessment_results` (assessment_type='ielts_writing')
  - 3 new routes in `main.py`:
    - `GET  /api/ielts/sections`
    - `POST /api/ielts/writing/generate`
    - `POST /api/ielts/writing/evaluate`
  - 2 new credit keys: `ielts_writing_eval` (15cr), `ielts_writing_prompt` (3cr)
- **Verified E2E:** 117-word Task 2 essay scored 5.5 overall with correct
  Task Response cap (5.0) for word-count violation; persisted with all
  4 sub-bands in details_json.
- **Deferred to M-2:** IELTS Speaking (needs audio recording + Whisper).


### M-2 — RRB ALP CBAT

- **Completed:** 2026-09-22 — commit `<hash>`
- **What shipped:**
  - NEW `cbat_engine.py` (~594 lines) — DB-backed engine
    for 6 sub-tests: Analogies, Decision Making, Numerical Ability,
    Memory (Short/Long), Following Directions
  - NEW migration `20260922_cbat.sql` — 2 tables
    (`charvak_cbat_sessions`, `charvak_cbat_answers`)
  - NEW `templates/cbat.html` — timed question delivery, SVG rendering,
    no back-navigation, per-question countdown
  - 5 new routes: `/api/cbat/sub-tests`, `/start`, `/submit-answer`,
    `/complete`, `/status/{id}`
  - `cbat_session` credit key (25cr)
  - `rrb_alp_cbat` catalog entry (81 exams total)
- **Verified E2E:**
  - 6 sub-tests with per-question timing metadata
  - AI-generated 20 unique Analogies questions
  - Idempotent answer submission (UNIQUE constraint)
  - Session score 5.0% for 1/20 correct
  - All data persisted across 3 tables
  - 25 credits deducted correctly
- **Future (M-3):** Seed curated CBAT questions into a cache
  (currently AI-generated per session)
  - Delivery: image-based (SVG inline), strict per-question timing,
    no back-navigation (UNIQUE constraint on answers table)


### M-3 — State Government Exam Coverage

- **Completed:** 2026-09-22 — commits `f471b67`, `1c0d161` (merged via `2a91239`, `1da969e`)
- **What shipped:**
  - **3 new categories** in `exam_prep_engine`:
    - `state_pcs` (20 exams): UPPSC, MPSC Rajyaseva, RPSC RAS, WBCS,
      TNPSC Group 1 & 2, KPSC KAS, MPPSC SSE, GPSC, OPSC, APSC,
      CGPSC, JPSC, UKPSC, HPSC, PPSC, Kerala PSC, Manipur PSC,
      JKPSC, TPSC
    - `state_police` (18 exams): UP, Bihar, Rajasthan, Delhi, Haryana,
      MP, Maharashtra, Punjab, Kerala, Karnataka, TN, Telangana, AP,
      Gujarat, WB, Odisha, Jharkhand, Chhattisgarh
    - `state_tet` (17 exams): UPTET, REET, MAHA TET, TNTET, KARTET,
      UTET, WBTET, MPTET, JTET, OTET, PSTET, HPTET, APTET, TSTET,
      KTET, Assam TET, Bihar TET
  - **Catalog: 81 → 136 exams, 9 → 12 categories**
  - Zero new engines, tables, routes, or templates — all reuse
    existing infrastructure
  - AI question generation works for every new exam
- **Verified:**
  - Prod shows 136 exams / 12 categories
  - AI generation confirmed for new exams
- **Coverage:** all major Indian states across PCS / Police / TET


### M-3.5 — Prompt hardening + difficulty calibration

- **Completed:** 2026-09-22 — commit `43bc281` (merge of `43c20d2`)
- **What shipped:**
  - AI prompt rewritten with STRICT RULES:
    - Enforce EXACTLY 4 options per question
    - Require unique questions (no duplicates)
    - Verify correct answer appears in options
    - Self-regenerate on invalid output
  - `difficulty` field added to all 136 exams
  - `_get_exam_difficulty()` helper added
  - Prompt passes `Difficulty: {level}` context
- **Distribution:** Easy 49, Medium 68, Hard 19
- **Verified:**
  - ssc_cgl/Reasoning (Medium): 5 unique, 4-opts-each
  - up_police/GK (Easy): basic state GK
  - cat/VARC (Hard): complex reasoning
- **Discovered but NOT fixed:** see C13.

### C13 — Curated question banks (Session M-4)

- **Discovered:** 2026-09-22 (content quality audit on SSC CGL Reasoning)
- **Issue:** Prompt hardening reduces but does not eliminate logical
  errors in AI questions (missing correct answer in options, subtle
  math errors). Content quality is user-visible.
- **Solution:** Pre-generate questions once, manually review, seed
  into `charvak_exam_question_bank`. Cache-first, live-AI fallback.
- **Scope:**
  - Top 20 exams x 5 topics x 30 questions = 3,000 curated questions
  - Manual review process
  - Seed script (reuse Session G3 pattern)
  - Extend `_load_from_bank` to prefer seeded questions
- **Est:** 2-3 hr per batch
- **Priority:** Medium-High

## 🔴 CRITICAL — Must Fix

### C2 — `voice_to_web_engine.py` persistence

- **Discovered:** 2026-09-20 (was flagged as B-2, never executed)
- **Issue:** 5 in-memory stores (`websites`, `domains`, `updates`, `support_tickets`, `seo_configs`)
- **Action:** Design tables + migration + refactor + test
- **Est:** ~1 hr
- **Target:** Session B-2
- **Status:** SKIPPED on 2026-09-21 in favor of C1. Re-schedule per priority.

### C3 — RTL UI support — DEFERRED 2026-09-21

- **Discovered:** 2026-09-20 (`base.html` has `<html lang="en">` hardcoded)
- **Original issue:** Arabic users see LTR layout despite `dir="rtl"` in config
- **Why deferred:** Only 1 of 34 languages is RTL (`ar`). No evidence of an
  Arabic-speaking user base in any project doc. RTL-layout-with-English-text
  is worse UX than clean LTR — the right sequence is C6 (content i18n) FIRST,
  then C3.
- **Escalation trigger (any of):**
  1. A real Arabic-speaking user or customer appears
  2. Sales/marketing targets MENA region
  3. C6 (assessment UI translations) ships — then C3 makes sense as follow-up
- **When triggered:** ~2 hr (dynamic `lang`/`dir`, bootstrap RTL swap,
  cookie picker, ~2 CSS overrides in `static/css/style.css`)
- **Verdict:** DEFERRED (product decision — no current user base)

---

## 🔍 NEEDS VERIFICATION

### V1 — Doc sprawl

- **Check:** List all .md files in root
- **Concern:** Duplicates may exist (KNOWN-ISSUES vs FINAL-STATUS, etc.)
- **Action:** Verify next audit

### V2 — whatsapp_bot.py JSON mode — FALSE ALARM

- **Discovered:** Line 60 uses `response_format="text"` — but this is
  `audio.transcriptions.create` (Whisper), NOT chat completions.
  Text format is correct for Whisper.
- **Line 89** (the only LLM call) uses JSON mode correctly.
- **Verdict:** ✅ No bug. No action needed.

### V3 — 34-language claim vs delivered

- **Check:** Count actual supported languages
- **Concern:** Site copy says 34; actual may be less
- **Status:** ✅ RESOLVED 2026-09-21 — `global_config.LANGUAGES` has 34 languages,
  and as of Session G1 `indian_language_ai._generate_questions` serves all of them
  via AI. Copy claim is now accurate for the assessment flow.

---


### V4 — Dev and prod share one Render Postgres

- **Discovered:** 2026-09-21 (Session G3)
- **Reality:** `.env` `DATABASE_URL` connects to
  `dpg-d9m92j0ae00c73blvoq0-a.singapore-postgres.render.com/vouchai`.
  Every local script run writes to prod. No dev/staging isolation.
- **Evidence:**
  - Local `charvak_exam_question_bank` count (12,892) exactly matches
    prod count verified via Render Shell
  - `charvak_user_ability` table appeared in prod immediately after
    local `ability_engine._ensure_tables()` ran during G2
  - No log file at `/tmp/g3_seed.log` in Render Shell despite local
    seed script having run — because the script never ran in Render's
    container; it ran on the local machine talking to the shared DB
- **Implication:**
  - All local experiments are prod operations
  - Any destructive query (`DROP`, `DELETE` without `WHERE`, bulk
    `UPDATE`) affects real users immediately
  - No safe sandbox for testing
  - Backups capture prod state, not a dev clone
- **Action (deferred):** Set up local Postgres 15 for dev (Postgres 15
  is already installed per `MASTER-REFERENCE.md` at
  `C:\Program Files\PostgreSQL\15`) OR provision a separate Render
  staging database.
  - **Option A (local):** Point `.env.local` at
    `postgresql://postgres:dev@localhost:5432/charvak_dev`, run
    migrations + seed scripts against it.
  - **Option B (Render staging):** New Render Postgres resource;
    copy prod → staging periodically for realistic tests.
- **Escalation trigger:** Any of the following:
  1. Any destructive operation planned (DROP, DELETE without WHERE,
     bulk UPDATE)
  2. Onboarding a second developer
  3. Adding a feature that requires iterative testing against scratch
     data
- **Verdict:** DEFERRED (works today; revisit when risk grows)


### V5 — Local shell env var overrides .env DATABASE_URL

- **Discovered:** 2026-09-22 (Session M-2 verification)
- **Reality:** `.env` points to Render prod DB. But setting
  `$env:DATABASE_URL` in PowerShell to a local Postgres URL makes
  Python's `load_dotenv()` a no-op — the shell value wins.
- **Consequence:** During a single session, browser tests hit PROD
  (`charvakit.com`) while shell curl/cleanup scripts hit LOCAL.
- **Rule:** Never override `DATABASE_URL` in the shell unless
  working with local. `.env` = prod source of truth.
- **Fix for cleanup scripts:** read from `.env`:
  ```powershell
  $env:DATABASE_URL = ((Get-Content .env | Where-Object { $_ -match '^DATABASE_URL=' }) -replace '^DATABASE_URL=', '').Trim()

## ✅ CONFIRMED BY DESIGN (no action)

| # | Item | Verified |
|---|---|---|
| D1 | `dynamic_role_engine.create_dynamic_training_plan` stateless | 2026-09-20 |
| D2 | `ai_internship_engine.submit_work` random score placeholder | 2026-09-20 |
| D3 | `role_manager` + `dynamic_role_engine` parallel by design | 2026-09-20 |
| D4 | `record_survey_response` counter-only | 2026-09-20 |
| D5 | `admin_role_manager` used in main.py:6131 | 2026-09-20 |

---

## 📅 SCHEDULED

| # | Item | When |
|---|---|---|
| #53 | Delete charvakit-new-OLD folder | 2026-09-22 |

---

## 🔒 BLOCKED

| # | Item | Blocker |
|---|---|---|
| #65 | whatsapp_bot.py full fix | Meta registration |

---

## 📋 EXECUTION ORDER (revised 2026-09-21)

1. ~~**Session B-2**~~ — voice_to_web persistence (C2)  [SKIPPED, re-schedule later]
2. ~~**Session G1**~~ — Assessment AI for 34 languages (C1)  ✅ DONE 2026-09-21
3. ~~**Session G4**~~ — RTL UI (C3)  [DEFERRED 2026-09-21 — no Arabic user base]
4. ~~**Session G2**~~ — Adaptive difficulty (C4)  ✅ DONE 2026-09-21 (commit `15193f9`)
5. ~~**Session G3**~~ — Question banks (C5)  ✅ DONE 2026-09-21 (commit `f4a3fd3`)
6. ~~**Session G5**~~ — Assessment i18n (C6)  ✅ DONE 2026-09-21

**All CRITICAL items resolved.** Remaining: C2 (parked), C3 (deferred).
**Dead code cleanup completed 2026-09-21 (Session G2-pre):**
- Deleted `assessment_complete.py` (in-memory stub, zero frontend callers)
- Removed 5 orphaned `/api/assessment/*` routes from `main.py`
- Commits: `bdf32fa`, `8951c9b`
---

## 🧠 PROCESS LESSONS LEARNED

### L1 — PowerShell + Python file patching is fragile (Session G1, 2026-09-21)

Three automated patch attempts failed before a manual edit succeeded:

- `Out-File -Encoding UTF8` (PowerShell 5.x) prepends a BOM, which broke
  byte-level string anchors in the patcher script
- `Measure-Object -Line` and `Out-String` fold/wrap UTF-8 content at console
  width, producing wrong line/char counts (reported 354 lines when the file
  had 390; reported 17,575 chars when the file was 19,806 bytes)
- Manually pasted here-string payloads silently lost leading whitespace and
  trailing commas, producing `IndentationError` and `SyntaxError`
- Hand-typed base64 payload introduced typos (`LANGUAGESS`) and dropped commas

**Reliable path forward:**
- For source edits containing non-ASCII (Devanagari, Tamil, etc.), use
  **Notepad (manual edit)** — verified working in Session G1
- For file-state questions, trust **`git diff --exit-code`** over any
  PowerShell string measurement
- Always `git diff` before commit and `git push` after — git is the durable backup

### L2 — Pager stalls in terminal scripts

`git diff` without `--no-pager` opens `less` and blocks non-interactive scripts.
Recommended: `git config --global core.pager ""` on Windows.

### L3 — Preserve `.bak` files until AFTER the commit is pushed

Session G1 deleted all `.bak` backups before the final commit.
Nothing was lost because git tracked the change, but the safety margin was thin.
**Rule: delete `.bak` files only after `git push` succeeds.**

### L4 — `git rm <file>` does not stage other working-tree changes

`git rm assessment_complete.py` stages only that file's deletion. Any other
modified files (`main.py` in this case) need explicit `git add`. Always check
`git status --short` before committing — files marked ` M` in the second
column are modified but NOT staged.

`git commit` without `-a` only commits staged changes. Verify with
`git show --stat HEAD` after each commit that the expected files landed.

### L5 — `ast.parse()` is stricter than Python's real import

`ast.parse(open(path).read())` fails on files with UTF-8 BOM (`EF BB BF`),
raising `SyntaxError: invalid non-printable character U+FEFF`. But
`import module_name` succeeds — Python accepts BOM at start of source files.

**Rule:** use `python -c "import X"` for syntax validation. Reserve
`ast.parse` for cases where the string doesn't have a BOM, or strip the
BOM first.

**Note:** `results_system.py` has a pre-existing BOM (unrelated to G2).
No action taken; if a future housekeeping session wants a repo-wide BOM
sweep, grep files whose first 3 bytes are `EF BB BF`.

### L6 — Multi-insert patchers must go strictly bottom-up

When a patch inserts lines at multiple positions in the same file, apply
edits in **strictly descending index order** (highest first). An insert at
index 49 shifts every subsequent index — so an "insert at 48" that follows
it lands 2 lines off and can break the file.

**Session G2 evidence:** the first Batch-3 patcher for
`enhanced_assessment_engine.py` failed exactly this way (`'{' was never
closed`). Rolled back cleanly with `git checkout --`. The corrected patcher
applied ops in reverse index order and worked first try.


### L7 — Real OpenAI latency is 3-4x the nominal estimate

Session G3: batch seeding 207 pairs took 88 min, not the estimated
33 min. Root cause: OpenAI chat completions averaged ~25s per call in
practice, not the ~7.5s assumed from single-call timings.

**Rule:** for batch OpenAI work, estimate at **25-30s per call** unless
you have measured recent latency. Add 2-3s throttle on top.

### L8 — Engine fallback masks OpenAI failures as success

`exam_prep_engine._generate_via_ai` catches exceptions and returns
`_stub_questions()` on failure, but the outer `generate_questions`
still returns `status: success`. The seed script therefore reports OK
on fallback content.

**G3 evidence:** `jssc/Math` (pair 198) — OpenAI timed out at 45s, stub
content (30 trivial arithmetic questions) was written to the bank.
Fixed by deleting stub rows (LENGTH heuristic) and re-generating.

**Rule:** for content-quality-sensitive batches, verify question content
sample, not just count. Consider adding a `source` column to the bank
to distinguish AI-generated from stub.

**Rule:** for multi-edit patchers, iterate indices in descending order,
or operate on string matches rather than line indices.


### L9 — Double-encoded UTF-8 in template dropdown values

Session G5 found `base.html`'s language dropdown had 17 `<option>`
values that were double-encoded (UTF-8 bytes reinterpreted as Latin-1,
then re-encoded). `हिन्दी` was stored as `à¤¹à¤¿à¤¨à¥à¤¦à¥€`.

**Fix:** rewrite `<option value="XX">ANYTHING</option>` from
`global_config.LANGUAGES` (which was clean).

**Rule:** when pasting non-ASCII into files, verify bytes with
`[System.IO.File]::ReadAllBytes()`. If the first bytes of a Devanagari
character are `C3 A0` instead of `E0 A4`, it's double-encoded.

**Search for hidden instances:** grep for `à¤`, `à®`, `à²`, `Ø§`, `ä¸`,
`Ð `, etc. across all templates.

---

## PROCESS COMMITMENT

**To prevent future slips:**

1. **Every session is documented** before starting (in this file)
2. **After every session**, status is updated here
3. **Never let a promised item silently disappear** — flag it in this file immediately
4. **Verification audits** every N sessions to catch gaps
5. **Session-CONTEXT.md** links here for fresh chats

---
**Last updated:** 2026-09-22
**Next update:** after C13 or Session C2