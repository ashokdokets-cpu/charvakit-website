# Charvak IT Consulting - Project Status

**Last updated:** 2026-10-03 (Session 13 - Career Assessment Phase 3 + PayPal sandbox test)
**Version:** v3.5-session-13-20261003
**Live:** https://www.charvakit.com
**Status:** Tier 1 + Tier 2 complete. Tier 3 in progress (6 of 10 features shipped). Session K closed: 3 security + 5 data integrity + 4 deferrals + 16 dead-field/easy-bug fixes + 2 migration features. B-3 notification persistence done. B-4 products verified stateless.

## Session 2026-10-09 - Session 42 (certificate polish + funnel wiring + AI course designer)

**HEAD:** 9d2aced

11 commits, four real bugs fixed, four new features shipped. The
complete student funnel now works end-to-end.

### Shipped

- **Certificate polish** (42-0): signature block, wordmark header,
  quiet integrity badge, honest comparison strip, CTA copy
- **Code cleanups** (42-1): charvakFetch global, seed env fix,
  Versant passed column, .gitignore cleanup, PDF "Your Score",
  "N cr" -> "N credits"
- **Readiness SEO + GA4** (42-2): meta tags, sitemap, 4 funnel events
- **Placement-prep landing** (42-3): /placement-prep-2026, URL
  preselect, login gate, pattern-selection bug fix
- **Shareable mock result** (42-3/4): /mock-result/{session_id},
  next-step block with readiness + courses + retake
- **AI Course Designer** (42-5): designer card on /ai-courses,
  custom-list API, ?next= auth fix

### Bugs fixed

1. Empty signature block on the readiness PDF
2. Pattern selection on /mock-drive generated the wrong questions
3. Login dead-end on any ?next= redirect
4. Register flow ignoring ?next=

### Verified in production

- /placement-prep-2026  200
- /ai-courses           200
- /readiness-check      200

### Backup

Charvak_Complete_Backup_20261009_061207.zip (60.94 MB, 813 files,
167 charvak_* tables, HEAD at 9d2aced)

### Next session

Read the launch numbers first. Then decide the next feature based on
what real users actually did, not speculation.

---

## Session 2026-10-03 - Session 13 (Career Assessment Phase 3 + PayPal sandbox test)

### Shipped

**Career Assessment Phase 3 (Sessions 10-13 cumulative)**
- Topic tagging: 7 role categories x 8 topics each. Every question
  tagged with 1-2 topics at generation time.
- Skill gap analysis: per-topic blended score, strong/mixed/weak labels,
  weakest-first sort in the response.
- Cross-assessment adaptive difficulty: reads `ability_engine` on
  /start, seeds the prompt with a difficulty hint (foundation-first /
  standard / challenge based on Elo bands).
- Ability engine update on /complete (first real use since Session C4).
- AI-generated learning paths: matches `charvak_courses` from the
  25-course catalog, curates external resources, generates a 2-4
  week plan. Cached after first generation.

**Career Assessment formats shipped (Sessions 10-11)**
- 8 formats: mcq, short_answer, numeracy, situational_judgment,
  behavioral, system_design, debugging, case_study
- 2 more shown but disabled (coding, sql - need a sandbox; Session 14)
- Catalog: 106 roles, 66 industries, 7 experience levels

**University Subscriptions (Session 8)**
- 3 tiers: starter (4000 cr), growth (10000 cr), enterprise (20000 cr)
- Security fix: `/api/university/register` was open IDOR

**Legacy-Shift Migration Tier (Session 8)**
- Rs 4,999 migration plan (1000 cr)
- Real file-by-file plan with data migration + rollback

**Silent-Killer Sentinel (Session 9a)**
- Real URL monitoring (was a stub)
- Watch + scan tables, 7 engine methods, 4 routes, dashboard

**Indian Language AI MCQ scoring (Session 21)**
- Real deterministic scoring (was counting answers)
- 10/15/20 question selector, option shuffle, auth on /submit

**C7 paid-tier sweep (Sessions 3-8)**
- 17/17 templates shipped. Complete.

**Session 9 quick wins (2026-10-03)**
- PayPal credits capture test: verified end-to-end with a US sandbox
  buyer + US sandbox merchant. Order -> approval -> capture -> credits
  -> idempotency all confirmed.
- ARCHITECTURE.md refresh: 5 sessions of new sections added.
- KNOWN-ISSUES: PowerShell process-kill and mojibake display gotchas.
- OUTSTANDING-WORK-INVENTORY: sessions 8-13 closures + follow-ups.

### Code changes

New engine: `career_assessment_engine.py` (~900 lines)

New tables:
- `charvak_career_assessments`
- `charvak_career_assessment_answers`
- `charvak_university_subscriptions`
- `charvak_legacy_shift_reports`
- `charvak_silent_killer_watches`
- `charvak_silent_killer_scans`

New env vars:
- `PAYPAL_MODE` (`live` | `sandbox`; defaults to `live`)

New credit keys (11 total for career assessment):
- Deterministic: `career_assessment_quick|standard|full` (15/25/35)
- AI-scored: `career_assessment_ai_quick|standard|full` (20/30/40)
- University: `university_starter|growth|enterprise` (4000/10000/20000)
- Legacy-Shift: `legacy_shift_migration` (1000)
- Silent-Killer: `product_silent_killer` (15), `silent_killer_recheck` (5)

### Verified

- Career Assessment E2E: 8 formats, real scoring, adaptive flow,
  learning paths
- PayPal sandbox: order -> approval -> capture -> credits -> idempotency
- All new routes tested with auth + credit gates
- Production live and verified

### Still pending

- Career Assessment Phase 2b: coding + SQL via Judge0 (Session 14)
- Silent-Killer continuous cron (Session 9b)
- Difficulty-aware ability update (Session 14, ~30 min)
- `PAYPAL_MODE=live` explicit on Render (1 min)

---

## Session 2026-09-29 - Auth persistence + cache revalidation

### Shipped
- Token persistence to Postgres (`charvak_auth_tokens`). `verify_token`
  falls back to the DB on cache miss. Survives uvicorn reload and Render
  redeploy. Verified: log in -> restart uvicorn -> same token returns 200.
- Cache-Control revalidation: `CachedStaticFiles` now `max-age=3600,
  must-revalidate`. The `?v=2.x` bump footgun is retired.
- AI-Slop Report Card (ai-contamination-detector.html) now calls the real
  `/api/products/ai-slop/scan` route instead of `Math.random()`.

### Flags closed
- #2 uvicorn reload invalidates tokens
- #4 CachedStaticFiles ?v=

### Pending
- #5 ai_courses_payments PayPal stub audit (audit done, no code change needed)
- #6 PayPal credits webhook safety net
- #3 PayPal credits capture test

**HEAD:** `6fa14d1`

---
---

---

## Session 2026-09-28 - Session C (AI tools + security sweep)

### Shipped
- 4 unlisted AI tools rebuilt with real forms + credits flows:
  Neural Wireframe (25 cr), Globalize.ai (15 cr), Legacy-Shift (20 cr), Agent-Ready (15 cr)
- FYP Per-Chapter Expand (10 cr per chapter, DOM-cached)
- Internship admin dashboard (/admin/internship-enrollments)

### Security
- 20 unguarded /api routes secured (require_admin or require_auth_for_email)
- 4 AI tool routes now require email-match auth
- **147 HTTPException re-raise clauses** - the guards added today were
  being swallowed by route-level except Exception blocks; this fix made them fire
- Lazy-import-in-pool deadlock sweep: zero remaining sites

### Docs
- SYSTEM-AUDIT-2026-09-28.md produced
- All reference docs synced to HEAD
- Backup at C:\projects\Charvak_Complete_Backup_20260928_230130.zip (50.5 MB)

### Verified E2E
- Neural Wireframe: pricing-page description -> real React+Tailwind JSX
- Globalize.ai: example.com -> Spanish translations + LOPDGDD compliance
- Legacy-Shift: legacy PHP -> SQL injection + XSS + migration steps
- Agent-Ready: example.com -> JSON-LD + micro-APIs + product schema
- All 4 routes return 401 without auth (verified via curl)

**HEAD:** `6fa14d1`


## Session 2026-09-19 - Session K (Security + Data Integrity + Cleanup)

### Shipped to production

**Security (3 items)**
- K/1: Auth guard on `/api/exam/{progress,history,study-plan}` (was IDOR)
- K/2: `/api/payment/status` trimmed to booleans only (was leaking key_ids + mode)
- K/3: `recommend_custom_role` restricted to admin-only

**Data integrity (5 items)**
- K/4: `revenue_engine.create_subscription` no longer double-counts on tier change
- K/5: `resume_engine.SubVendorManager.track_submission` counter only bumps on new inserts
- K/6: `charvak_vms.approve_timecard` idempotency guard
- K/7: outreach UNIQUE constraint on email (migration applied to prod)
- K/8: `messaging_engine.get_stats` includes `replied` in read count

**Dead fields + easy bugs (16 items)**
- Removed 2 misleading placeholder stats
- Fixed 11 small logic bugs (chatbot FAQ, review typo, monitor async, ATS keys, median math, etc.)
- Verified 5 dead fields already resolved

**New persistence features (2 items)**
- K/29: `indian_language_ai.submit_assessment` persists to `charvak_lang_ai_submissions`
- #37b: `enterprise_engine.kiosk_check_in` logs events to `charvak_enterprise_kiosk_events`

**B-3: notification_engine persistence**
- New table: `charvak_notifications`
- `send_email` INSERTs every notification (was in-memory only)
- `get_notification_history` and `get_stats` read from DB

**B-4: products_engine verified stateless**
- Removed dead `self.results = []` field
- All 11 product methods were already compute-and-return

### Migrations applied

- `migrations/20260919_outreach_unique_email.sql` (K/7)
- `migrations/20260919_lang_and_kiosk.sql` (K/29 + #37b)

Both applied to prod via Render Shell 2026-09-19.

### Documentation

- `SESSION-K-SUMMARY.md` — Session K record
- `DEFERRALS.md` — 8 documented design decisions
- `DOC-STYLE.md` — code/doc/commit style guide
- `SCHEMA.md` — auto-generated schema for all 128 tables
- `OUTSTANDING-WORK-INVENTORY.md` — master backlog

---

## Quick Links

- **Production:** https://www.charvakit.com
- **Render (Charvak):** https://dashboard.render.com - service `srv-d9hhljd8nd3s73d2hoeg`
- **Render (VouchAI):** service `srv-d9nque942hec7386q3mg`
- **GitHub:** https://github.com/ashokdokets-cpu/charvakit-website
- **Razorpay:** https://dashboard.razorpay.com
- **SendGrid:** https://app.sendgrid.com
- **Cloudflare:** https://dash.cloudflare.com

**Full docs:**
- `MASTER-REFERENCE.md` - comprehensive technical reference
- `ARCHITECTURE.md` - system architecture, flows, schema
- `PAGES-INVENTORY.md` - every template documented
- `TIER3-MASTER-PLAN.md` - Tier 3 execution plan

---

## Infrastructure

| Layer | Where |
|---|---|
| App | Render (Singapore) - Python 3.11.9 + FastAPI + Uvicorn |
| Database | Render Postgres `dpg-d9m92j0ae00c73blvoq0-a`, db `vouchai` (shared with Dokets VouchAI) |
| CDN | Cloudflare |
| Email | SendGrid |
| Payments | Razorpay (INR + international) + PayPal (multi-currency) |
| AI | OpenAI GPT-4o-mini + ElevenLabs |
| Cron | Render Cron Job `send-emi-reminders` (daily 9:00 AM IST) |

---

## Git Tags

| Tag | Date | Meaning |
|---|---|---|
| `v2.2-mock-drives-20260917` | 2026-09-17 | **Latest** - Company mock drives persist + frontend fixes |
| `v2.1-tiered-pricing-20260916` | 2026-09-16 | Basic/Intermediate/Advanced tiered pricing |
| `v2.0-course-emi-20260916` | 2026-09-16 | AI course fee + India EMI + global pricing |
| `v1.9.1-precourseEMI-20260916` | 2026-09-16 | Safety tag before EMI work |
| `v1.9-enterprise-page-20260916` | 2026-09-16 | Enterprise landing page + lead capture |
| `v1.8-ai-courses-20260916` | 2026-09-16 | AI Courses (catalog, lessons, certificates) |
| `v1.7-interview-prep-ai-20260916` | 2026-09-16 | Interview prep with AI scoring + credits |
| `v1.6-referral-persistent-20260915` | 2026-09-15 | Referral system persistence |
| `v1.5-jobboard-persistent-20260915` | 2026-09-15 | Job board persistence |
| `v1.4-tier2-complete-20260914` | 2026-09-14 | Tier 2 complete |
| `v1.3-accessibility-20260913` | 2026-09-13 | Accessibility 69 to 90 |
| `v1.2-tier1-complete-20260913` | 2026-09-13 | Tier 1 complete |
| `v1.1-stable-20260913` | 2026-09-13 | Docs milestone |
| `v1.0-stable-20260911` | 2026-09-11 | Pre-session stable |
| `v1.0.1-pre-fix-b` | 2026-09-11 | Before Fix B (credits persistence) |

---

## Latest Backup

`C:\Users\lenovo\OneDrive\Desktop\Charvak_Complete_Backup_20260917_012029.zip` (6.39 MB, 1,014 entries)

Contains: all source code, templates, static assets, migrations, scripts, `.env`, `.git/` history, DB dump (24 tables, 362 rows), and master docs.

---

## Session 2026-09-16/17 - Tier 3 (Course Fee, EMI, Tiered Pricing, Mock Drives)

### Shipped to production

**AI Course Fee + India EMI + Global Pricing (v2.0)**
- 3 new tables: `charvak_course_prices`, `charvak_course_payments`, `charvak_course_installments`
- 175 seed prices (25 courses x 7 Tier-1 markets)
- India: 2 or 3 milestone-block EMIs based on course duration
- Global: one-time Razorpay (international) or PayPal, in local currency
- IP-based location fallback for currency detection
- PayPal webhook added; Razorpay webhook extended for course payments
- Race-safe idempotency on `razorpay_payment_id`

**Basic/Intermediate/Advanced Tiered Pricing (v2.1)**
- 1 new table: `charvak_course_levels` (75 rows = 25 courses x 3 levels)
- Multipliers: Beginner 0.60x price / 0.70x weeks; Advanced 1.60x / 1.30x
- Level selector on course page with live price/EMI refresh
- Level-aware reuse check (same level reuses, different level creates new)

**Company Mock Drives persistence + frontend (v2.2)**
- 3 new tables: `charvak_mock_sessions`, `charvak_mock_answers`, `charvak_assessment_results`
- `complete_mock_drive.py` and `results_system.py` now persist to Postgres
- 4 frontend bugs fixed in `companies.html` (fake score, lost answers, prompt(), quote escaping)
- New `GET /mock-drive` route + nav link
- `companies.html` converted to `{% extends "base.html" %}`

### Verification

- All 3 features tested E2E on production
- Real browser test: TCS mock drive with 9 answers, real score 18.9%
- All DB tables verified in prod

### Cron

- Render Cron Job `send-emi-reminders` running daily at 9:00 AM IST
- Sends T-3d, due-date, +1d, +3d, +7d escalating EMI reminders

### Backup

- `Charvak_Complete_Backup_20260917_012029.zip` (6.39 MB, 1,014 entries)
- Includes code + DB dump + `.git` history + docs

### Bugs caught by testing (before deploy)

- SQL identifier vs parameter (would 500 every course enrollment)
- Wrong duration source (wrong EMI blocks)
- Hardcoded `user_level='beginner'` overwrite (all tiers reset)
- Reuse check too broad (wrong level silently reused)
- Duplicate `let currentPlan` (infinite spinner)
- AI 'correct' field returned as string (crash on int())
- Onclick quote escaping in JS template (killed entire script block)

---

## Tier 1 - COMPLETE (10/10)

See archived sessions below.

---

## Tier 2 - COMPLETE

See archived sessions below.

---

## Tier 3 - In Progress (6 of 10 shipped)

| # | Feature | Status |
|---|---|---|
| 1 | Job Board | Shipped (v1.5) |
| 2 | Referral System | Shipped (v1.6) |
| 3 | Interview Prep | Shipped (v1.7) |
| 4 | AI Courses | Shipped (v1.8) + course fee/EMI (v2.0) + tiered pricing (v2.1) |
| 5 | Enterprise page | Shipped (v1.9) |
| 6 | Company Mock Drives | Shipped (v2.2) |
| 7 | University Portal | Next - Session 4 |
| 8 | Analytics Dashboards | Next - Session 4 |
| 9 | Micro-Internship | Session 5A (queued) |
| 10 | WhatsApp Bot | Blocked (Meta number registration) |

### Session 5C - Flagged for future

Three more in-memory mock systems that deserve their own pass:

- `advanced_assessment_engine.py` - separate mock-drive variant at `/api/assessment/mock-drive`
- `company_assessment` / `company_mock_complete.py` - separate mock at `/api/company/*-mock`
- `/companies` route currently renders the mock-drive UI; should eventually become a brand directory while the mock UI stays at `/mock-drive`

---

## Known Issues

- **Heading order** - some pages may still have h4-to-h3 skips (accessibility)
- **Contrast** - Lighthouse flags some text/background pairs
- **TBT ~1,900 ms mobile** - deferred scripts fire in burst
- **`.env` in backup ZIPs** - treat backup archives as sensitive
- **Root directory has ~30 one-off dev scripts** - cosmetic cleanup pending
- **`.bak-*` files in root** - 30+ historical backups; cleanup pending
- **BOM in some files** - harmless in `.py` (Python 3 strips it); verify before editing `.html`
- **`wget.exe` in project root** - 6.88 MB binary, unused; delete candidate
- **OneDrive file-lock issues** - project lives in `OneDrive/Desktop`; several git operations hit transient locks. Consider moving to `C:\projects\charvakit-new`.
- **Rotate leaked credentials** - Render Postgres password + PayPal secret were displayed in chat 2026-09-16; rotation pending
- **SYNC_API_KEY / SYNC_API_SECRET** - hardcoded defaults in public repo; dual-key rotation pending

---

## Environment Variables

### Required on Render + local `.env`
DATABASE_URL (Render Postgres internal URL)
RAZORPAY_KEY_ID (rzp_live_...)
RAZORPAY_KEY_SECRET
RAZORPAY_WEBHOOK_SECRET
PAYPAL_CLIENT_ID
PAYPAL_CLIENT_SECRET
SENDGRID_API_KEY
OPENAI_API_KEY
ELEVENLABS_API_KEY
SECRET_KEY (64 chars)
SITE_URL (https://www.charvakit.com)
ADMIN_EMAIL (charvakit@gmail.com)
HR_EMAIL (hr@charvakit.com)

text

---

## Archived Sessions

### Session 2026-09-12/13 - Tier 1 + Security + Performance

**Security (P0 fixes):**
- Fix A - `/api/credits/purchase` now requires verified Razorpay payment for paid plans
- Fix B - Credits persisted to Postgres (`charvak_user_credits`, `charvak_credit_usage_history`, `charvak_credit_purchases`)
- Fix C - Razorpay webhook at `/webhook/razorpay` (abandoned-checkout safety net)
- Render Postgres password rotated (Charvak + VouchAI)
- Admin password rotated
- `RAZORPAY_WEBHOOK_SECRET` set on Render + local

**Performance:**
- `defer` on Razorpay, PayPal, Chart.js, Bootstrap JS
- Preconnect to jsdelivr + Google Fonts
- 1-year cache headers on `/static/*`
- Hero image 418 KB -> 71 KB
- Performance: 42 -> 52

**Accessibility:**
- aria-label additions (selects, social links, user menu, WhatsApp)
- Heading order fixed (`index.html`, `base.html`)
- Accessibility: 69 -> 90

**Content cleanups:**
- Legal pages updated to September 2026
- Full mojibake repair across all templates
- `exam-prep.html` BOM stripped

**SEO:**
- `/sitemap.xml` supports HEAD
- `/robots.txt` added with sitemap directive
- GA4 installed (`G-HVHHD3KJ9G`)

**Documentation:**
- `MASTER-REFERENCE.md` - technical reference
- `ARCHITECTURE.md` - system architecture
- `PAGES-INVENTORY.md` - template catalog

**Real-world verification:**
- Real Rs.99 payment completed on production
- Webhook fired, idempotent no-op (correct behavior)
- Credits granted + persisted + shown in UI

### Tier 1 - COMPLETE (10/10)

| # | Task | Status |
|---|---|---|
| 1 | End-to-end user journey test | Done |
| 2 | Enable email verification | Done |
| 3 | Test email templates | Done |
| 4 | Verify legal pages | Done |
| 5 | User journey test | Done |
| 6 | Real Rs.1 payment test | Done |
| 7 | Mobile responsiveness | Done |
| 8 | Performance audit | Done |
| 9 | SEO basics | Done |
| 10 | GA4 + Search Console | Done |

### Tier 2 - COMPLETE

Mojibake repair, password strength, rate limiting, backend health audit, admin polish, blog/case studies, testimonials, ongoing STATUS.md maintenance.

---

*Update this file after each session. Most recent session goes at the top.*