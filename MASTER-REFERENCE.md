# CHARVAKIT.COM - MASTER REFERENCE
## Charvak IT Consulting Pvt Ltd
### Last updated: October 20, 2026 (Session 70 - Wave 3 100% COMPLETE)

**HEAD:** a016814
**Live:** https://www.charvakit.com
**Resume here:** see `SESSION-CONTEXT.md` and `TRACK-A-B-PLAN.md`
**Backlog:** see `OUTSTANDING-WORK-INVENTORY.md` (master list of remaining work)
**Version:** v3.7-session-70-20261020

### Reference Documents

- **`SCHEMA.md`** — Complete DB schema (all `charvak_*` tables). Regenerate with `python scripts/regenerate_schema.py`.
- **`OUTSTANDING-WORK-INVENTORY.md`** — Master backlog (~87 items, categorized by session).
- **`DEFERRALS.md`** — Documented design decisions (won't-fix with rationale + escalation triggers).
- **`DOC-STYLE.md`** — Code/doc/commit style guide (emoji policy, naming, migrations).
- **`SESSION-CONTEXT.md`** — One-file resume pointer for fresh chat windows.
- **`KNOWN-ISSUES.md`** — Bug registry (fixed + open, categorized).
- **`TIER3-PERSISTENCE-PROJECT.md`** — Persistence tracking for the 62-engine project.

---



## SESSION 2026-10-20 (Session 70) - Wave 3 100% Complete

**Commit:** `a016814` (S67b AI Tutor frontend)
**HEAD:** a016814
**Wave 3 status:** 100% complete (all 3 features shipped)

### S67b — AI Tutor Frontend Chat Panel

Completes Wave 3 feature B. The AI Tutor backend (S67a) now has a
full frontend that reuses the S65 chat pattern.

**templates/my-course.html (+343 lines):**
- Floating "💡 Ask Tutor" button (bottom-right FAB)
- Slide-in chat panel (`#tutorPanel`) positioned below the site nav
  (top:100px, height:calc(100vh - 100px), right:0, width:400px)
- Teal header with 36px white circular × close button
- Context label that updates on resume ("Data Engineering · Week 1")
- Message area with user/assistant/system bubbles
- Textarea + Send button (Enter to send, Shift+Enter for newline)
- Typing indicator ("AI is typing...")
- localStorage session persistence per enrollment_id
- Auto-resume from backend via GET /api/ai-tutor/session/{id}
- `_token()` helper added (was missing in my-course.html)

**Behavior:**
1. Click 💡 → panel slides in from right (0.3s ease)
2. If no session → first message creates one via POST /api/ai-tutor/ask
3. Course context injected (course_name, enrollment_id, week_num)
4. AI response references the actual lesson content
5. Close × → slides out, session preserved in localStorage
6. Page reload → auto-resume conversation from DB

**Bugs found and fixed during build (7 real bugs):**
1. `_token()` was undefined in `my-course.html` — existed only in
   `interview-session.html` from S65
2. `visibility: visible` toggle during `transform` transition made
   the panel appear off-screen during the 0.3s slide-in
3. `!important` specificity conflict between base `#tutorPanel` and
   `#tutorPanel.open` transform rules
4. Panel rendered inline (not `position: fixed`) — fixed via
   `position: fixed !important` on the div
5. `×` button was invisible — forced 36px circle with white bg
6. **Panel at `top: 0` caused × to fall inside the site nav's fixed
   zone (y:32-98) — moved panel to `top: 100px`**
7. **Currency selector in nav (z-index: 9999) was stacking directly
   on top of the × button — reduced panel z-index from 99999 to 1050,
   header to 100**

**Process lesson (from bug 6/7):** For "invisible but exists" UI
buttons, always run `document.elementFromPoint(x, y)` in browser
console. It reveals what element is actually at that position —
usually something unintended in a fixed nav or overlay.

**Verified E2E:**
- Panel opens: rect.x=561, transform=translateX(0), visible on right
- Panel closes: rect.x=961, transform=translateX(400px), off-screen
- × button clickable (no overlap)
- Chat: "what week 1 covers" → 8-point response with real topic names
  pulled from `charvak_course_lessons` (Data Engineering Week 1)
- Session persists via localStorage across page reload

### Wave 3: 100% COMPLETE

| Feature | Commit(s) | Status |
|---|---|---|
| A — Interview Prep AI depth | 2d1f1a4 + 336afbb | ✅ |
| B — AI Tutor backend | 581a8f9 | ✅ |
| B — AI Tutor frontend | a016814 | ✅ |
| C — Career Certifications | 766fb6b | ✅ |

### Platform after Session 70

- 38 commits shipped across sessions 51-70
- Wave 1 + Wave 2 = 100%
- Track D Phase A = 100%
- UI Modernization = 100% (7/7 phases)
- Interview Prep conversational = 100%
- AI Tutor (backend + frontend) = 100%
- Career Certifications = 100%
- GPT-4o-mini Phase 1-3b = 100%
- Zero bugs, zero broken features

### Remaining 3 Items (all 5-min dashboard tasks, no code)

1. Send Amrita reply to Prof. Raj (unlocks Track C)
2. Rotate Render Postgres password (last security flag)
3. Phase 3c env flip (Nov 3 target, GPT-4o-mini migration complete)

**After these 3: platform has zero unblocked work.** Everything else
is blocked on Amrita signing or employer demand.

---
## SESSION 2026-10-20 - Sessions 65 + 67a + 69 (Wave 3)

**Commits:** `2d1f1a4` (S65a), `336afbb` (S65b), `581a8f9` (S67a), `766fb6b` (S69)
**HEAD:** a016814

### S65 - Interview Prep Conversational Mode

The single biggest feature shipped today. Users can now choose between
"Quick Practice" (static, 8 questions) and "Full Mock Interview"
(conversational, adaptive, up to 12 turns) on `/interview-prep`.

- Backend: `_generate_next_turn`, `start_conversational`, `submit_turn`,
  `complete_conversational` methods (+335 lines)
- Frontend: chat UI with turn indicator, transcript, per-turn scoring
- AI reads answers, generates real follow-ups (verified: 3-turn Data
  Scientist interview on L1/L2 regularization; AI's Turn 2 references
  Turn 1's content)
- Score display: avg-per-turn for conversational, partial-session indicator
- Migration: 3 columns on `charvak_interview_sessions`

### S67a - AI Tutor Persistent Backend

Rewrites `interactive_tutor.py` from in-memory to DB-backed with real
course context injection.

- Before: `self.sessions = {}` dict (lost on reload)
- After: `charvak_tutor_sessions` + `charvak_tutor_messages` tables
- `_load_course_context()` injects current lesson content + curriculum
  outline from `charvak_course_lessons` + `charvak_enrollments`
- Migrated 4 OpenAI calls to `openai_compat.build_payload` (GPT-5 ready)
- New routes: `POST /api/ai-tutor/ask`, `GET /api/ai-tutor/session/{id}`
- Existing `/api/tutor/*` routes preserved (backward compatible)
- **Verified persistence**: session survives uvicorn restart, turn_count
  continues from 2 → 3 across restart

### S69 - Career Assessment Certifications

Standalone B2C-first certification. Tiered by score (Certified 70-89 /
Expert 90-94 / Elite 95-100), pricing (free ≥85, 5 credits for 70-84).
Distinct from readiness certificates (benchmarked) — this is earned expertise.

- Migration: `charvak_career_certifications` (13 cols + 4 indexes)
- 7 new engine methods: `issue_certification`, `get_certification`,
  `verify_certification`, `list_certifications`, `_compute_tier`,
  `_generate_cert_id`, `_compute_cert_hash`, `_mask_email`
- 7 new routes: certify, get, verify, list, pdf, view page, dashboard
- Templates: `career-certification.html` (~250 lines),
  `my-certifications.html` (~200 lines)
- CTA on `/ai-assessment` result page (score ≥ 70 shows "Get Certified")
- PDF: full Career Assessment branding (via new `report_type` param on
  `render_readiness_certificate_pdf`)
- HMAC verification, idempotent issuance, privacy-safe email masking
- **Verified E2E**: certify 91/100 → CCERT issued as Expert tier (free),
  HMAC verify works, PDF downloads with correct branding + correct QR URL

### Wave 3 Status: 2.5 / 3 complete

| Feature | Status |
|---|---|
| A - Interview Prep AI depth | ✅ Complete (S65) |
| B - AI Tutor backend | ✅ Complete (S67a) |
| B - AI Tutor frontend | ⏳ S67b (~45 min) |
| C - Career Certifications | ✅ Complete (S69) |

### Bugs Fixed During Sessions 65-69 (7 real bugs, all with auto-revert gates)

1. Python 3.11 f-string backslash restriction in `logger.info`
2. PowerShell inline JS escaping breaks parsing (used here-string)
3. `SECRET_KEY` import from `global_config` doesn't exist
   (matches existing `_generate_certificate_hash` pattern:
   `os.getenv("READINESS_HMAC_KEY") or os.getenv("SECRET_KEY")`)
4. First fix attempt lost `sig = hmac.new(...)` line — auto-revert gate
   only checks `ast.parse`, not runtime; **added runtime smoke test**
5. PDF verify URL hardcoded `/api/readiness/verify/` → added
   `verify_url_path` param to renderer
6. PDF issued date showed "N/A" → renderer reads `created_at`
7. PDF branding said "Role Readiness" → parameterized `report_type`

**Process rule added:** When inserting code after a function docstring,
count triple-quotes — you need the SECOND `"""` on its own line, not the
first. First attempt put branding block inside the docstring where Python
treats it as text.

---
## SESSION 2026-10-20 - Sessions 63 + 64 + 64b (Track D Phase A 100%, CAS Admin UI complete)

**Commits:** `bb0ecea` (S63), `ef5974f` (S64), `2cff7e2` (S64b)
**HEAD:** a016814

### Session 63 - Track D Phase A complete (bb0ecea)

Wired JD parser into Career Assessment. Full loop closed:
- `/ai-assessment` gets "I have a JD" toggle (checkbox + textarea)
- `carAnalyzeJd()` calls `/api/jd/parse`, fuzzy-matches role/industry/level
  against catalog, auto-fills 3 dropdowns
- `carApplyUrlPrefill()` reads `?role=&industry=&level=` from URL on load
- `/jd-assessment` CTA carries prefill params

Track D Phase A now 100% (parser + MVP + wire-in).

### Session 64 - CAS Admin UI backend (ef5974f)

- `cas_engine.list_api_keys()` gets `search` + `sort` params
  - search: ILIKE across institution_name, contact_email, key_id, contact_name
  - sort whitelist: created_desc (default), created_asc, institution_asc,
    calls_desc, tier_asc
- `/api/admin/cas-keys/list` accepts `?search=` and `?sort=`
- NEW: `/api/admin/cas-keys/list.csv` — full CSV export with same filters

### Session 64b - CAS Admin UI frontend (2cff7e2)

Applied as 6 gated patches (P1-P6), each verified with Jinja + `node --check`
before proceeding:
- P1: CSS for toolbar/checkbox/bulk; grid-template-columns 5→6 cols
- P2: Toolbar HTML (search, sort, CSV button) + bulk actions bar
- P3: Empty checkbox column in renderList header
- P4: Checkbox input in renderRow template (pending rows only)
- P5: loadKeys reads search + sort from toolbar inputs, appends to fetch URL
- P6: Selection helpers (toggleSelection, clearSelection, updateBulkBar,
  bulkApproveSelected, exportKeysCsv)

Verified: zero console errors, search filters, sort re-orders, CSV downloads,
bulk bar correctly hidden at 0 rows.

### Process lesson (logged in KNOWN-ISSUES)

Earlier attempt to patch admin-cas-keys.html corrupted the file by matching
`window.loadKeys = async function()` — that string doesn't exist in the clean
file (functions use `async function loadKeys()` with `window.loadKeys = loadKeys`
exports at the bottom). The wrong anchor caused the insert to land on a
`renderRow` return template, splicing three functions together.

Session 64b fix: line-range anchors + unique full-line string matches +
`node --check` gate + auto-revert on failure. Zero corruption.

---
## SESSION 2026-10-19 - Sessions 55-56 (Track D Phase A)

**Commits:** `e8488f6` (parser), `50fa546` (MVP), `2c0451c` (cards)

### Shipped
- `jd_parser_engine.py` — JD → 11-field structured output
- `POST /api/jd/parse` — public, 5/min rate limit
- `templates/jd-assessment.html` — JD Scanner landing page
- `GET /jd-assessment` — public route
- `🎯 JD Scanner` nav link (teal CTA row)
- What-next cards on /ai-assessment result (4 cards)

### Verified
- 7/7 real JDs parsed (NCS, LENZE, Middle East)
- /jd-assessment 200 on prod
- API endpoint tested with SWE + PM
- Cards render on prod result page

### Track D Phase A: 67% (2 of 3 items)
Item C (wire into Career Assessment) = Session 57

## SESSION 2026-10-19 - Session 52 (Certificate-as-a-Service)

**Commit:** `1902eb7`

### Shipped

- Certificate-as-a-Service — bulk verification API for universities
- `cas_engine.py` (new, ~16 KB): verify_certificate_by_hash,
  verify_batch, request_api_key, approve_api_key, check_api_key,
  list_api_keys. SHA-256 API key storage, approval-gated.
- 3 new routes: `POST /api/cas/verify-batch`,
  `POST /api/cas/request-key`, `GET /employer/cas`
- New template `employer-cas.html` (hero, 4 pricing tiers, API docs,
  request form)
- New migration `20261019_cas_api_keys.sql`
- CTA in `employer-dashboard.html` hero → /employer/cas

### Wave 2 status: 100% COMPLETE

Trust Score API (S50) + Employer Dashboard (S51) + CAS (S52).
Three B2B products live. Track C (Amrita pilot) technically unblocked.

### Prod verified (2026-10-19)

- `GET /employer/cas` -> 200
- `POST /api/cas/verify-batch` (no key) -> 401
- `GET /employer/dashboard` -> 200
- Engine smoke test: 10/10 checks pass (single, batch, approval
  gate, quota, missing key, not-found, cleanup)

---
## SESSION 2026-10-19 - Session 51 (Employer Dashboard)

**Commit:** `4c2ef76`

### Shipped

- Employer Dashboard — B2B product surface for the Trust Score API
- `passport_engine.list_public_passports()` engine method
- 3 new routes: `/api/passport/public/list`, `/employer/dashboard`,
  `/employer/verify/{handle}`
- 2 new templates + "For Employers" nav link
- Bug fix: raw JSON button href set at render time (was JS race)

### Wave 2 status: 66% (Certificate-as-a-Service remains — Session 52)

### Prod verified (2026-10-19)

- `/employer/dashboard` -> 200, renders @hr-6201 (442, developing)
- `/employer/verify/hr-6201` -> 200, component bars 43/50/30/50,
  integrity "elevated", 7 certs, hash `5af408b282c9e447`
- `/api/passport/public/list` -> valid JSON with correct shape

---
## SESSION 2026-10-16 - Session 43-A3.4 + A4

**Commits:** `4e8148a`, `d13d2be`, `69f09d0`, `a4f6354`, `d2531de`, `3b5dc0d`, `13dad7b`

### Shipped

**A3.4 - FYP Refine Section (interactive iterative rewrite)**
- New engine method: `refine_section_ai()` + `_fallback_refine()`
- New route: `POST /api/fyp/refine` (5 credits per instruction)
- Frontend: refine panel inside each expanded chapter
- History preserved in DOM with revert option

**A3.3 - FYP Plagiarism-Safe Rewriter (humanize text)**
- Engine: `humanize_text_ai()` + `_fallback_humanize()`
- Route: `POST /api/fyp/humanize` (15 credits)
- Tone selector (academic / report / casual)

**A4 - Personalized training recommendations**
- `TOPIC_TO_COURSE` + `COURSE_HIGHLIGHTS` dicts (42 topics, 35 courses)
- `get_personalized_recommendations()` in career_assessment_engine
- `_resolve_topic_key()` fuzzy matcher for truncated topic names
- Keyword fallback for topics without explicit mapping
- Route: `GET /api/training-engine/personalized` (auth-gated)
- Frontend: server-call version of loadPersonalizedRecommendations
- Removed client-side `_teTopicToCourseHints` + `_teMatchTopicToCourses`

**Also closed:**
- A1.12 Blue badge candidate reassurance
- A2.1 QR code on certificate PDF
- A1.10 Readiness 404 friendly page
- GPT-4o-mini Phase 1 (centralized OPENAI_MODEL in global_config)
- `multi_pattern` NameError fix

**Remaining in Track A:**
- A1.1 Render Postgres password rotation
- A2.3 Certificate i18n (deferred)
- A6 Benchmark data (needs 200+ certs)
- A7 Certificate-as-a-Service (needs a buyer)

---

## SESSION 2026-10-02/03 - Sessions 8-13 + PayPal sandbox test

**Commits:** `2d600f3`, `abd653d`, `f42a607`, `dac60a8`, `c041328`, `69e3daa`,
`5946ec3`, `86d1653`, `e9b30ab`, `94ab7e1`, `482d653`, `fbc5852`, `a585f21`,
`6c7632a`, `db9e2a1`, `e27f052`, `5acefdb`, `a8f5e59`, `35e1954`, `4961c26`

### Shipped

**Session 8 — University + Legacy-Shift + C7 17/17**
- University subscriptions (3 tiers: starter/growth/enterprise)
- Legacy-Shift Rs 4,999 migration tier
- C7 paid-tier sweep completed 17/17

**Session 9a — Silent-Killer Sentinel**
- Real URL monitoring (was a stub returning fake monitor ids)
- `charvak_silent_killer_watches` + `charvak_silent_killer_scans`
- 7 engine methods, 4 routes, dashboard

**Session 9 quick wins — PayPal sandbox**
- `payment_engine.py` gained `PAYPAL_MODE` env var + `_paypal_base()`
  helper. Defaults to `live`.
- `/api/region` accepts `?country=` / `?currency=` dev override
- Verified the full PayPal capture flow end-to-end with sandbox
  credentials: order -> approval -> capture -> credits -> idempotency

**Sessions 10-13 — Career Assessment (3 phases)**
- Phase 1: new `career_assessment_engine.py`, 106 roles, MCQ only
- Phase 2a: 7 more formats (short_answer, numeracy, situational_judgment,
  behavioral, system_design, debugging, case_study)
- Phase 3: topic tagging, skill gap, cross-assessment adaptive
  difficulty via `ability_engine`, AI-generated learning paths
- 2 formats (coding, sql) still disabled pending Judge0 sandbox

**Session 21 — Indian Language AI MCQ scoring**
- Real deterministic scoring (was counting answers, not correctness)
- 10/15/20 question selector, option shuffle
- Auth + email match on `/api/indian-languages/submit`

**Session 13 doc pass**
- ARCHITECTURE.md refreshed (5 sessions of new sections)
- KNOWN-ISSUES: PowerShell process-kill + mojibake display gotchas
- OUTSTANDING-WORK-INVENTORY: sessions 8-13 closures + follow-ups
- STATUS.md: Session 13 entry

---

## SESSION 2026-09-29 - Auth persistence + cache revalidation

**Commits:** `f58e63f`, `e28c781`

### Shipped
- **Token persistence:** new table `charvak_auth_tokens` (migration 20260929).
  `auth.active_tokens` is now backed by Postgres. `verify_token` reads from
  the DB on cache miss and repopulates the in-memory cache.
- **Cache revalidation:** `CachedStaticFiles` now sends
  `Cache-Control: public, max-age=3600, must-revalidate` instead of
  `max-age=31536000, immutable`. Fixes the `?v=2.x` footgun.
- **AI-Slop Report Card:** `ai-contamination-detector.html` now calls the
  real `/api/products/ai-slop/scan` route (25 cr) instead of `Math.random()`.

### Flags closed
- #2 uvicorn reload invalidates tokens
- #4 CachedStaticFiles ?v=

### Session B addendum - payment flags closed (2026-09-29)

**Commits:** `9130b8f`, `7c679f1`

- **PayPal credits webhook safety net** — if the browser closes after
  PayPal captures but before the frontend POSTs, the webhook grants
  credits idempotently. Custom_id format: `credits|<email>|<plan>`.
- **Signature verification** — `/webhook/paypal` now forwards transmission
  headers to PayPal's verify API and returns 401 on failure. Requires
  `PAYPAL_WEBHOOK_ID` env var. Forged prod payload -> 401.
- **`purchase_credits` import fix** — was importing an instance method as
  a module-level function; every webhook delivery returned
  "cannot import name". Now uses the `ai_credit_engine` singleton.

**Still open:** #3 live PayPal capture test ($2.39 + refund). Code is
ready, fake-payload tests pass in prod. Deferred to a dedicated session
where the full flow can be watched.


### Still open (payment flags)
- #5 ai_courses_payments PayPal stub audit
- #6 PayPal credits webhook safety net
- #3 PayPal credits capture test (live $2.39 + refund)
## SYSTEM OVERVIEW

- Engines: 32+
- Templates: 203
- APIs: 180+
- Languages: 34 global + 12 Indian
- Visa Types: 17
- Security: 7 layers
- Payments: LIVE (Razorpay INR + international, PayPal multi-currency)
- AI Credits: DB-backed, persisted (Fix B - 2026-09-12)
- Course Payments + India EMI: LIVE (2026-09-16)
- Tiered Pricing (Basic/Intermediate/Advanced): LIVE (2026-09-16)
- Mock Drives: DB-backed (2026-09-17)
- Webhook safety net: LIVE (Razorpay + PayPal)

---

## COMPANY

- **Location:** #301, Sri Padmavati Towers, 3rd Lane, Seetaram Nagar, Guntur 522001, Andhra Pradesh, India
- **Email:** hr@charvakit.com
- **Phone:** +91 799 7871 701

**Two products share one Render Postgres database:**
1. **Charvak** (this project) - AI tools, exams, credits, career engine
2. **Dokets VouchAI** - AI escrow platform (dokets.com)

---

## INFRASTRUCTURE

| Service | Identifier | Notes |
|---|---|---|
| Render (Charvak) | `srv-d9hhljd8nd3s73d2hoeg` | Python 3.11.9, Singapore |
| Render (VouchAI) | `srv-d9nque942hec7386q3mg` | Node, Singapore |
| Render Cron | `send-emi-reminders` | Daily 9:00 AM IST - EMI reminder emails |
| Render Postgres | `dpg-d9m92j0ae00c73blvoq0-a` | DB: `vouchai` (shared) |
| GitHub | `ashokdokets-cpu/charvakit-website` | main branch |
| Cloudflare | www.charvakit.com | CDN + DNS |
| Razorpay | LIVE | INR + International payments + webhook |
| PayPal | LIVE | Multi-currency |
| SendGrid | LIVE | Transactional email |
| OpenAI | GPT-4o-mini | AI features |
| ElevenLabs | LIVE | Voice features |

### Local dev

- Postgres 15 installed at `C:\Program Files\PostgreSQL\15`
- Service: `postgresql-x64-15` (Automatic start)
- DB: `vouchai` at `postgresql://postgres:dev@localhost:5432/vouchai`
- `.env.local` present, not committed
- See `DEV-SETUP.md`

### Render env vars
DATABASE_URL (Render Postgres internal URL)
RAZORPAY_KEY_ID (rzp_live_...)
RAZORPAY_KEY_SECRET
RAZORPAY_WEBHOOK_SECRET (Fix C)
PAYPAL_CLIENT_ID
PAYPAL_CLIENT_SECRET
PAYPAL_MODE (live | sandbox; defaults to live)
SENDGRID_API_KEY
OPENAI_API_KEY
ELEVENLABS_API_KEY
SECRET_KEY (64 chars)
SITE_URL (https://www.charvakit.com)
ADMIN_EMAIL (charvakit@gmail.com)
HR_EMAIL (hr@charvakit.com)

text

---

## TECH STACK

| Layer | Technology |
|---|---|
| Backend | Python 3.11.9 + FastAPI + Uvicorn |
| Templates | Jinja2 (203) |
| Database | PostgreSQL via psycopg2 |
| Frontend | Bootstrap 5, vanilla JS, Chart.js |
| Hosting | Render (Singapore) |
| CDN | Cloudflare |
| CI/CD | GitHub push -> Render auto-deploy |

---

## ENGINES (33+)

Core: payment, kyc, escrow, referral, badge, blog, chatbot, sso,
micro_internship, training, interview_prep, job_board,
products, candidate, email, messaging, events, brand, team,
ats, university, enterprise, invoice, tools,
marketing_ai, indian_language_ai, lms, career_v2

Data-backed: `jobs_unified_engine` (Session 31, unified jobs feed), `candidate_profile_engine` (Session 30, unified view), `judge0_client` (Session 28, code execution), `integrity_engine` (Session 27), `ai_credit_engine`, `email_verification`, `ai_courses`, `ai_courses_payments`, `complete_mock_drive`, `results_system`

---

## FEATURES

- **Career Assessment** (v3.5, Sessions 10-13): 8 formats, 106 roles x 66 industries x 7 levels, adaptive difficulty, skill gap, AI-generated learning paths at `/ai-assessment`
- **University Portal** (v3.5, Session 8): 3 paid tiers, credit-based subscriptions
- **Silent-Killer Sentinel** (v3.5, Session 9a): real URL monitoring
- **Legacy-Shift Migration Tier** (v3.5, Session 8): Rs 4,999 plan
- **Indian Language AI** (v3.5, Session 21): real MCQ scoring

- 16 AI Products + 12 AI Tools
- NA Module (17 visas, 6 files)
- Career Center (alerts, saved jobs, interviews, offers)
- LMS (ratings, quizzes, certificates, lessons, payouts)
- Marketing AI (job ads, social posts)
- Indian Language AI (12 languages)
- Enterprise (Teams, ATS, University, Enterprise)
- AI Credits (purchase, daily bonus, usage history - persisted)
- Exam Prep (122 exams, Indian + global)
- **AI Courses** (catalog, lessons, certificates - persisted)
- **AI Course Fee + India EMI + Global Pricing** (v2.0)
- **Tiered Pricing** (Basic/Intermediate/Advanced - v2.1)
- **Company Mock Drives** (18 companies, AI-generated, persisted - v2.2)

---

## DATABASE SCHEMA

### Charvak-owned tables

| Table | Purpose |
|---|---|
| `users` | email, password_hash, name, phone, role |
| `email_verification_tokens` | token, email, expires_at, verified |
| `password_reset_tokens` | reset flow |
| `contacts` | contact form submissions |
| `charvak_user_credits` | email PK, plan, credits_remaining, daily_usage (JSONB), expires_at |
| `charvak_credit_usage_history` | every deduction |
| `charvak_credit_purchases` | purchase log; `payment_id` UNIQUE for idempotency |
| `charvak_courses` | 25-course catalog, price_inr source of truth |
| `charvak_enrollments` | enrollment state, user_level (beginner/intermediate/advanced) |
| `charvak_course_lessons` | weekly lessons (JSONB content) |
| `charvak_certificates` | issued certificates with recipient name |
| `charvak_course_prices` | 175 rows (25 courses x 7 Tier-1 markets) |
| `charvak_course_payments` | per-payment log; `razorpay_payment_id` UNIQUE |
| `charvak_course_installments` | India EMI schedule (milestone-block model) |
| `charvak_course_levels` | 75 rows (25 courses x 3 levels) |
| `charvak_mock_sessions` | one row per started company mock drive |
| `charvak_mock_answers` | one row per answered question |
| `charvak_assessment_results` | every assessment result |
| `charvak_interview_sessions` | Interview prep sessions |
| `charvak_interview_answers` | Interview prep answers |
| `charvak_referrals` | referral codes + referrer info |
| `charvak_referral_clicks` | click tracking |
| `charvak_referral_bounties` | bounty payments |
| `charvak_jobs` | job board postings |
| `charvak_applications` | job applications |
| `charvak_skill_gaps` | skill gap analysis |
| `charvak_synced_users` | Dokets RB sync |
| `charvak_synced_applications` | Dokets RB sync |

| `charvak_career_assessments` | Career Assessment parent rows (role x industry x level, questions_json, learning_path_json) |
| `charvak_career_assessment_answers` | Per-question answers (idempotent per assessment+question_index) |
| `charvak_university_subscriptions` | University portal subscriptions (starter/growth/enterprise) |
| `charvak_legacy_shift_reports` | Legacy-Shift migration plans (analysis_json + plan_json) |
| `charvak_silent_killer_watches` | URL monitor watches |
| `charvak_silent_killer_scans` | URL scan history per watch |

### VouchAI-owned tables (shared DB, do not touch)

`Contract`, `Dispute`, `Milestone`, `Payment`, `User`, `UserAchievement`

---

## API ENDPOINTS (key)

### Auth
- `POST /api/auth/register`
- `POST /api/auth/login` - email verification check + admin bypass
- `POST /api/auth/logout`, `/api/auth/logout-all`
- `GET /api/auth/me`

### Credits
- `GET /api/credits/plans`
- `GET /api/credits/{email}`
- `POST /api/credits/check`
- `POST /api/credits/purchase`
- `POST /api/credits/daily-bonus`
- `GET /api/credits/expiry/{email}`, `/api/credits/usage/{email}`
- `GET /api/credits/admin/stats`

### Payments
- `POST /api/payment/create-order`
- `POST /api/payment/verify`
- `GET /api/payment/history`
- `POST /webhook/razorpay`
- `POST /webhook/paypal`

### AI Courses
- `GET /api/ai-course/catalog`
- `GET /api/ai-course/course/{course_name}` - returns levels[]
- `GET /api/ai-course/price/{course_name}?level=X&country=YY`
- `POST /api/ai-course/enroll` - FREE path (price 0)
- `POST /api/ai-course/create-order`
- `POST /api/ai-course/confirm-payment`
- `GET /api/ai-course/installments/{enrollment_id}`
- `GET /api/ai-course/access/{enrollment_id}/{week_num}`
- `POST /api/ai-course/complete-week`
- `POST /api/ai-course/complete`
- `GET /api/ai-course/certificate/{certificate_id}`

### Company Mock Drives
- `GET /mock-drive` - page (v2.2)
- `GET /api/company-patterns/{company_id}`
- `POST /api/mock/start-complete`
- `POST /api/mock/submit-complete`
- `POST /api/mock/complete-full`


### Candidate Profile + Signup (Sessions 30, 32)

- `GET /api/candidate/{email}/unified` — self-view of full activity
- `POST /api/candidates/upsert` — unified candidate write (whitelisted)
- `GET /career-center/jobs` — unified jobs page
- `GET /candidate/signup` — marketing gate -> /profile when authed
- `/candidate-signup`, `/developer-signup` — 302 -> /candidate/signup
### Jobs Unified (Session 31)

- `GET /api/jobs/unified` — public feed across job-board + staffing + gigs.
  Supports `?source=`, `?q=`, `?limit=` filters.
- `GET /career-center/jobs` — Career Center jobs page (HTML)
### Candidate Profile (Session 30)

- `GET /api/candidate/{email}/unified` — self-view of the candidate's
  full activity across all subsystems. Supports `?include=` filter.
### Integrity (Session 27)

- `POST /api/integrity/event` — record one environment signal (auth + ownership)
- `GET  /api/admin/career-assessment/{aid}/integrity` — admin view (events + summary)

### Results
- `POST /api/results/record`
- `GET /api/results/user/{email}`
- `GET /api/results/readiness/{email}`

### Admin
- `/admin-login`, `/admin-control`
- All `/admin*` routes protected by middleware

---

## PAYMENT FLOW

### Credit purchase
User selects plan
-> POST /api/payment/create-order
-> Razorpay order created with notes: {plan, email, tool, amount_inr}
-> Client pays, calls /api/payment/verify + /api/credits/purchase
-> Webhook /webhook/razorpay idempotent fallback

text

### Course fee + EMI (v2.0)
Student picks level (beginner/intermediate/advanced)
-> GET /api/ai-course/price/{course}?level=X&country=YY

Student clicks Enroll
-> POST /api/ai-course/create-order
India: charges first installment only
Global: charges full price

-> POST /api/ai-course/confirm-payment
Verifies, fetches gateway, records, unlocks block

-> Webhook branches on notes.tool == "ai_course"

text

### EMI milestone-block model (India only)
- 2 blocks up to 8 weeks, 3 blocks for longer
- Each paid installment unlocks its block
- Locked weeks show "Pay to Unlock" card
- 24h-throttled in-context reminder email

### Reminder emails
- Render Cron `send-emi-reminders` daily 9 AM IST
- Stages: T-3d, due-date, +1d, +3d, +7d
- Dedupe via `last_reminder_stage`

**Idempotency:** `payment_id` UNIQUE on purchases + course_payments

---

## ADMIN ACCOUNTS

| Email | Role |
|---|---|
| charvakit@gmail.com | Admin |
| hr@charvakit.com | Admin |

**Rotate password:** `python scripts/rotate_admin_password.py`

---

## PROJECT STRUCTURE
charvakit-new/
â”œâ”€â”€ main.py # FastAPI app (~5900 lines)
â”œâ”€â”€ auth.py # Register, login, tokens
â”œâ”€â”€ database.py # DB connection + user CRUD
â”œâ”€â”€ payment_engine.py # Razorpay + PayPal + webhook sig verify
â”œâ”€â”€ ai_credit_engine.py # DB-backed credits
â”œâ”€â”€ ai_courses.py # AI courses + certificates
â”œâ”€â”€ ai_courses_payments.py # Course payments + India EMI (NEW v2.0)
â”œâ”€â”€ complete_mock_drive.py # Company mock drives (DB-backed v2.2)
â”œâ”€â”€ results_system.py # Assessment results (DB-backed v2.2)
â”œâ”€â”€ notification_engine.py # Email notifications + EMI reminders
â”œâ”€â”€ email_verification.py # DB-backed verification
â”œâ”€â”€ password_reset.py
â”œâ”€â”€ email_engine.py # SendGrid
â”œâ”€â”€ [40+ other engines]
â”œâ”€â”€ templates/ # 203 Jinja2 pages
â”œâ”€â”€ static/ # css, js, images, fonts
â”œâ”€â”€ na_module/ # North America modules
â”œâ”€â”€ migrations/ # SQL migrations (idempotent)
â”œâ”€â”€ scripts/ # Dev/ops scripts
â”œâ”€â”€ requirements.txt, runtime.txt
â”œâ”€â”€ .env # Never committed
â”œâ”€â”€ STATUS.md
â”œâ”€â”€ MASTER-REFERENCE.md # <- this file
â”œâ”€â”€ ARCHITECTURE.md
â”œâ”€â”€ TIER3-MASTER-PLAN.md
â”œâ”€â”€ PAGES-INVENTORY.md

text

---

## OPERATING COMMANDS

```powershell
# Local dev
uvicorn main:app --reload --port 8000

# Backup
python scripts/full_backup.py

# Rotate admin password
python scripts/rotate_admin_password.py

# Send EMI reminders manually
python scripts/send_emi_reminders.py

# Tag a stable release
git tag -a "vX.Y-stable-YYYYMMDD" -m "description"
git push --tags
BACKUPS
Latest: Charvak_Complete_Backup_20260917_012029.zip (6.39 MB, 1,014 entries)

Includes source, templates, static, migrations, scripts, .env, .git/, _DB_DUMP/ (24 tables), docs.

Security note: backup ZIPs contain .env secrets - do not share publicly.

KNOWN ISSUES / TODO

See KNOWN-ISSUES.md for the full list.

- [ ] Rotate PayPal client secret (deferred)
- [ ] Fix heading order on remaining pages (accessibility)
- [ ] TBT ~1,900ms mobile - needs conditional script loading
- [ ] Session 5C (mock engine consolidation) queued
- [ ] Backfill missing migrations/20260916_charvak_enrollments.sql
- [ ] Fix 20260916_course_payments.sql FK ordering
- [ ] Persist remaining 24 engines (Sessions B, D, F, H + Tier E verify)
- [ ] Exam prep frontend mock-test UI (backend + routes are live)
- [ ] Analytics Dashboards audit

EXTERNAL DASHBOARDS
Render: https://dashboard.render.com

GitHub: https://github.com/ashokdokets-cpu/charvakit-website

Razorpay: https://dashboard.razorpay.com

SendGrid: https://app.sendgrid.com

OpenAI: https://platform.openai.com

Cloudflare: https://dash.cloudflare.com

Keep this file updated after major changes.

text

---

## Step 3 — After saving, verify

```powershell
Set-Location "C:\Users\lenovo\OneDrive\Desktop\charvakit-new"

$bytes = [System.IO.File]::ReadAllBytes("MASTER-REFERENCE.md")
Write-Host "Size: $($bytes.Length) bytes"
Write-Host "Lines: $((Get-Content MASTER-REFERENCE.md).Count)"
Write-Host "First 3 bytes: $($bytes[0]) $($bytes[1]) $($bytes[2])"

Write-Host "`nFirst 5 lines (UTF-8 aware):" -ForegroundColor Cyan
$lines = [System.IO.File]::ReadAllLines("MASTER-REFERENCE.md", [System.Text.Encoding]::UTF8)
for ($i = 0; $i -lt 5; $i++) {
    Write-Host ("{0,4}: {1}" -f ($i+1), $lines[$i])
}

Write-Host "`nMarkers:" -ForegroundColor Cyan
@("v2.2-mock-drives-20260917","charvak_course_levels","AI Course Fee") | ForEach-Object {
    $found = $false
    foreach ($l in $lines) { if ($l -match [regex]::Escape($_)) { $found = $true; break } }
    Write-Host ("  {0,-40} {1}" -f $_, $(if ($found) { 'OK' } else { 'MISSING' })) -ForegroundColor $(if ($found) { 'Green' } else { 'Red' })
}



## SESSION 2026-10-05 - Session 24 (Client Roles Admin UI)

**Commit:** `37f978f`

### Shipped

- **/admin/client-roles** - list of all client roles with applicant
  counts, summary strip, status filters, per-row actions
- **/admin/client-roles/{role_id}** - role info + ranked applicant
  list + View modal + Download Package button

### Bugs fixed during session

- Modal moved from content block to modal block slot to escape
  the `<main>` stacking context
- Modal button bindings moved inside DOMContentLoaded
- Removed a template-tag reference inside a JS comment that Jinja
  was parsing as a real tag
- Restored click delegation handler that had been lost in an earlier
  patch
- Exposed `loadAll` / `loadRoles` on window for inline Refresh buttons

### Local dev admins added

- `hr@charvakit.com` / `DevPass!2026#HR`
- `charvakit@gmail.com` / `DevPass!2026#CV`
- Both added to `ADMIN_EMAILS` in `.env.local`

### Prod verified

- `/admin/client-roles` -> 302 (redirect to login = gate works)
- Old `/cbrex-package` route -> 401 (retired)

<!-- BEGIN SESSION-48 -->

## SESSION 2026-10-18 - Session 48 (Cohort Mode - Wave 1 Complete)

**Commit:** 1399073

### Shipped

- Cohort Mode (batch leaderboards for college cohorts, coaching groups, training batches)
- cohorts_engine.py: 5 methods (create, join, leaderboard, mine, refresh)
- 3 new tables: charvak_cohorts, charvak_cohort_members, charvak_cohort_leaderboard
- 8 new routes: /cohorts, /cohorts/{id}, /cohorts/join/{code} + 5 API
- 2 new templates: cohorts.html, cohort-detail.html
- base.html: nav + footer "My Cohorts" links
- passport.html: "My Cohorts" section for owner

### Composite Score Formula (Cohort Leaderboard)

composite = passport.charvak_score * 0.6 + min(current_streak * 5, 100) + min(weekly_drills * 10, 150)

### Session 47.5 - Migration Pipeline (same week)

- scripts/run_migrations.py shipped and wired into Render start command
- 3 non-blocking migration warnings fixed (skill_twin_badge, assessment_integrity, mba_courses)
- 89 migrations clean on prod (failed_or_already_exists=0)

### Wave 1 - Complete

| Layer | Session | Table(s) |
|---|---|---|
| Identity (Passport) | 46-A | charvak_passports |
| Viral (Challenges) | 46-B | charvak_skill_twin_challenges |
| Habit (Drills + Streaks) | 47 | charvak_daily_drills, charvak_user_streaks |
| Batch (Cohorts) | 48 | charvak_cohorts, charvak_cohort_members, charvak_cohort_leaderboard |

### Verified E2E on Prod

- /cohorts returns 200, renders correctly
- /cohorts/COH-{id} returns 200, leaderboard computes
- /passport/{handle} shows "My Cohorts" section for owner
- Migration 20261018_cohorts.sql applied automatically on deploy

### Next Session Candidates

- A) Polish Cohort Mode (~3-4 hrs): leave, rename, delete, promote admin, public discovery
- B) Trust Score Public API (~2-3 hrs): employer verification endpoint
- C) Passport Share Integration (~1-2 hrs): one-click LinkedIn badge, og:image
- D) Real usage analytics (~2-3 hrs): view count, share count tracking

<!-- END SESSION-48 -->

<!-- BEGIN SESSION-49-49.5 -->

## SESSION 2026-10-19 - Session 49 + 49.5 (Cohort RBAC + Public Toggle)

**Commit:** 5525cd7 (Session 49) + d3de41b (Session 49.5)
**Wave 1:** Complete with production-quality polish

### Session 49 - Cohort RBAC + Discovery polish (commit 5525cd7)

Closes 5 product gaps identified at Session 48 close-out.

Backend (cohorts_engine.py):
- leave_cohort(cohort_id, member_email) - member leaves, owners blocked
- rename_cohort(cohort_id, caller_email, new_name) - owner only
- delete_cohort(cohort_id, caller_email) - owner only, cascade
- promote_admin(cohort_id, caller_email, target_email) - owner only
- demote_admin(cohort_id, caller_email, target_email) - owner only
- list_public_cohorts(limit=50) - discovery

Routes (main.py): 6 new endpoints
- GET    /api/cohorts/public
- POST   /api/cohorts/{id}/leave
- POST   /api/cohorts/{id}/rename
- DELETE /api/cohorts/{id}
- POST   /api/cohorts/{id}/promote
- POST   /api/cohorts/{id}/demote

Frontend: owner actions menu, member list with role badges,
leave button for non-owners, rename/delete confirmation modals,
promote/demote inline actions, public discovery section.

### Session 49.5 - Public cohort toggle (commit d3de41b)

Closes the last Wave 1 gap - public discovery section was unusable
because no UI existed to make cohorts public.

- create_cohort() accepts is_public kwarg
- set_cohort_visibility(cohort_id, caller_email, is_public) - owner only
- POST /api/cohorts/{id}/visibility route
- "Make this cohort public" checkbox in create modal
- "Make Public" / "Make Private" toggle button in owner actions
- is_public now returned in get_leaderboard (both cache paths)

### Critical fixes discovered during E2E

1. Role field missing from leaderboard cache-hit path
   (Session 49's promote/member list depended on it)
2. Cache not invalidated on join/leave (stale leaderboard)
3. Create/join modals trapped in {% block content %} (faded backdrop)
   Moved to {% block modal %} slot per Session 24 lesson
4. is_public missing from leaderboard API response (label stuck at default)

### Wave 1 - Complete with polish

| Layer | Session | Status |
|---|---|---|
| Identity (Career Passport) | 46-A | DONE |
| Viral (Skill Twin Challenges) | 46-B | DONE |
| Habit (Daily Drills + Streaks) | 47 | DONE |
| Batch (Cohort Mode) | 48 + 49 + 49.5 | DONE + POLISHED |

### Session 50 candidates

- A) Trust Score Public API (~2-3 hrs) - employer verification endpoint
- B) Employer Dashboard (~4-5 hrs) - browse verified candidates
- C) Certificate-as-a-Service (~2-3 hrs) - bulk verify for universities
- D) Docs sync + retrospective (~30 min)

<!-- END SESSION-49-49.5 -->
