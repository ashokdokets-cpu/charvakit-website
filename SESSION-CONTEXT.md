# Session Context - Charvak

**HEAD:** 2cff7e2
**Live:** https://www.charvakit.com
**Updated:** 2026-10-20 (Sessions 63-64b closed - Track D Phase A + CAS Admin UI complete)
**Next up:** 2 five-min tasks (Amrita email + Render password), then Wave 3 decision

---

## Two 5-Min Tasks Pending

1. **Send Amrita reply to Prof. Raj** - 5 min, unlocks Track C (university pilot revenue line)
2. **Rotate Render Postgres password** - 5 min, closes last security flag

Both are dashboard work, not code. After these, entire P0 backlog is empty.

---

## Sessions 63 + 64 + 64b Closed

**Commits:** `bb0ecea` (S63), `ef5974f` (S64), `2cff7e2` (S64b)

### S63 - Track D Phase A 100%

- "I have a JD" toggle on /ai-assessment
- Paste JD → parse via /api/jd/parse → auto-fill role/industry/level
- /jd-assessment CTA carries ?role=&industry=&level= prefill params
- carApplyUrlPrefill() reads URL params on load

### S64 - CAS Admin UI backend

- cas_engine.list_api_keys() gets search + sort params
- /api/admin/cas-keys/list accepts ?search=&sort=
- NEW: /api/admin/cas-keys/list.csv (CSV export)

### S64b - CAS Admin UI frontend

- 6 gated patches (P1-P6), each with Jinja + node --check gate
- Toolbar: search input + sort dropdown + Export CSV button
- Bulk selection: checkboxes on pending rows + bulk approve
- Zero corruption. All gates passed.

### Process lesson

Earlier patch attempt corrupted admin-cas-keys.html by matching
`window.loadKeys = async function()` (doesn't exist - functions use
`async function loadKeys()` with `window.X = X` exports at bottom).

Fixed by: line-range anchors + unique full-line matches + node --check
gate + auto-revert on failure. See KNOWN-ISSUES.md.

---

## Platform State (all at 100%)

| Area | Status |
|---|---|
| Wave 1 (Identity, Viral, Habit, Batch) | ✅ |
| Wave 2 (Trust API, Employer Dashboard, CAS) | ✅ |
| Track D Phase A | ✅ |
| UI Modernization (7 phases) | ✅ |
| Session 64 CAS backend | ✅ |
| Session 64b CAS frontend | ✅ |
| GPT-4o-mini Phase 1-3b | ✅ |
| Open bugs | ✅ Zero |
| Broken features | ✅ Zero |

## Scheduled

- **Nov 3:** Phase 3c GPT-4o-mini env flip (5-min on Render dashboard)
  Set `OPENAI_MODEL=gpt-5.4-nano`, `OPENAI_MODEL_SMART=gpt-5.4-mini`

## Session 65 Candidates

A) **Wave 3 continued build** (recommended)
   - Interview Prep AI depth (~2 sessions) - highest differentiation
   - AI Tutor in courses (~2 sessions) - high perceived value
   - Career Assessment certifications (~1 session) - feeds readiness loop

B) **Close remaining flags first**
   - Amrita email + Render password + Phase 3c env flip = 15 min total
   - Then clean slate for Wave 3

C) **Pause for external signal**
   - Wait for Amrita response before more builds
   - Meanwhile polish any specific surface

---

**Recommended flow for Session 65:**
1. First 15 min: Amrita email + Render password + Phase 3c env flip
2. Then: Wave 3 first build (Interview Prep AI depth is best default)

---

# Session Context - Charvak

**HEAD:** a73aaf1
**Live:** https://www.charvakit.com
**Updated:** 2026-10-20 (Sessions 60-62 closed - UI Modernization COMPLETE)
**Next up:** Session 63 (Track D Phase A item C or Wave 3 planning)

---

## UI/UX Modernization Arc - COMPLETE (7 of 7 phases)

**Commits:** 18c9695, 54ffbd5, a73aaf1

### Coverage
- Teal brand hero: 9/9 assessment pages
- SVG animated gauge: 8/8 scored assessments
- Confetti on pass: 4/4 pass/fail assessments
- All pages: fade-in on load, button press, prefers-reduced-motion

### 7 phases summary
1. Foundation - S56 (a7eea0e)
2. Career Assessment - S57 (72ac132)
3. Readiness Certificate - S58 (8cae1a1)
4. Mock Drive - S59 (4e94ea9)
5. IELTS x4 - S60 (18c9695)
6. Versant + CBAT - S61 (54ffbd5)
7. Micro-interactions - S62 (a73aaf1)

---

## Remaining flags: 2 (both 5-min tasks)

1. Send Amrita reply to Prof. Raj - HIGHEST LEVERAGE
2. Rotate Render Postgres password - Render dashboard

---

## Session 63 candidates

A) Track D Phase A item C - wire JD parser into Career Assessment (~1 session)
B) Wave 3 planning - Track D Phase B or Track E or Track F
C) Phase 3c GPT-4o-mini env flip - Nov 3 target (5-min task)
D) Docs sync + retrospective for UI arc (~30 min)

---


**HEAD:** 2c0451c
**Live:** https://www.charvakit.com
**Updated:** 2026-10-19 (Sessions 55-56 closed - Track D Phase A 67%)
**Next up:** Session 57 (wire JD parser into Career Assessment)

---

## Sessions 55-56 CLOSED - Track D Phase A

**Commits:** `e8488f6` (parser), `50fa546` (MVP), `2c0451c` (what-next cards)

### Live URLs

- https://www.charvakit.com/jd-assessment (JD Scanner)
- https://www.charvakit.com/api/jd/parse (API, 5/min)
- https://www.charvakit.com/ai-assessment (with What-next cards now)

### Verified on prod

- 7/7 real JDs parsed (all client staffing roles)
- /jd-assessment 200
- Nav link "JD Scanner" live in teal CTA row
- What-next cards render on /ai-assessment result

### Track D Phase A status

- ✅ Item A (parser engine) — Session 55
- ✅ Item B (/jd-assessment MVP) — Session 56
- ⏳ Item C (wire into Career Assessment) — Session 57

### Session 57 plan

1. `templates/ai-assessment.html`: "I have a JD" toggle + textarea
2. Parse via `/api/jd/parse`, prefill dropdowns
3. `templates/jd-assessment.html`: CTA carry prefill URL params
4. `templates/ai-assessment.html`: read ?role=&industry=&level= on load

### Remaining flags (2 five-min tasks)

1. Rotate Render Postgres password
2. Send Amrita reply to Prof. Raj

---


**HEAD:** b84fb12
**Live:** https://www.charvakit.com
**Updated:** 2026-10-19 (Session 54 closed — Track D Phase A flagged)
**Next up:** Session 55 — JD parser engine (Track D Phase A, item A)

---

## Session 2026-10-19 (evening) — Track D Phase Split

Decision: don't wait for Amrita to start Track D. Split into two phases:

**Phase A (Build now, Sessions 55-57):**
- A: JD parser engine (`jd_parser_engine.py`) — NEXT SESSION
- B: `/jd-assessment` MVP (frontend only)
- C: Wire JD parser into Career Assessment

**Phase B (Blocked on Amrita Week 2):**
- D-H: Assessment designer, score normalizer, dashboard, outcomes, attribution

**Full plan:** TRACK-D-JD2P-PLAN.md "Session 2026-10-19 — Split into Buildable + Blocked Phases"

---

## Session 55 Plan (next)

**Goal:** `jd_parser_engine.py` — paste a JD → structured data

**Deliverable:** `parse_jd(jd_text) -> Dict` with 11 fields:
title, company, seniority, domain, skills_required, skills_nice_to_have,
experience_years_min, experience_years_max, responsibilities,
success_signals, assessment_relevance (topics, formats, difficulty)

**Test with:** NCS roles (AI Engineer, ML Engineer, Platform Engineer),
LENZE (Lead Firmware, App Engineer), Middle East (STP Mechanical),
plus 2-3 synthetic (accountant, designer, sales)

**Tech:** `openai_compat.build_payload()` (Phase 3b gave us this for free).
Cost ~$0.002 per parse. Rate limit 5/min per IP.

**No new tables.** Pure parsing function.

---

## Still Open (10 min total, do this week)

1. Send Amrita reply to Prof. Raj
2. Rotate Render Postgres password (dashboard)

---

# Session Context - Charvak

**HEAD:** 1902eb7
**Live:** https://www.charvakit.com
**Updated:** 2026-10-19 (Session 52 closed)
**Wave 2:** 100% COMPLETE
**Next up:** Session 53 (CAS admin UI, or Send Amrita reply, or pay down flags)

---

## Session 52 CLOSED (2026-10-19) - Certificate-as-a-Service

Completes Wave 2. Bulk verification API for institutional buyers.

**Commit:** 1902eb7

### Live URLs

- https://www.charvakit.com/employer/cas (landing page + request form)
- https://www.charvakit.com/employer/dashboard (unchanged, now links to CAS)
- https://www.charvakit.com/api/cas/verify-batch (POST, X-CAS-Key header)
- https://www.charvakit.com/api/cas/request-key (POST, self-serve)

### Verified on prod

- GET /employer/cas -> 200, renders hero + 4 pricing tiers + docs + form
- POST /api/cas/verify-batch (no key) -> 401 "X-CAS-Key header required"
- POST /api/cas/request-key -> 200, pending record created (verified locally)
- GET /employer/dashboard -> 200 (CTA link present at line 51 of template)

### Files touched

- cas_engine.py (new, ~16 KB, 7 public methods)
- migrations/20261019_cas_api_keys.sql (new)
- main.py (3 routes)
- templates/employer-cas.html (new, ~11 KB)
- templates/employer-dashboard.html (CTA added)

### Session 53 candidates

A) CAS admin UI (~1 session) - /admin/cas-keys page, approve button
B) CAS usage tracking (~1 session) - monthly quota reset cron
C) Employer Dashboard polish (~1 session) - empty state, sort, CSV
D) Pay down 4 long-carried flags (~45 min) - Render pwd, LMS, PayPal, IELTS CI
E) Send Amrita reply to Prof. Raj (5 min - draft exists in context)
F) GPT-4o-mini Phase 2 - due Oct 27

### Recommendation

Option E first (5 min, high leverage - unlocks Track C pilot), then
Option A (CAS admin UI) or Option D (flag cleanup) depending on time.

---

**HEAD:** 4c2ef76
**Live:** https://www.charvakit.com
**Updated:** 2026-10-19 (Session 51 closed)
**Next up:** Session 52 (Certificate-as-a-Service - completes Wave 2)

---

## Session 51 CLOSED (2026-10-19) - Employer Dashboard

Turns the Trust Score API into a browsable, filterable B2B product.
This is the first real B2B product surface on the platform.

**Commit:** 4c2ef76
**Wave 2:** 66% complete (Trust API done, Employer Dashboard done, CAS pending)

### Live URLs

- https://www.charvakit.com/employer/dashboard
- https://www.charvakit.com/employer/verify/hr-6201
- https://www.charvakit.com/api/passport/public/list

### Verified on prod

- Dashboard renders @hr-6201 (442, developing, 7 certs)
- Verify page shows component bars (43/50/30/50), integrity badge
  "Elevated signals" (correct), hash 5af408b282c9e447, raw JSON opens
- Nav link "For Employers" live on all pages

### Files touched

- passport_engine.py (list_public_passports method)
- main.py (3 routes)
- templates/base.html (nav link, line 344)
- templates/employer-dashboard.html (new, ~9.9 KB)
- templates/employer-verify.html (new, ~10 KB)

### Session 52 plan

Certificate-as-a-Service - completes Wave 2. See COMMITMENT.md
"Session 52 candidates" option A.

First read TRACK-C-B2B-PLAN.md (defines the university pilot this
product unblocks), then COMMITMENT.md Session 52 candidates.

---

**HEAD:** f2dbf00
**Live:** https://www.charvakit.com
**Updated:** 2026-10-16 (Session 44-A3 closed)
**Next up:** 44-A4 (Resume Roaster Teaser) or A5 (DoketsRB sync)

---

## Session 44-A3 CLOSED (2026-10-16) - State-PSC Free-Mock Funnels

The first SEO-driven revenue initiative shipped. Ten localized landing
pages, each with a free 15-question mock and a Rs 49 currency-aware
unlock for the full 100-question mock.

### What shipped

- `state_psc_funnel_engine.py` - free tier + HMAC tokens + paid unlock
- `charvak_state_psc_unlocks` table (self-healing DDL)
- `state_psc_full_mock` price key in `payment_engine.PUBLIC_PRICE_TABLE`
- `templates/free-mock.html` - single template, 10 exam pages
- `{% block head %}` added to `base.html` (infrastructure for SEO pages)
- Hero CTA on `/exam-prep` (all 10 exams linked)
- 10 new sitemap URLs (61 -> 71 total)
- Defensive bank fetch in `exam_prep_engine` (probes `embedding`,
  `reviewed` columns to survive dev/prod schema drift)

### The 10 exams

UPPSC PCS, MPSC Rajyaseva, RPSC RAS, WBCS, TNPSC Group 1, KPSC KAS,
MPPSC SSE, GPSC Class 1 & 2, APSC CCE, Kerala PSC KAS.

### Live URLs

- `https://www.charvakit.com/free-mock/uppsc_pcs`
- `https://www.charvakit.com/free-mock/mpsc_rajyaseva`
- ... (8 more)

### Verified E2E on prod

- 15 real questions served from the prod bank
- Deterministic scoring + per-topic breakdown
- `unlock_offer` returns Rs 49 / INR / razorpay for IN visitors
- Unknown exam -> 302 to `/exam-prep`
- Hero CTA + sitemap both render correctly

### Session 44 total (today)

- 44-A1: AI Slop Checker (Rs 199) - revenue line #3
- 44-A2: IELTS Band Guesser (Rs 99) - revenue line #4
- 44-B: Global Multi-Currency layer (all paid surfaces)
- 44-A3: State-PSC Free-Mock Funnels (10 landing pages)

### Revenue lines now live: 4

| # | Product | INR | Status |
|---|---|---|---|
| 1 | AI Tools one-off | Rs 99 | Live |
| 2 | IELTS Deep Report | Rs 99 | Live |
| 3 | AI Slop Report | Rs 199 | Live |
| 4 | IELTS Band Report | Rs 99 | Live |
| 5 | State-PSC Full Mock | Rs 49 | NEW |

### Next session candidates

- **A (recommended):** 44-A4 Resume Roaster Teaser (~4-5 hrs)
- B: 44-A5 DoketsRB bidirectional sync (infrastructure exists; needs
  DoketsRB-side wiring; 2 sessions)
- C: PayPal capture route for A1.6/A1.7/A3 unlocks (~30 min)
- D: Docs + backup polish (~30 min)
- E: Seed the local bank (~30 min) so future local tests don't need prod

### Still pending (long-carried)

- A1.1 Render Postgres password rotation (Session 19 flag)
- A1.2 PAYPAL_MODE=live explicit on Render (Session 9 flag)
- GPT-4o-mini Phase 2 (evaluate successor) - due Oct 27

---
# Session Context - Charvak

**HEAD:** f2dbf00
**Live:** https://www.charvakit.com
**Updated:** 2026-10-16 (Session 44-B closed)
**Next up:** 44-A3 (Localized Exam Funnels) or 44-A4 (Resume Roaster)

---

## Session 44-B CLOSED (2026-10-16) â€” Global Multi-Currency + A1/A2 revenue lines

Three batches shipped today, all live on prod. Revenue lines #3 and
#4 are now producing (currency-aware on both).

### Commits (all pushed to origin/main)

- cf9d772  feat(currency): global multi-currency layer
- 88f944f  fix(currency): dev override + A2 leftovers
- af1e61b  fix(currency): forward ?country= to price fetch
- d035e19  style: indent normalize
- 512a9b3  polish: clear PayPal loading message + scroll to button
- 6181bd0  fix(currency): accept country_code override in create-order

### What shipped

**44-A1 â€” AI Slop Checker** at `/slop-check`
- Free public code scanner, rate-limited 3/hour per real client IP
- Rs 199 PDF blueprint, Razorpay webhook delivery
- Reuses `premium_report_engine` + `pdf_engine.render_premium_report_pdf`
- Bug fixed in prod (commit 48298e1): webhook plan guard rejected
  orders missing `plan` key. Fixed by adding `plan: 'ai_slop_report'`.

**44-A2 â€” IELTS Band Guesser** at `/ielts-band-guess`
- Free 30-second speaking teaser
- Rs 99 full diagnostic report
- Reuses `ielts_engine.evaluate_speaking`
- Webhook-driven delivery

**44-B â€” Global Multi-Currency Layer**
- `payment_engine.resolve_public_price(key, country)` helper
- `GET /api/public/price/{key}` public endpoint
- A1 + A2 routes now currency-aware
- Both templates display local prices + route to correct gateway
- Both templates forward `?country=` dev override
- PayPal SDK lazy-loads (no more unconditional load on every page)
- Client-confirm routes for PayPal flows

### The global-product upgrade

Before: Charvak's paid surfaces were essentially India-only.
After: every paid surface uses one pattern:
  country -> tier -> price -> gateway -> response.

US sees $4.99, UK sees Â£3.99, IN sees Rs 199.

### Verified

- Pre-push hook: 14/14
- `git status --short` empty
- HEAD = origin/main = origin/HEAD = 6181bd0
- Prod smoke test: all 4 paid flows reachable
- Currency chain verified on local + prod

### Next session candidates

- **Option A (recommended):** 44-A3 â€” Localized Exam Funnels
  (10 state-PSC landing pages, 5 free questions + Rs 49 unlock,
  highest ceiling ~Rs 20-50K/month, ~6-8 hrs)
- Option B: 44-A4 â€” Resume Roaster Teaser (~4-5 hrs)
- Option C: A1.6 country-code latent bug cleanup (~5 min)
- Option D: A2.3 certificate i18n (Hindi/Telugu, ~2 hrs)

### Still pending (long-carried)

- A1.1 Render Postgres password rotation (since Session 19)
- A1.2 PAYPAL_MODE=live explicit on Render
- GPT-4o-mini Phase 2 (evaluate successor) â€” due Oct 27

---
## HIGH PRIORITY FLAG - GPT-4o-mini retirement (Jan 14, 2027)

OpenAI is retiring GPT-4o-mini on 14 January 2027.
34 files, 78 references. This is the AI engine for the whole platform.

**Read GPT-RETIREMENT-REMINDER.md before starting any session.**
Full plan in COMMITMENT.md, search: GPT-4o-mini retirement.

Timeline:
  Phase 1 (Centralize):  Oct 20, 2026
  Phase 2 (Evaluate):    Oct 27, 2026
  Phase 3 (Swap + test): Nov 3, 2026
  Latest start:          Dec 15, 2026
  DEADLINE:              Jan 14, 2027

First task before migration:
  Centralize model name in global_config.py as OPENAI_MODEL
  with env var override. Then swap is 1 line, not 34 files.

---

## Session 43-A3/A4 CLOSED (2026-10-16) - FYP features + personalized training

**HEAD at close:** 13dad7b

Two complete Track A feature batches shipped in one session.

### A3 batch - FYP feature set (4/4 complete)

| Feature | Status | Route | Credits |
|---|---|---|---|
| A3.1 Citation Helper | Done (verified today, shipped earlier) | /api/fyp/citations | 8 |
| A3.2 Milestone Roadmap | Done (verified today, shipped earlier) | /api/fyp/roadmap | 15 |
| A3.3 Plagiarism-Safe Rewriter | Done (NEW today) | /api/fyp/humanize | 15 |
| A3.4 Refine Section | Done (NEW today) | /api/fyp/refine | 5 per instruction |

Full FYP credit-bearing features: 9 (topics, proposal, documentation, expand-chapter, viva, citations, roadmap, humanize, refine).

### A4 batch - Personalized training recommendations

Server-side recommendation engine that matches a user's readiness cert skill gaps to catalog courses.

**New route:** `GET /api/training-engine/personalized?email=X` (auth-gated)

**New engine method:** `career_assessment_engine.get_personalized_recommendations(email)`

**Architecture:** Server-side mapping (TOPIC_TO_COURSE dict in Python) - single source of truth. Reusable across pages.

**Frontend:** `/training-engine` shows a "Recommended for you" panel with tiered "why" text based on the user's actual score.

### Also closed this session

- A1.12 - Blue badge candidate reassurance (52ef7ed + 05f7573)
- A2.1 - QR code on certificate PDF (5fd8aec)
- A1.10 - Readiness 404 friendly page (f8fedb7 + 84884ac)
- `multi_pattern` NameError fix (4b49771) - unblocked the Amrita demo
- GPT-4o-mini Phase 1 - centralized model name in global_config (8a579f7 + d091998)
- A2.5 - Confirmed N/A (no fabricated social proof exists)

### Next session options

1. **A2.3 i18n** - Hindi + Telugu certificate labels (2 hrs). High value if Amrita moves forward.
2. **Track C prep** - Pilot proposal + weekly report template, ready to fire when Prof. Raj replies.
3. **Docs sync** - Update KNOWN-ISSUES.md, ARCHITECTURE.md, TRACK-A-B-PLAN.md, STATUS.md.
4. **Amrita tracker** - Waiting on Prof. Raj. Follow-up email due Sunday if silent.

### Pending / Deferred

- A1.1 Render Postgres password rotation (5-min dashboard task)
- A2.3 Certificate i18n (deferred)
- A6 Benchmark data instrumentation (needs 200+ certs)
- A7 Certificate-as-a-Service (needs a buyer)
- Track B (CSR) - starts after A2 complete
- Track D (JD2P) - after Amrita pilot Week 2
- Track E (Behavioral readiness) - after Amrita signs

### Prod verification

Full /training-engine flow verified on prod with a real Data Engineer cert:
- 8 recommended courses matched
- Correct "Fills: [topic]" badges
- Tiered "why" text
- All 7 gap areas listed

---

## Session 43-A1.8 + A1.9 CLOSED (2026-10-13)

**Status:** Share instrumentation + placement-prep promotion shipped.
The full campus placement funnel is now attributable end to end.

### What shipped today (all 4 batches)

| Batch | What | Revenue impact |
|---|---|---|
| A1.6 | AI Tools one-off purchases (Rs 99) | First revenue line |
| A1.7 | IELTS Deep Report micro-paywall (Rs 99) | Second revenue line |
| A1.8 | WhatsApp/LinkedIn share instrumentation | Measurement only |
| A1.9 | Placement-prep promotion + attribution | Funnel improvement |

### Next session

- **A2** - Certificate round 3 (QR, watermark, i18n)
- **A2.5** - Real social proof feed
- **A3** - FYP features (Citation, Milestone, Plagiarism, Refine)
- Or cleanup: `rdOpenShare()` removal, PayPal E2E for A1.6

---

## Session 43-A1.7 CLOSED (2026-10-13) - IELTS Deep Report micro-paywall

**HEAD:** f2dbf00
**Status:** A1.7 shipped. Track A1.6 + A1.7 = first two revenue lines live.

### Read this next

1. If continuing Track A, the next batch is **A1.8** (WhatsApp loop
   instrumentation) or **A2** (Certificate round 3).
2. If doing cleanup, the A1.6 country-code bug is a 5-min patch.
3. Production smoke test after Render deploys:
   - `curl https://www.charvakit.com/api/ielts/deep-report/price`
   - Expect `Ã¢â€šÂ¹99` for IN, `$4.99` for US.

### What shipped this session

- `ielts_deep_report_engine.py` Ã¢â‚¬â€ new engine, 773 lines
- `static/js/ielts-deep-report.js` Ã¢â‚¬â€ new frontend, 421 lines
- 4 new routes under `/api/ielts/deep-report/`
- PDF renderer + email helper
- CTA slot + init on both IELTS templates

Full details in COMMITMENT.md.

---

## Session 43 CLOSED (2026-10-12) - Integrity fact panel + FYP MBA calibration

**HEAD at close:** c56e9c6 + pending docs commit
**Active roadmap:** see `TRACK-A-B-PLAN.md`

### Shipped

- Integrity fact-panel certificate redesign (facts, not verdicts)
- FYP discipline-aware topic generation (MBA/commerce support)
- 8 MBA courses generated and promoted to public catalog
- MBA role calibration verified for 5 roles

### Commits

- e6daf79 - feat(integrity): fact-based certificate panel + reweighted classifier
- 3fd8ad7 - feat(fyp): discipline-aware topic generation - MBA/commerce support
- c56e9c6 - docs: Track A (B2C) + Track B (CSR) master plan

### Files touched

- integrity_engine.py (compute_risk_level + get_public_summary)
- templates/readiness.html (badge + fact panel)
- final_year_project_engine.py (discipline-aware prompt)
- 8 MBA courses in charvak_courses (public catalog)

### Site health

- 182 page routes: all 200 or legit redirect
- 155 API routes: all reachable
- 0 broken buttons
- 0 HTTP 500s

### Still pending

- Batch A1-A5 (Track A) - see `TRACK-A-B-PLAN.md`
- Stage B1-B4 (Track B) - after A2

### Next session kickoff

Read `TRACK-A-B-PLAN.md`. Start with Batch A1 (small cleanup, ~45 min).

---
# Session Context - Charvak


## Session 42 continuation (2026-10-09) - Entry point + funnel for readiness

Post-Session-42 small additions. Two commits that matter more
than their line counts suggest: they turned the readiness check
from a standalone tool into a proper funnel.

### Commits

- 025c637  feat(readiness): dynamic CTA + sample certificate preview
- 30296ad  feat(readiness): next-step funnel on the certificate page

### What changed

**42-6 (readiness-check landing page)**
- CTA button is now dynamic: "Get my readiness score for <role>
  - free, 5 min" and updates live as the user picks a role
- Added a sample certificate preview below the CTA showing a
  78/100 example with benchmark comparison and cert ID

**42-7 (readiness certificate page)**
- New "Want to improve this score?" block below the share buttons.
  4 tiles linking to:
    1. /mock-drive
    2. /ai-courses
    3. /interview-prep
    4. /ai-internship
- Same pattern as the mock-result next-step block (Session 42-4)

### Why this matters

The readiness check was an endpoint. A student completed it,
got a score, and had nowhere to go. Now:

    readiness check  ->  score + certificate
                     ->  "Want to improve?"
                     ->  4 next-step tiles
                     ->  discover the rest of the platform

Combined with Session 42-2's GA4 funnel events, the readiness
check is now measurable AND connected to the rest of the
system. Every certificate page becomes a discovery moment.

### Strategic note

Across Sessions 42-2 through 42-7, the positioning shifted:
- Before: "we have 10 products, come use everything"
- After: "start with the free readiness check; then discover
  the rest based on your gaps"

The readiness check is the entry point. The certificate page
is the discovery surface. The rest of the platform is what
students find when they're ready.

## Session 42 CLOSED (2026-10-09) - Certificate polish, funnel wiring, AI course designer

The largest single session in the arc. Twelve commits across five
sub-sessions, all pushed to main. Four real bugs fixed, four new
features shipped, the complete student funnel now works end-to-end.

### Commits (chronological)

- b1a0668  feat(readiness): Session 42-0 - certificate polish for market launch
- 35dedf4  feat(readiness): Session 42-0g - quiet integrity badge + Your Score
- 79097b9  feat(readiness): Session 42-0i - final pre-launch CTA polish
- ba11798  chore(ui): align career assessment CTA with certificate CTA
- d1be352  refactor(session-42-1): move charvakFetch to base.html + fix seed env
- b4b494d  feat(versant): Session 42-1b - passed column on Versant sessions
- 717467e  chore(session-42-1d): .gitignore + PDF + "cr" -> "credits"
- c64c32f  feat(session-42-2): readiness-check SEO + GA4 funnel
- 83d0a81  feat(session-42-3): placement-prep landing page + pattern selection
- 1c929a5  feat(session-42-3): GA4 funnel + shareable mock drive result page
- 9eb635f  feat(session-42-4): next-step block on the mock-result page
- 9d2aced  feat(session-42-5): AI course designer on /ai-courses + ?next= auth fix

### What shipped

**42-0 - Certificate polish**
- Signatory block now reads "Bhavya M" + "Founder & CEO, Charvak IT Consulting"
- Wordmark header (text-rendered, swaps to image if a 700px+ logo-wordmark.png exists)
- Tagline replaced the duplicate eyebrow line
- Quiet integrity badge: only fires clean (green) or elevated (red "Under Review")
- Percentile cell replaced with "Your Score"
- CTA copy: "Want a deeper assessment?" + "25 credits"

**42-1 - Code cleanups (four carry-forward flags closed)**
- charvakFetch moved from cbat.html to base.html (now globally available)
- Seed scripts load .env.local first, refuse prod without CHARVAK_ALLOW_PROD=1
- Versant sessions gained a passed BOOLEAN column (default threshold 60)
- .gitignore duplicate whitelist lines removed (14 entries)
- PDF readiness certificate: "Percentile: N" -> "Your Score: N"
- Platform-wide: "N cr" -> "N credits" across 10 templates (38 instances)

**42-2 - Readiness SEO + GA4**
- Meta description + OG tags on readiness-check.html
- /readiness-check added to sitemap.xml (priority 0.9)
- GA4 events: readiness_start, readiness_complete, readiness_download_pdf,
  readiness_upgrade_click

**42-3 - Placement-prep landing + pattern selection fix**
- New public page: /placement-prep-2026 (18 companies in 3 sections)
- URL preselect: /mock-drive?company=tcs auto-selects TCS
- Login gate on companies.html (inline "Log in to take a mock drive"
  card with ?next= preservation)
- **Pattern-selection bug FIXED**: clicking any of a company's
  patterns previously generated the SAME questions. Now threads
  pattern_id through start_mock_drive -> multi_pattern lookup.
  Verified: TCS NQT / Digital / Innovator produce distinct drives.
- GA4 events: placement_prep_view, mock_company_click, mock_start, mock_complete

**42-4 - Next-step block on mock result**
- /mock-result/{session_id} public shareable page
- New API: GET /api/mock/result/{session_id}
- "What next?" section with 3 cards:
  1. Role Readiness Check (deep-linked with company->role mapping)
  2. AI Courses (existing catalog)
  3. Retake this drive
- GA4: mock_result_view, mock_result_share

**42-5 - AI Course Designer on /ai-courses**
- Designer card below the search: topic + level + weeks
- Calls /api/ai-course/generate-custom (50 credits, existing engine)
- Success card with Review course CTA
- "Your custom courses" section lists the user's previously designed
  courses at the top of the catalog
- New API: GET /api/ai-course/custom-list?email=X (auth-gated)
- GA4: ai_course_design_start / complete / error
- **?next= auth fix**: login.html and register.html both now honor
  ?next= with sanitization. Previously login.html read ?redirect=
  (legacy) and register.html ignored both - users always landed on
  "/" or "/welcome". The Register link now carries ?next= through.

### The four bugs fixed

1. Empty signature block on the readiness PDF certificate
2. Pattern-selection bug on /mock-drive - silently broken since
   launch. Every pattern of a company generated the same questions.
3. Login dead-end on /mock-drive (and any other ?next= redirect)
4. Register flow ignoring ?next= - new users lost their destination

### The complete student funnel (live)

    Placement-prep landing  ->  Pick company  ->  Take mock drive
        ->  Shareable result page  ->  Next-step block
        ->  Readiness check (pre-filled)  ->  Certificate
        ->  AI course designer (if topic not found)
        ->  Course enrollment

Two entry points (readiness-first, mock-drive-first), one connected
funnel, every step free until the student chooses otherwise.

### Verified in production

- https://www.charvakit.com/placement-prep-2026     200
- https://www.charvakit.com/ai-courses              200
- https://www.charvakit.com/readiness-check         200

### Follow-up flagged (low priority)

- The "Your custom courses" section on /ai-courses may briefly
  flicker on slow connections (display:none -> display:block).
  Move to a CSS class if it becomes an issue.
- The search-0-results "design a custom course for this term" hint
  from the original 42-5 plan was dropped (JS escaping complexity).
  Could be added in a follow-up if user testing shows demand.
- Render Postgres password rotation still pending (Session 19 flag).

### Session 43 candidates

- A: AuditBot Continuous (recurring revenue, COMPETITIVE-STRATEGY Gap 4)
- B: Certificate round 3 (QR in the PDF, watermark, multi-language)
- C: Personalized training views on /training-engine
- D: Review launch results - check-stats.ps1 + GA4 Realtime
- E: Docs + backup polish

**Recommendation: D first.** Read the numbers from the placement
and readiness launches before building anything else. Then A or C
based on what the data shows.


## Session 41 CLOSED (2026-10-08) - IELTS topical-relevance scoring

Closes the flag logged in Session 40c: IELTS writing and speaking
AI scoring did not enforce topical relevance, so off-topic
submissions could still receive a normal band score. Along the way,
found and fixed a pre-existing production bug that made the whole
relevance story silently ineffective.

**Commits:**
- b3fd1f6  feat(ielts): Session 41-1 - topical-relevance scoring for writing + speaking
- 0f17fe9  feat(ielts): Session 41-2 - off-topic banners + fix writing prompt param

**What shipped:**

Engine (ielts_engine.py):
- New `_topical_overlap()` helper (keyword-overlap, log-only).
- `evaluate_writing` prompt now instructs the AI to verify the
  essay addresses the task prompt; off-topic essays cap Task
  Achievement at 3.0 and return `topical_relevance=false` +
  `relevance_note`.
- `evaluate_speaking` prompt now:
    * tells the AI which parts were answered, and instructs it NOT
      to cap the band for missing parts (regression fix - partial
      submissions were scoring 0)
    * verifies the responses address the topic; off-topic caps all
      sub-bands at 3.0 and returns `topical_relevance=false`.
- Both methods log a warning when a naive keyword-overlap check
  disagrees with the AI's relevance judgment. Diagnostic signal,
  never overrides the score.

Frontend:
- ielts-writing.html + ielts-speaking.html: red "Off-topic
  response" banner above the yellow partial banner when
  `topical_relevance === false`. Uses the AI's
  `relevance_note` as the message.

Root-cause fix (main.py):
- The writing evaluate route read `data.get("prompt_text", "")`
  but the frontend sends `{prompt: ...}`. The prompt never reached
  the engine, so the AI could not judge topical relevance. Every
  IELTS writing evaluation since the feature shipped was scored
  without the prompt.
- Fixed to read `prompt` first, fall back to `prompt_text`.

Test harness (scripts/test_ielts_relevance.py, new):
- 6 canned cases: on-topic full, on-topic partial, off-topic full,
  off-topic short, speaking on-topic partial, speaking off-topic.
- Asserts on topical_relevance, partial, and band caps.
- ~\.03 per full run. Invoked manually after prompt changes.
- Tracked via .gitignore whitelist (`!scripts/test_ielts_relevance.py`).

**Verified E2E:**
- Harness: 14/14 checks pass.
- Browser (writing off-topic tea essay on road-safety prompt):
  red banner + yellow partial banner, Task Response 3.0,
  Overall Band 4.5, feedback explicitly notes the mismatch.
- Browser (writing on-topic technology essay): no banners, all
  bands 8.0, feedback praises the on-topic content.
- Browser (speaking off-topic): red banner with the AI's note.
- Browser (speaking on-topic partial): yellow partial banner only.
- Trust badge + integrity capture still work on both templates.

**Follow-up flagged:**
- The harness is a manual script, not wired to CI. If a future
  session wants a CI gate, `python scripts/test_ielts_relevance.py`
  exiting non-zero on failure is the hook point.
- Repo hygiene note: `.gitignore`'s `!scripts/*` whitelist has
  duplicates (`update_geoip.py`, `ai_verify_questions.py`, etc.
  appear twice). Cosmetic; not fixed.
- The writing-evaluate route now accepts both `prompt` and
  `prompt_text`. Once we confirm nothing else sends
  `prompt_text`, the fallback can be removed. Low priority.

**Session 42 candidates:**
- A: Certificate round 2 (QR, watermark, multi-language)
- B: AuditBot Continuous (recurring revenue)
- C: Personalized training views on /training-engine
- D: Docs + backup polish
- E: Wire scripts/test_ielts_relevance.py into a pre-deploy check


## Session 40c CLOSED (2026-10-08) - IELTS writing + speaking partial-credit handling

The final structural gap in the assessment trust pipeline. Writing and
speaking are the two AI-scored IELTS sub-tests; they needed the same
partial-credit treatment Versant received in 40a-9, calibrated for
AI-scored flows.

**Commit:** 668179e feat(ielts): Session 40c-1 - partial-credit handling
for writing + speaking

**What shipped (1 patch + 1 hotfix):**

Writing (evaluate_writing):
- Both the fallback and success returns gain
    "partial": word_count < min_words
- min_words is 150 for Task 1, 250 for Task 2
- Response also carries word_count + min_words
- Frontend: yellow banner
    "You wrote N words. Minimum for this task is M words.
     Task Response is capped at band 5.0."

Speaking (evaluate_speaking):
- Parts tracking: which of parts 1, 2, 3 have responses
- Partial = any expected part missing
- Response gains: partial, parts_covered, part_counts
- Frontend: yellow banner
    "You answered parts X. Part Y, Z not attempted.
     Score may not reflect full ability."

Routes (main.py):
- Writing complete_session details carry partial + word_count + min_words
- Speaking complete_session details carry partial + parts_covered + response_count

**Hotfix during the session:**
The v3 banner insertion for ielts-speaking.html landed ABOVE the fetch
that defines `j`. Fix (v4) moved the banner block to inside the try,
right after the `if (j.status !== 'success')` guard. Verified: the
banner uses `j.partial` and `j` is in scope at that point.

**Verified E2E:**
- Writing partial (100 words on Task 2): banner renders, DB stores
  partial=True, word_count=100, min_words=250
- Writing full (252 words): banner does not render, partial=False
- Speaking partial (parts 1+2 answered): banner renders listing the
  missing part, DB stores partial=True, parts_covered=[1,2]
- Trust badge + capture still work on both templates
- No console errors on either result screen

**Follow-up flagged (HIGH priority, its own session):**

The AI scoring for writing + speaking does not reliably enforce
topical relevance. Pasting off-topic text can still return a non-zero
band score; conversely, a partial-but-on-topic submission scored 0
with a feedback message about "missing responses." This is a prompt
engineering problem, not a partial-credit problem. Logged in
KNOWN-ISSUES.md as candidate for a dedicated session.

**Trust pipeline coverage: complete for all 4 IELTS sub-tests + 5
assessment types.**

| Assessment | Persistence | Capture | Badge | Admin | Partial |
|---|---|---|---|---|---|
| Career | yes | yes | yes | yes | n/a |
| Mock | yes | yes | yes | yes | n/a |
| CBAT | yes | yes | yes | yes | n/a |
| Versant | yes | yes | yes | yes | yes |
| IELTS Writing | yes | yes | yes | yes | yes (new) |
| IELTS Reading | yes | yes | yes | yes | yes |
| IELTS Listening | yes | yes | yes | yes | yes |
| IELTS Speaking | yes | yes | yes | yes | yes (new) |

The assessment trust pipeline arc that started in Session 38 is
now fully closed.

**Session 41 candidates:**
- A: AI scoring relevance fix for IELTS writing + speaking (own session)
- B: Certificate round 2 (QR, watermark, multi-language)
- C: AuditBot Continuous (recurring revenue)
- D: Personalized training views on /training-engine
- E: Docs + backup polish


## Session 40b CLOSED (2026-10-08) - IELTS persistence + integrity roll-out

Session 40a extended the integrity pipeline to Versant. Session 40b
does the same for IELTS (4 sub-tests: writing, reading, listening,
speaking), and fixes a cluster of pre-existing IELTS bugs along the
way.

**Commits:**
- 150015f  feat(ielts): Session 40b-1 - create IELTS session persistence table
- ab499a1  feat(ielts): Session 40b-2a - engine session lifecycle methods
- 6fcd3d7  feat(ielts): Session 40b-2b - start routes create sessions + fix missing tables
- deacda8  feat(ielts): Session 40b-2c/3a-d - complete routes close sessions + frontends propagate session_id
- c85d467  docs(session-40b): partial note - IELTS backend lifecycle done
- 35cc66f  feat(integrity): Session 40b-4 + 40b-4b - IELTS prefixes in ownership helper
- 9df36c7  feat(integrity): Session 40b-5 - admin list + detail endpoints show IELTS
- d352bf9  feat(integrity): Session 40b-6/6b/6c - wire capture + trust badge into IELTS
- c65b696  feat(ielts): Session 40b-7 - partial-credit tracking for reading + listening

**What shipped:**

Backend:
- New table `charvak_ielts_sessions` with 10 columns, one row per
  sub-test attempt
- Migration `20261008_ielts_sessions.sql` + self-healing DDL in
  `ielts_engine._ensure_tables()`
- `create_session(email, test_type, content_ref)` and
  `complete_session(session_id, band_score, details)` methods
- 4 start routes create sessions and return session_id
- 4 complete routes close sessions on evaluate/score
- 4 templates propagate session_id in the evaluate payload

Integrity layer:
- `_integrity_lookup_owner` gains 4 IELTS prefixes (IELTS-W/R/L/S)
- **Two-segment fallback** for multi-dash prefixes
  (single-segment lookup first, then two-segment)
- Admin list endpoint JOINs `charvak_ielts_sessions` and COALESCEs
  role = 'IELTS {test_type}', format = 'ielts'
- Admin detail endpoint gains the IELTS branch

Frontend:
- All 4 templates load `integrity-capture.js` + call
  `CharvakIntegrity.init()` with a getter for the session ID
- Badge slot + `CharvakIntegrity.renderBadge()` on each scorecard
- Yellow partial-submission banner (reading + listening)

Partial-credit handling:
- `evaluate_reading` + `evaluate_listening` count answered (sel >= 0)
- Response includes `answered_count` + `partial` flag
- Persisted in `details_json`
- Frontend shows banner when partial=True

**Pre-existing bugs fixed along the way (7):**

1. **4 missing tables** ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â `charvak_ielts_reading_passages`,
   `charvak_ielts_listening_sections`, `charvak_ielts_reading_attempts`,
   `charvak_ielts_listening_attempts`. Engine code referenced them,
   no migration ever created them. Silent failure at runtime.

2. **`last_used_at` column missing** from `reading_passages` and
   `listening_sections`. Engine's UPDATE queries referenced it.

3. **Migration file `#` comment syntax** ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â `20261008_ielts_reading_listening.sql`
   had invalid `#` comments; needs `--`.

4. **Seed scripts target prod** ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â `scripts/seed_ielts_reading.py` and
   `seed_ielts_listening.py` call `load_dotenv()` (which loads `.env` =
   prod). Local seeding required passing `DATABASE_URL` explicitly.

5. **3 missing commas after `session_id`** in template payloads.
   The 40b-2c patcher inserted `session_id: XX.sessionId` without
   a trailing comma in writing/reading/listening. Speaking was fine.

6. **1 missing comma before `session_id`** in writing template.
   The `prompt: IW.promptText` line needed a comma after the insert.

7. **`$host` and `$pid` PowerShell variable collisions** in test
   scripts. Both are read-only built-in variables.

**Verified E2E:**

- 4 sessions created with correct prefixes
  (IELTS-W/R/L/S + 12 hex chars)
- Reading session completed (Honey Bees passage, band 3.5, 2/10)
- Partial submission (6 of 10): banner renders, DB shows
  partial=True, answered=6, band=4.5
- Full submission (10 of 10): no banner, DB shows partial=False
- Trust badge renders on all 4 result screens
- Admin list shows format=ielts (1+ rows)
- Regression: CBAT/VERSANT/MOCK/CAR still resolve correctly

**Patterns established:**

- **Two-segment prefix fallback** in `_integrity_lookup_owner` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â
  single-segment lookup first, then two-segment when the map misses
  and the ID has 2+ segments. Preserves CAR/CBAT/VERSANT behavior.
- **Comma preservation rule** for JS object literal patches ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â when
  inserting a field, verify both the preceding and following fields
  end with commas as appropriate.
- **Deterministic partial-credit tracking** ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â count answered vs total,
  flag partial, render banner. Simpler than Versant's AI-calibrated
  approach because IELTS scoring is objective.

**Session 40c candidates:**
- A (recommended): Roll Layer A + badge to IELTS writing + speaking
  (partial-credit handling; the writing/speaking scores are AI-generated,
  so partial calibration is closer to Versant's pattern)
- B: Certificate round 2 (QR, watermark, multi-language)
- C: AuditBot Continuous (recurring revenue)
- D: Personalized training views on /training-engine
- E: Docs + backup polish

**Follow-ups flagged:**
- `charvakFetch` in `base.html` (still pending from Session 39)
- Seed scripts env routing cleanup (loading `.env` instead of `.env.local`)
- Versant `passed` boolean column (from Session 40a)
- Render Postgres password rotation still pending (Session 19)

**Trust pipeline coverage: complete for all 5 assessment types:**

| Assessment | Persistence | Capture | Badge | Admin | Partial |
|---|---|---|---|---|---|
| Career | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | n/a |
| Mock | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | n/a |
| CBAT | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | n/a |
| Versant | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ |
| IELTS | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ (reading/listening) |


## Session 40a CLOSED (2026-10-07) - Versant persistence + integrity roll-out

Session 39 shipped the integrity roll-out for Mock Drives and CBAT.
Session 40a extends the same pipeline to Versant - and along the way
fixed a Tier 3 persistence gap that had been silently breaking
Versant since it was refactored.

**Commits:**
- 150728a  feat(versant): Session 40a-1 - create session persistence tables
- c0bb9fc  feat(integrity): Session 40a-3 - add VERSANT prefix to ownership helper
- 628cf98  feat(integrity): Session 40a-4 - list endpoint joins versant sessions
- 7a9be9f  feat(integrity): Session 40a-5 - detail endpoint prefix routing for VERSANT
- cbd1712  feat(integrity): Session 40a-6 - wire capture into versant.html
- 29f078b  feat(integrity): Session 40a-7 - Trust badge on the Versant scorecard
- e25598e  feat(versant): Session 40a-9 - graceful partial-credit handling

**What was broken before this session:**

Versant has been dead-on-arrival. `cbt_versant.py` was refactored at
some point to persist to Postgres, but:
- No migration created the tables
- No `_ensure_tables()` self-healed them
- Every `create_session()` call hit the try/except and returned
  "could not create session"
- 0 rows in `charvak_versant_sessions` locally
- 0 Versant rows in `charvak_assessment_results`

The bug was invisible because the try/except swallowed the error and
logged it silently.

**What shipped:**

Backend:
- migrations/20261007_versant_sessions.sql - creates
  `charvak_versant_sessions` + `charvak_versant_answers`
- cbt_versant.py._ensure_tables() - self-healing DDL called from
  __init__. Tables now create on first import even without running
  the migration.
- _integrity_lookup_owner's table_map gains a VERSANT entry routing
  to charvak_versant_sessions
- /api/admin/integrity-events list query LEFT JOINs versant +
  COALESCEs role = 'English Assessment', format = 'versant'
- Detail endpoint prefix switch gains a VERSANT branch

Graceful partial-credit handling:
- complete_session computes partial = answered_count < 48
- _score_versant prompt tells the AI how many were answered and
  asks for a "confidence" JSON field
- Response includes partial / answered_count / total_count
- results_system.record_assessment_result persists the metadata
- Frontend renders a yellow banner: "Partial submission - You
  answered N of 48 questions. The score below is not comparable
  to a full-test result."

Frontend:
- versant.html loads integrity-capture.js and calls
  CharvakIntegrity.init() with a getter for window.VS.sessionId
- Trust badge renders on the scorecard via the shared
  CharvakIntegrity.renderBadge()
- Partial banner renders above the score when partial=true

**Verified E2E:**
- Versant session starts (was broken before)
- 10 events captured in a live session
- Admin list shows VERSANT row with "English Assessment Ãƒâ€šÃ‚Â· versant"
- Detail page metadata card fully populated
- Scorecard badge renders green/blue/yellow/red depending on state
- Partial submission (10/48 and 28/48): yellow banner renders,
  DB records partial=True + answered_count + confidence='reduced'
- Full submission: no banner, confidence='high'

**Patterns established:**
- Versant joins the ownership prefix map (5 entries now:
  CAR/MK/MOCK/CBAT/VERSANT)
- The badge renderer works on 4 assessment types with the same
  10-line call pattern
- Graceful partial-credit handling is now the model for any future
  scoring integration: no hard block, but a clear label + AI
  calibration + persisted metadata

**Patcher discipline lesson:**
- When replacing a Python statement whose closing paren is on its
  own line, the paren MUST be part of the replacement boundary.
  The 40a-9 v1 patcher stopped at the last quoted string and left
  the original `)` orphaned. v2 added an explicit assertion on the
  closing paren line + a post-write AST parse check with automatic
  restore-on-failure. Both gates are now standard for multi-line
  Python replacements.

**Session 40b candidates:**
- A (recommended): Roll integrity pipeline to IELTS (Session 40b).
  Same pattern as Versant. IELTS has 4 sub-tests (writing/reading/
  listening/speaking), needs one `charvak_ielts_sessions` table
  with a `test_type` column.
- B: Certificate round 2 (QR, watermark, multi-language)
- C: AuditBot Continuous (recurring revenue)
- D: Personalized training views on /training-engine
- E: Docs + backup polish

**Follow-ups flagged:**
- `charvak_versant_sessions` has no `passed` boolean column.
  Admin detail shows "ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â" for Passed. Add a passed column +
  populate it in complete_session (score >= threshold). Small.
- `charvakFetch` helper belongs in base.html - 3+ templates
  duplicate the pattern (still on the list from Session 39).
- IELTS is now the only assessment without the trust pipeline.

**Reminder:** Render Postgres password rotation still pending
(since Session 19).



## Session 39 CLOSED (2026-10-07) - Integrity roll-out to Mock + CBAT

Session 38 shipped the integrity admin UI + public trust badge for
Career Assessments. Session 39 extends the same engine, admin UI,
and badge to Mock Drives and CBAT.

**Commits:**
- 8e7607a  feat(integrity): Session 39-1 - generalize ownership check
- 2504a26  refactor(integrity): Session 39-2 + 39-3 - extract capture to shared helper
- 48905ca  feat(integrity): Session 39-4 - wire capture into Mock Drives
- 251e0d1  feat(integrity): Session 39-5/5b/5c - wire CBAT + fix two blocking bugs
- f70c41e  feat(integrity): Session 39-6 - public integrity endpoint + Mock result badge
- 90a6290  refactor(integrity): Session 39-7a/7b - shared badge renderer
- 9cae1ee  feat(integrity): Session 39-7c - CBAT result badge
- f6f9401  feat(integrity): Session 39-8a - list endpoint joins mock + cbat tables
- 5ed18f4  feat(integrity): Session 39-8b - detail endpoint prefix-based metadata

**What shipped:**

Backend:
- _integrity_lookup_owner() helper in main.py: routes assessment_id
  prefixes to the correct table (CAR/MK/MOCK/CBAT)
- /api/integrity/public/{assessment_id} - new public endpoint that
  returns risk_level + verified + message for any assessment prefix
- /api/admin/integrity-events list endpoint: LEFT JOINs career + mock
  + cbat tables, COALESCEs role/format so MK/CBAT rows show real values
- /api/admin/career-assessment/{aid}/integrity detail endpoint:
  prefix-based metadata lookup (was hardcoded to career table)

Frontend:
- static/js/integrity-capture.js: extracted the 250-line capture IIFE
  into a shared helper. CharvakIntegrity.init({ getAssessmentId })
- CharvakIntegrity.renderBadge({ slotId, assessmentId }) - shared
  trust badge renderer with self-injecting CSS
- ai-assessment.html, companies.html, cbat.html all now call the
  shared helper (10-15 lines each instead of 250)
- Trust badge renders on Mock Drives result + CBAT result screens

Two pre-existing bugs fixed along the way:
- CBAT page route was never registered in main.py (Session M-2
  shipped the engine + template, forgot the route)
- cbat.html called window.charvakFetch() at 3 sites but the
  function was never defined

**Verified E2E:**
- 31 assessments in /admin/integrity-events, all showing real
  Role Ãƒâ€šÃ‚Â· Format (Capgemini Ãƒâ€šÃ‚Â· mock_drive, analogies Ãƒâ€šÃ‚Â· cbat,
  Data Analyst Ãƒâ€šÃ‚Â· sql)
- Mock + CBAT detail pages: metadata card fully populated
- Public /api/integrity/public/MOCK-xxx returns the correct summary
- Career Assessment flow unchanged - full regression pass
- /readiness/{id} public badge still works

**Patterns established:**
- ID prefix routing (_integrity_lookup_owner) - any future assessment
  type plugs in with one entry in the prefix map
- Shared renderBadge - any future assessment result page renders the
  badge in ~10 lines
- Patcher discipline: preview-then-assert-then-write. Three asserts
  fire before any file write. Two gate failures saved main.py from
  corruption during 39-8b.

**Session 40 candidates:**
- A (recommended): Roll Layer A + badge to Versant + IELTS
  (Tier 2 - needs design decision on where session_id comes from)
- B: Certificate round 2 (QR, watermark, multi-language)
- C: AuditBot Continuous (recurring revenue)
- D: Personalized training views on /training-engine
- E: Docs + backup polish

**Follow-ups flagged:**
- Systemic charvakFetch helper belongs in base.html - 3+ templates
  duplicate the pattern now. One-line addition to base saves every
  future template.
- Two CAR- rows still show "ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Ãƒâ€šÃ‚Â· ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â" (older assessments from before
  Session 10 added role metadata). Cosmetic, not worth chasing.

**Reminder:** Render Postgres password rotation still pending
(since Session 19).



## Session 38 CLOSED (2026-10-07) - Integrity admin UI + public Trust Score badge

Session 27 recorded integrity signals; Session 38 turns them into
visible artifacts. Employers can now see a candidate's trust signal
on the certificate they receive, and admins can review the raw events.

**Commit:** 33cb2f6 feat(integrity): Session 38 - admin UI + public Trust Score badge

**What shipped:**

Admin UI (new):
- `/admin/integrity-events` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â list page. Summary strip, risk filters,
  email/ID search. Sorted by risk (elevated first), then by event count.
- `/admin/integrity-events/{assessment_id}` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â detail page. Assessment
  metadata card, risk badge, per-type counts, chronological event
  timeline with per-type filter pills.

Backend (main.py):
- `GET /api/admin/integrity-events` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â new list endpoint (admin-gated).
  Aggregates events per assessment, joins to `charvak_career_assessments`
  for role/industry/level/format, computes risk level per row.
- `GET /api/admin/career-assessment/{aid}/integrity` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â enriched with
  parent assessment metadata (email, role, industry, level, format,
  size, score, passed, status, started_at, completed_at, num_questions).
- `GET /api/readiness/{certificate_id}/integrity` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â NEW public endpoint.
  Looks up the source assessment via `charvak_readiness_certificates`,
  returns the public-safe summary. No raw events, no PII.

Engine (integrity_engine.py):
- `get_public_summary(assessment_id)` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â public-safe wrapper around
  `get_summary()`. Returns {status, risk_level, verified, total_events,
  message}. Strips per-type counts, timestamps, and metadata.

Frontend (templates/readiness.html):
- Trust Score badge renders below the verdict pill on every certificate.
- Four states: clean (green shield), minor (blue info), moderate
  (orange warning), elevated (red alert).
- "What does this mean?" collapse explains the signals: what we
  capture, what it means, what it doesn't mean.
- Silent-fail: a dead backend never breaks the certificate.

**Verified E2E:**
- List page: 21 assessments, 7 elevated / 9 moderate / 5 minor / 0 clean
  (before the elevated test)
- Detail page for CAR-03ED7FFB32: 87 events (65 tab_switch, 14 focus_out,
  8 paste), all rendering with correct metadata summaries
- Public badge: clean state on RDC-7D1C13B5B5A4 (green shield), elevated
  state after swapping to CAR-03ED7FFB32 (red alert), reverted after test
- Both risk badges render the correct icon, color, and message

**Session 39 candidates:**
- A (recommended): Roll Layer A + Trust Score badge to Versant, Mock
  Drives, CBAT, IELTS. Engine + route + badge pattern all exist.
- B: Certificate round 2 (QR, watermark, multi-language)
- C: AuditBot Continuous (recurring revenue)
- D: Personalized training views on /training-engine
- E: Docs + backup polish

**Reminder:** Render Postgres password rotation still pending (since
Session 19).




## Session 37 CLOSED (2026-10-07) - Wire the Career Engine trio to real data

Three surfaces looked like products but two were hardcoded mockups.
This session wired them to the real backends from Sessions 30-36.

**Commit:** <hash> feat(career): Session 37 - wire the Career Engine trio to real data

**What shipped:**

Job Board (templates/job-board.html, full rewrite):
- Was: 6 hardcoded jobs, prompt()-based Apply, localStorage state
- Now: fetches /api/jobs/unified, renders 8 real items
  (7 staffing + 1 gig), client-side filters, 'View & Apply'
  navigates to the real detail page
- Honest DoketsRB integration banner

Training Engine (templates/training-engine.html, full rewrite):
- Was: 3 fake courses, fake instructors, Coursera/Udemy links
- Now: fetches /api/ai-course/catalog, renders the 31 real courses
  with filters, sort, search; 'View Course' navigates to the real
  detail page; AI-designed course callout to /ai-assessment
- Removed external learning platform links

Career Engine narrative (templates/career-engine.html, rewrite):
- Was: 'Model 19' badge, stale external course links, no CTA
- Now: 'Career Engine Overview', 'Your Career Journey - 7 Steps',
  primary CTA to /career-center

Navigation (templates/base.html):
- Added 'My Career Center' to Services dropdown
- Added 'My Career Center' to footer

Cross-links (all three surfaces + career-v2):
- /career-center panel: 'See the 7-step journey' link
- /job-board: 'My Career Center' + 'Explore Training'
- /training-engine: 'My Career Center' + 'See the 7-Step Journey'

Fixed: nested anchor in career-v2.html panel header (37-3b).

**Verified E2E:**
- 8 real items on /job-board
- 31 real courses on /training-engine
- Filters, searches, and cross-links work
- /career-engine and /career-center now distinguishable
- Nav dropdown + footer both link to /career-center

**Flagged (Session 38+):**
- DoketsRB bidirectional sync (COMMITMENT.md line 3824)
- Job posting as first-class feature
- Personalized training views (needs readiness cert data)

**Session 38 candidates:**
- A (recommended): Admin UI for integrity events (Session 27 data)
- B: Personalized training views (Job Board flag -> Training Engine)
- C: Certificate round 2 (QR, watermark, multi-language)
- D: AuditBot Continuous (recurring revenue)

**Reminder:** Render Postgres password rotation still pending.


## Session 36 CLOSED (2026-10-07) - Two-tier AI course unlock

The AI-designed course is now a real freemium product. Design is 50
credits, Weeks 1-2 are free to consume, and 150 credits unlock the
full course plus the certificate and AI tutor.

Total committed: 200 credits. Total curious: 50 credits.

**Commit:** 3ea3320 feat(courses): Session 36 - two-tier AI course unlock

**What shipped:**

Backend (ai_courses_payments.py):
- check_access now gates Weeks 3+ of custom courses on paid_unlock.
- The custom-course check runs BEFORE the installment lookup so stray
  installment rows from the enrollment path don't fire the EMI branch.
- paid_unlock=TRUE custom courses bypass the check (full access).

Backend (ai_courses.py):
- charvak_enrollments.paid_unlock BOOLEAN DEFAULT FALSE (self-healing DDL).
- Self-limiting grandfather: NULL rows flip to TRUE once.
- New: check_unlock_status(enrollment_id, email)
- New: unlock_full_course(enrollment_id, email)
- complete_course gates certificate issuance on paid_unlock.
- complete_week gates auto-issue and returns certificate_locked.

Backend (main.py):
- New: POST /api/ai-course/unlock-full (charges 150 credits, idempotent).
- Defense-in-depth: /lesson/ and /content/ also call check_course_access.

Backend (ai_credit_engine.py):
- New credit key: ai_course_full_unlock = 150.

Frontend (my-course.html):
- New #unlockCard for credit-based unlock (distinct from EMI card).
- showPaywall() branches on unlock_type === 'full_course'.
- unlockFullCourse() with confirmation dialog + 401/402/403 handling.
- completeWeek() checks certificate_locked and routes to unlock card.

Frontend (course-detail.html):
- Custom-course panel shows 'Start free (Weeks 1-2)' + 'Unlock for 150 credits'.
- unlockFullFromDetail() ensures enrollment then charges.

Frontend (ai-assessment.html):
- Custom-course intro copy explains the two-tier model.
- Design confirmation card adds a 'What comes next' bullet list.

**Verified E2E on prod:**
- 150 credits deducted (logged in usage history).
- Custom course weeks 1-2 allowed, weeks 3-6 blocked.
- POST /api/ai-course/unlock-full flips paid_unlock and returns success.
- Certificate gate returns 'locked' for unpaid custom courses.
- After unlock, certificate issues and public verify URL works
  (CERT-F3C47CEFE7A7, CERT-BE0F380DC299 both verified).
- Catalog courses unaffected at every layer.
- All 5 existing test enrollments grandfathered (paid_unlock = TRUE).

**Also committed in this session:**
- Session 35's DEV_SKIP_EMAIL_VERIFICATION flag (email_verification.py).

**Session 37 candidates:**
- A (recommended): Admin UI for integrity events (Session 27 data) -
  turn the trust signal into a visible employer-facing artifact.
- B: Roll unified panel to /my-results and /profile (Session 30 pattern).
- C: Certificate round 2 (QR, watermark, multi-language).
- D: AuditBot Continuous (recurring revenue).

**Reminder:** Render Postgres password rotation still pending.


## Session 34 CLOSED (2026-10-07) - AI course designer

Closes the last dead-end in the Local-to-Global journey. When a
candidate's learning path has a weak topic with no catalog match,
the AI designs a full course on demand.

**Commit:** ce34cfe feat(career): Session 34 - AI course designer

**What shipped:**

Backend (main.py):
- /api/ai-course/generate-custom: stopped auto-enrolling. Returns
  course info so the frontend can present a review step.
- /api/ai-course/create-order: free (Rs 0) courses bypass the
  payment gateway entirely. Returns {status: 'exists',
  enrollment_id, free: true} which the frontend already handles.
- Both idempotent paths updated to match.

Frontend (ai-assessment.html):
- generateCustomCourse(topic, level, roleHint, candStatus):
  - Adaptive weeks: weak -> 6, mixed -> 4, strong -> 3
  - Signature and call site updated to pass candStatus
  - Call-site label: 'Generate - 50 cr' -> 'Design this course - 50 cr'
- Success card: 'Start Learning' -> 'Review course ->' pointing at
  /course/{name} so the candidate sees the curriculum before enrolling
- Fixed JS string-escaping bug from Session 34 v1 (missing argument
  connector between the 3rd and 4th function args)

Frontend (course-detail.html):
- Login hint is now dynamic. Logged in -> shows the account email.
  Logged out -> shows the original 'Login required' warning.

**Verified:**
- Custom course generated: 'Fundamentals Syntax (Mid Intensive)',
  6 weeks (weak -> adaptive), Rs 0
- Custom course generated: 'Modeling ML (Mid Intensive)',
  4 weeks (mixed), Rs 0
- POST /api/ai-course/create-order returns
  {status:'exists', enrollment_id:'ENROLL-6703420F', free:true}
  for a Rs 0 course - no Razorpay gateway involved
- Review course -> lands on course detail page
- Enroll Now -> free enrollment, redirects to /my-course/{id}

**Session 35 candidates (recommended: cleanup + polish):**
- A (recommended): Necessary fixes + small polish
  * Rotate Render Postgres password (pending since Session 19)
  * Add DEV_SKIP_EMAIL_VERIFICATION=1 flag for local dev
  * Fix 'Pay in EMIs' display on Rs 0 course pages
  * Roll unified panel to /my-results
  * Top-3 jobs preview on /career-center panel
- B: Admin UI for integrity events (Session 27 output) ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â strategic
- C: Certificate round 2 (QR, watermark, multi-language)
- D: AuditBot Continuous (recurring revenue)

**Reminder:** Render Postgres password rotation still pending.


## Session 33 CLOSED (2026-10-07) - Assess -> Upskill loop

Fourth and final step of the unification arc. Closes the loop from
assessment result to course enrollment.

**Commit:** <hash from push>

**What shipped:**

Engine (career_assessment_engine.py):
- _ai_generate_learning_path prompt now requests 'fills_topic' per
  recommended course - the weak topic that course addresses
- Rule added: fills_topic MUST be copied verbatim from weak topics
- Defensive normalize: fills_topic defaults to '' if AI omits

Frontend (ai-assessment.html):
- renderLearningPath() course card now shows:
    Course name
    [Fills: <weak topic>] badge
    Reason text
    [Start course ->] button (deep-links to /course/{name})

**Verified:**
- New learning paths (2026-10-07+) populate fills_topic correctly
- Old cached paths (2026-10-06) keep fills_topic=None (expected)
- Browser renders badge + CTA
- Clicking Start course -> lands on working course detail page
- Price API + EMI schedule render (3 installments, ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¹1,333 each)

**Local-only fix (not a code change):**
- charvak_course_levels migrations were missing from local dev DB
- Applied: 20260916_course_levels.sql + seed + 20260920_desc_update
- Result: 75 rows (25 courses x 3 levels), all tiers priced
- Prod was unaffected - the route has always worked

**Unification arc: 4 of 4 COMPLETE**
- 30: unified candidate profile (read) - SHIPPED
- 31: unified jobs feed (read) - SHIPPED
- 32: unified candidate signup (write) - SHIPPED
- 33: Assess -> Upskill loop - SHIPPED

**Session 34 candidates:**
- A (recommended): AI course designer - auto-generate courses for
  topics with no catalog match. Reuses Session 18's custom-course
  generator. Zero dead ends.
- B: Render Postgres password rotation (still pending)
- C: Admin UI for integrity events (Session 27 output)
- D: Certificate round 2 (QR, watermark, multi-language)

**Reminder:** Render Postgres password rotation still pending.


## Session 32 CLOSED (2026-10-07) - Unified candidate signup (Phase 3)

Third step of the unification arc. One signup entry point, one write
path, one profile editor. Closes the "write side" of the arc.

**Commit:** ffa00dc feat(candidate): Session 32 - unified candidate signup (Phase 3)

**What shipped:**

Engine (candidates_engine.py):
- ALLOWED_FIELDS expanded from 23 to 37 fields
- _ensure_columns() self-healing DDL for signup_source column
- signup_source validation against a whitelist of source tags
- get_me() now reads all 39 columns (was 25) - read/write symmetry
  restored after the field expansion

Engine (candidate_engine.py):
- register_candidate() delegates to candidates_engine.upsert()
- Adds signup_source='pool-register' (forgery-proof)
- Repeat registrations now update rather than error

Routes (main.py):
- /candidate/signup -> marketing gate + redirect to /profile when authed
- /candidate-signup -> 302 -> /candidate/signup (legacy)
- /developer-signup -> 302 -> /candidate/signup (legacy)

Templates:
- candidate-signup.html: 252-line form replaced with 60-line gate
- profile.html: 5 new fields (preferred_roles, visa_status,
  portfolio_url, github_url, linkedin_url) + prefill on load
- base.html: nav dropdown merged (2 signup items -> 1)
- about.html, how-it-works.html, reverse-staffing.html, register.html:
  links repointed, register.html CTA reworded

**Verified:**
- signup_source column self-heals, accepts valid tags, drops invalid
- get_me round-trips all fields including the 14 new ones
- Legacy /api/candidate/register lands through the unified path
- /candidate/signup redirects authenticated users to /profile
- /profile writes all 5 new fields and prefills them on reload

**Prod verified:**
- /candidate/signup -> 200
- /candidate-signup -> 302 -> /candidate/signup
- /developer-signup -> 302 -> /candidate/signup
- /profile -> 200

**Session 33 candidates:**
- A (recommended): Assess -> Upskill loop. When a candidate
  completes a Career Assessment with weak topics, the result page
  links directly to course enrollment. Read-side only.
- B: Roll the unified panel (Session 30) to /my-results and /profile
- C: Add top-3 jobs preview to the /career-center panel
- D: Docs + backup polish session

**Unification arc:**
- 30: unified candidate profile (read) -- SHIPPED
- 31: unified jobs feed (read) -- SHIPPED
- 32: unified candidate signup (write) -- SHIPPED
- 33: Assess -> Upskill loop -- NEXT

**Reminder:** Render Postgres password rotation still pending.


## Session 31 CLOSED (2026-10-06) - Unified jobs feed (Phase 2)

Second step of the unification arc. Merges three job sources into
one normalized public feed and one Career Center page.

**Commit:** d0d9d77 feat(jobs): Session 31 - unified jobs feed + Career Center page

**What shipped:**

New engine `jobs_unified_engine.py` (~230 lines):
- get_unified_jobs(source, q, limit) -> dict
- Merges charvak_jobs + charvak_client_roles + charvak_micro_projects
- Normalized shape: id, source, source_label, title, company,
  location, type, skills[], compensation{}, posted_at, detail_url
- Sanitization by construction: staffing items never carry
  client_name, vendor refs, or budget (matches /open-roles policy)
- Source-isolated: a failure in one source never breaks others
- Sort: posted_at DESC, source ASC
- Filters: source (whitelist), q (title substring), limit (1..200)

New route `GET /api/jobs/unified`:
- Public read (no auth) ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â same data as /job-board + /open-roles + /micro-internship
- Rate limited 120/min
- Validates source against VALID_SOURCES whitelist
- Rejects non-integer limit with 400

New page `/career-center/jobs` (templates/career-jobs.html):
- Filter pills: All / via Charvak / Gigs / Job Board
- Debounced title search (300ms)
- Job cards: source badge, urgency badge, title, company/location/type,
  experience, skills (first 6 + "N more"), View & Apply button
- Empty state with Clear Filters
- Cards deep-link to /open-roles/... or /micro-internship/...

Panel integration:
- /career-center now has "View all openings ->" link in the
  unified activity panel header
- Refresh button shows dim-then-restore visual feedback

**Verified:**
- 8-scenario HTTP test: all sources, source filter, title search,
  invalid source (200 + error dict), invalid limit (400), limit,
  sanitization over HTTP (no leaks), first item shape
- Browser: 8 items (7 staffing + 1 gig), filters work, search works,
  cards navigate
- Prod: /career-center/jobs -> 200, /api/jobs/unified -> 200

**Session 32 candidates:**
- A (recommended): Unified candidate signup entry point
- B: Close the Assess -> Upskill loop
- C: Roll the unified panel to /my-results and /profile
- D: Show top 3 jobs inline in the /career-center panel

**Long-term arc:**
- 30: unified candidate profile (SHIPPED)
- 31: unified jobs feed (SHIPPED)
- 32: unified candidate signup (candidate)
- 33: Assess -> Upskill loop (candidate)

**Reminder:** Render Postgres password rotation still pending.


## Session 30 CLOSED (2026-10-06) - Unified candidate profile (Phase 1)

The first concrete step of the unification arc. A read-only aggregation
layer that presents a candidate's activity across all subsystems in one
call. First surface: the Career Center panel.

**Two commits:**
- 2040caf feat(candidate): Session 30 - unified candidate profile endpoint
- 8a4025d feat(candidate): Session 30-4 - unified activity panel in Career Center

**What shipped:**

New engine `candidate_profile_engine.py` (~290 lines):
- get_unified_profile(email, include=None) -> dict
- 10 sections: identity, profile, assessments, certificates,
  applications, training, career_engine, integrity, credits, doketsrb
- Read-only. No writes, no schema changes, no engine modifications.
- Aggregates large tables (integrity events -> counts + risk level)
- Enumerates small tables (certificates, applications, enrollments)
- Section-isolated: a failure in one section never breaks the response
- Graceful empty sections for nonexistent users

New route `GET /api/candidate/{email}/unified`:
- Auth + email-match enforced (403 on mismatch)
- Rate limited 60/min
- ?include= filter validated against ALL_SECTIONS whitelist

Frontend panel in career-v2.html:
- "Your activity" section at the top of /career-center
- 4 stat cards: Certificates, Applications, Integrity, Credits
- Recent assessments list (last 5, with score + pass/fail)
- Hidden entirely when logged out
- Silent-fail on auth/network errors

**Verified:**
- Engine standalone test: all 10 sections return correct data
- HTTP test matrix: 401 (no auth), 200 (full), 200 (filtered),
  400 (invalid section), 403 (different user)
- Browser: panel renders with real data (6 certs, 2 apps,
  254 integrity events, 11641 credits)

**Strategic context:**
This is the read-only aggregation layer that the unification
discussion called for. The engines stay separate; the experience
becomes unified. Sessions 31-33 will extend it:
- 31: /api/jobs/unified (merge job-board + staffing + micro-projects)
- 32: Unified /candidate/signup entry point
- 33: Close the Assess -> Upskill loop

**Reminder:** Render Postgres password rotation still pending.


## Session 29 CLOSED (2026-10-06) - Career Assessment Phase 2b (SQL)

The SQL format is live on prod. Phase 2b is COMPLETE ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â all 10 assessment
formats from the original plan are shipped and tested.

**Commit:** a649f80 feat(sql): Session 29 - SQL format E2E via Judge0 SQLite

**What shipped:**
- _prompt_sql: generates {schema, task, starter_code, expected_output}
  with strict output-column rules (no id unless asked, no sort keys)
- _normalize_question: sql branch validates schema + task + expected_output
- _strip_answers_for_frontend: strips expected_output (no answer leak)
- _score_sql_batch: runs schema+candidate query via Judge0 SQLite
- _sql_outputs_match: NEW Python-side comparison with:
    * float tolerance (abs < 1e-3) so AVG returns 150.0 matching 150
    * trailing blank line normalization
    * strict column-count match (still fails on shape mismatch)
- _dispatch_scoring: routes hybrid + sql to _score_sql_batch
- registry: sql.available = True (SQLite dialect)

**Frontend (ai-assessment.html):**
- renderQuestionBody: sql branch renders schema + task + query textarea
- textareas (both coding and sql) no longer pre-filled with starter code
  so blank submissions register as blank (was a real bug)
- placeholder shows the hint text

**Verified E2E:**
- 10 SQL questions generated with valid schemas
- Judge0 SQLite execution: 8/8 correct queries scored 100%
- AVG float tolerance: SELECT AVG(price) returning 150.0 matches AI's '150'
- Sort-key prompt fix: "names ordered by age" now produces 1-column output
- Blank submissions: 'No query submitted' (not the starter text)
- Skill gap + learning path work identically

**Session 30 candidates:**
- A: Admin UI for integrity events (surfaces Session 27 data)
- B: Roll Layer A (integrity) to other assessments (Versant/Mock/CBAT)
- C: Phase 4 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â certificates for coding/SQL, employer-facing badges
- D: Reverse Staffing / Career Center polish

**Reminder:** Render Postgres password rotation still pending (Session 19).

**Backup:** Full backup recommended at session close.


## Session 28 CLOSED (2026-10-06) - Career Assessment Phase 2b (coding)

The coding format is live on prod. Real code execution against per-question
test cases via Judge0 CE (ce.judge0.com, free, no auth).

**Three commits pushed:**
- deca0c0 feat(judge0): Session 28a - Judge0 client for code execution
- c65d118 feat(coding): Session 28b - coding format E2E via Judge0
- (this commit) docs(session-28): Phase 2b coding close-out

**New surface area:**
- judge0_client.py (new) - Judge0 CE wrapper, runs code against test cases
- career_assessment_engine.py - coding format enabled (was "coming soon")
- templates/ai-assessment.html - coding renderer with code textarea

**Engine changes:**
- _prompt_coding() - generates coding problems + starter_code + 3 test cases
- _normalize_question() - coding branch validates problem + test_cases shape
- _strip_answers_for_frontend() - strips test_cases (no answer leak)
- _score_coding_batch() - runs submissions via judge0_client per question
- _dispatch_scoring() - routes hybrid+coding to _score_coding_batch
- _format_registry()["coding"]["available"] = True

**Verified E2E on local + prod:**
- 10 coding questions generated with valid test cases
- Judge0 execution: 3/3, 3/3, 3/3, 3/3, 3/3, 3/3, 0/3, 0/3, 0/3, 0/2
- Overall 60%, correct_count 6, persisted correctly
- Skill gap + learning path work identically to other formats
- Prod API confirms coding.available = true

**Credit model:** reuses AI-scored keys (20/30/40 for quick/standard/full).
No new credit key, no new table, no schema change.

**Still disabled: SQL format.** Session 28c will add it. Requires:
- Sandbox DB per request (or use Judge0's sqlite3 language ID)
- _prompt_sql + _normalize_question sql branch + _score_sql_batch
- _strip_answers_for_frontend sql branch
- Frontend renderQuestionBody sql branch

**Session 29 candidates:**
- A: SQL format (Session 28c) - completes Phase 2b
- B: Admin UI for integrity events (from Session 27)
- C: Roll Layer A + coding out to other assessments
- D: Document-phase close-out + backup

**Reminder:** Render Postgres password rotation still pending.


## Session 27 CLOSED (2026-10-06) - Anti-Cheating Layer A

Deterministic integrity signals on Career Assessments. Shipped in
three commits: engine + schema + routes (1124a38), frontend capture
(91e1b1f), and this docs commit.

**What shipped:**

- **`integrity_engine.py`** ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â standalone engine recording five
  environment signals during an assessment: paste, tab_switch,
  contextmenu, focus_out, rapid_input. Self-healing DDL. Batch read
  + summary methods. Risk classifier (clean / minor / moderate /
  elevated).

- **New table `charvak_assessment_integrity_events`** ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â one row per
  event. Columns: event_id, assessment_id, email, event_type,
  metadata (JSONB), occurred_at. Indexes on assessment and email.

- **New column `charvak_career_assessments.integrity_summary`** ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â
  JSONB rollup: per-type counts + total + risk_level. Written on
  every event for fast display (no aggregation query needed).

- **`POST /api/integrity/event`** ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â auth-gated, email-match,
  ownership-verified (the assessment must belong to the caller).
  No credits charged. Rate limit 120/min. Rejects non-string
  `assessment_id` / `event_type` with a clean 400.

- **`GET /api/admin/career-assessment/{aid}/integrity`** ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â
  admin-gated view returning event list + summary. Belt-and-suspenders
  via require_admin (middleware already gates /api/admin/*).

- **Frontend capture in `templates/ai-assessment.html`** ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â
  document-level listeners armed only when `_carCurrentAssessment`
  is non-null. Batches and flushes every 2 seconds via fetch.
  Uses keepalive fetch on pagehide (sendBeacon can't set auth headers).
  Silent-fails: a dead backend never breaks the candidate experience.
  Exposes `window.__integrityDebug` for manual testing.

**Verified E2E:**

- 8-scenario curl matrix: 401/200/404/400/400/200/403 all pass
- Engine unit test: records, reads back, summarizes, classifies risk
- Browser test: all 5 event types land in the DB with correct
  metadata (paste with chars, tab_switch with duration_ms,
  rapid_input with chars_per_ms)
- Input hardening: a list-shaped `assessment_id` returns 400,
  not 500

**Zero impact on the assessment flow itself.** The candidate UX is
unchanged. Events are recorded as a side channel; nothing is blocked.

**What's next ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Session 28 candidates:**

- A: **Career Assessment Phase 2b** (coding + SQL via Judge0) ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â
  now unblocked by Layer A. This is the piece that makes the
  assessment commercially viable.
- B: **Admin UI for integrity data** ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â surface the events on
  `/admin/client-roles/{role_id}` or a new page for assessment
  review. Turns recorded events into an employer-facing artifact.
- C: **Layer A roll-out to other assessment flows** ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Versant,
  Mock Drives, CBAT, IELTS. Each is a ~5-line frontend addition
  because the engine + route already exist.

Recommendation: **A** ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Layer A unblocks Phase 2b, and Phase 2b is
the product that makes the entire assessment stack sellable to
employers. The admin UI is a valuable follow-up but Phase 2b is the
strategic priority.

**Backup:** recommended after Session 27 commit ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â snapshot the
Layer A work in the same style as the Session 26 backup.

## Sessions 19-21 CLOSED (2026-10-04) - Certificate v2

Three sessions shipped together as the certificate-v2 release.

**Session 19 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Size upgrade CTA + supersedes chain**
- supersedes / superseded_by columns on charvak_readiness_certificates
- Auto-link on upgrade (same email/role/industry/level)
- Yellow "want a more precise score?" card on below-benchmark certs
- Green "Improved from an earlier check" callout on the new cert
- 15-question Standard check CTA (25 cr)

**Session 20 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Certificate polish**
- Best Score stat card on /my-results
- "Show only latest per role" toggle
- Supersede email notification

**Session 21 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â PDF download**
- render_readiness_certificate_pdf() ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â branded A4 layout, single page
- GET /api/readiness/{id}/download (public + token fallback)
- Frontend: real PDF download, no more window.print()

**Session 22 candidates:**
- A: Sprint B /my-jobs verified job matching (2 sessions)
- B: Certificate round 2 (QR, watermark, multi-language)
- C: Anti-cheating Layer A (1 session)

Recommendation: A.



## Session 22 CLOSED (2026-10-05) ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Sprint B: Client Staffing Pipeline

The CBREX-mediated staffing pipeline is live end-to-end.
Candidates can browse open roles, apply with screening answers and
consent, and self-provision their profile inline in the apply modal.

**6 commits shipped:**
- `e23b853` schema + engine + 9 routes (Session 22a)
- `41a91a1` /open-roles + /open-roles/{id} + apply modal (Session 22b)
- `598101e` candidates_engine + /api/candidates/* (Session 22c.1)
- `b95d39d` inline profile form (Session 22c.2)
- (+ two micro-fixes: registered_at column, JSONB skills coercion)

**Live URLs (prod):**
- /open-roles             public listing
- /open-roles/{role_id}   public detail + apply

**Backend namespace:**
- /api/staffing/open                      public listing
- /api/staffing/roles/{role_id}           public detail
- /api/staffing/roles/{role_id}/apply     auth + consent
- /api/candidates/me                      auth (caller only)
- /api/candidates/upsert                  auth (create/update)
- /api/admin/client-roles/*               6 admin endpoints

**5 new tables:**
charvak_client_roles, charvak_role_screening_questions,
charvak_role_screening_answers, charvak_candidate_documents,
charvak_candidate_consents

**Verified E2E on local + prod:**
- Anonymous browse, login-gated apply, dynamic question rendering,
  consent capture, inline profile form, retry-on-profile-missing,
  green success banner, all data persisted with correct FK links.

**Still pending for Session 23+:**
- CBREX package generator (PDF + ZIP with resume/eval/certificate)
- Admin dashboard (/admin/client-roles UI)
- Nav link for /open-roles in base.html
- Candidate profile edit page (/profile)



## Session 22.5 + Role Loading CLOSED (2026-10-05)

Extended Session 22 into a full staffing pipeline launch.

**7 real roles loaded to prod:** AI Machine Learning Engineer,
AI Agent Operations Engineer, Platform Engineer, AI Engineer (all NCS,
urgent), Lead Firmware Engineer, Application Engineer (Lenze), Sr.
Mechanical Design Engineer STP (Middle East Group). 92 screening
questions across all roles.

**New features:**
- /open-roles  public role listing (works on any device)
- /open-roles/{id}  detail + apply modal
- Inline profile collection when candidate has no profile
- /profile  candidate profile edit
- /my-applications  candidate's applications list
- HR email notification on every application to
  hr@charvakit.com + charvakit@gmail.com

**CBREX name fully stripped:** client_name="via Charvak", all vendor
fields nulled, budgets hidden from public API + UI, zero CBREX
strings in DB.

**Commits:** a2620d5, 8b7831f, e97d7ef, 5fb67f2 + seed files

**Verified E2E on prod:** fresh user registration -> apply -> inline
profile -> green success banner -> email arrives at both inboxes.

**Lesson:** database.py loads .env.local with override=True ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â silently
overrides shell env vars. For prod data ops: rename .env.local first,
use direct psycopg2, restore after.

**Next (Session 23):** CBREX package generator
- GET /api/admin/applications/{app_id}/cbrex-package (JSON)
- .pdf (Charvak Evaluation Form via pdf_engine.py)
- .zip (resume + eval PDF + certificate PDF + consent proof)



## Session 23 CLOSED (2026-10-05) - Submission package generator

Full pipeline now works end-to-end via API. Admin can generate a
complete client-ready submission package from any application.

**Commits:**
- d35032c  Session 23 4a.1 - JSON package builder
- b6ee7e3  Session 23 4a.2 - PDF evaluation form
- 579b249  Session 23 4a.3 - ZIP bundle + CBREX de-identifier
- 5a762aa  Session 23 polish - consistent 404s for missing apps

**New endpoints (all admin-gated):**
- GET /api/admin/applications/{id}/submission-package       (JSON)
- GET /api/admin/applications/{id}/submission-package.pdf   (PDF)
- GET /api/admin/applications/{id}/submission-package.zip   (ZIP)

**ZIP contents:**
- 01_candidate_profile.json
- 02_evaluation_form.pdf (branded Charvak layout)
- 03_readiness_certificate.pdf (if cert exists)
- 04_resume.<ext>               (if uploaded or text present)
- 05_consent_proof.<ext>        (if proof file uploaded)
- README.txt                    (manifest enumerating actual contents)

**CBREX de-identifier sweep completed:**
- Renamed cbrex_pdf_engine.py -> submission_pdf_engine.py
- All 3 routes renamed /cbrex-package* -> /submission-package*
- All function names, docstrings, comments de-identified
- Consent vendor default changed CBREX -> Charvak
- Result: 0 CBREX references across the codebase

**Verified E2E on local APP-7F862AE1:**
- All 3 new routes 200 (JSON/PDF/ZIP)
- Old routes 404
- Missing app IDs 404 consistently across all three
- ZIP contents match README

**Next session (24):** admin UI for client roles + applications
- /admin/client-roles          (list + applicant counts)
- /admin/client-roles/{role_id} (detail + applicants + downloads)
- Link in admin dropdown
- All backend endpoints already exist



## Session 24 CLOSED (2026-10-05) - Client Roles admin UI

Full admin interface for the staffing pipeline. Backend endpoints
already existed from Session 22; this session added the frontend.

**Commit:** `37f978f` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â feat(admin): Session 24 - client roles
list + role detail pages

**New pages:**

- `/admin/client-roles`
  - Table of all client roles with applicant counts
  - Summary strip: Total / Urgent / Applicants / Sourcing
  - Filter buttons by status (all / sourcing / shortlisting / submitted / closed)
  - Per-row: View detail, Open public page

- `/admin/client-roles/{role_id}`
  - Role info card with skills + priority badge
  - Summary strip: Total / Pending / Submitted / Shortlisted
  - Applicant list ranked by readiness
  - Per-applicant actions:
    - View modal with full profile + screening answers
    - Download submission-package.zip

**Bugs fixed during session:**

1. Modal trapped in `<main>` stacking context ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â moved to `{% block modal %}`
2. Modal button bindings moved inside DOMContentLoaded
3. Jinja parsed a template tag inside a JS comment ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â removed
4. Click delegation handler was silently lost in an earlier patch ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â restored
5. `loadAll` / `loadRoles` exposed on `window` for inline Refresh buttons

**Local dev admins created matching prod:**

- hr@charvakit.com
- charvakit@gmail.com
- ADMIN_EMAILS env updated in `.env.local`

**Verified E2E on local:**

- List page renders 7 roles, filters work, Refresh works
- Detail page renders 1 applicant, modal works, Download works
- No console errors

**Prod verified:**

- `/admin/client-roles` returns 302 (redirect to login = gate works)
- Old `/cbrex-package` route returns 401 (retired)

**Next session (25) candidates:**

- Status update UI in the applicant modal (shortlist / submitted / hired / etc.)
- Recruiter notes textarea
- Batch download ZIP (all applicants per role)
- Security sweep on new admin endpoints





## Session 25 CLOSED (2026-10-05) - Admin applicant actions

Three patches that close the admin workflow loop.

**Commit:** `cdc5cb3` + following (dashboard card)

**Shipped:**

- **Patch 5c.1** - Applicant status + recruiter notes UI in the
  modal on /admin/client-roles/{role_id}
  - Status dropdown (pending/shortlisted/submitted/interviewing/
    offer/hired/rejected/withdrawn)
  - Recruiter notes textarea (private, not shown to candidates)
  - Save button POSTs to /api/admin/applications/{id}/submission-status
  - Prefills current values on modal open
  - Auto-refreshes the applicant list after save

- **Patch 5c.2** - Batch download ZIP per role
  - New endpoint: GET /api/admin/client-roles/{role_id}/applicants-batch.zip
  - Returns one ZIP containing a per-applicant subfolder for every
    applicant of the role: candidate_profile.json + evaluation_form.pdf
    + README.txt + SUMMARY.txt at the root
  - New module: client_staffing_batch.py (standalone helper)
  - Frontend: 'Download All as ZIP' button next to Applicants header

- **Patch 5c.3** - Admin dashboard card
  - 'Client Roles' button added to admin-unified.html Quick Actions

**Fixed during session:**

- Schema assumption bug: charvak_applications has no candidate_name
  column. Batch query now LEFT JOINs charvak_candidates on email.

**Session 25 result:** the full admin workflow works from the
browser, no DB editing required:
  dashboard -> roles list -> role detail -> applicant modal
    -> status change + notes -> save
    -> single download or batch download

**Next session (26) candidates:**

- Security sweep on new admin endpoints (Session 14 style)
- Delete or leave legacy /api/assessment/* routes (8 remaining)
- Verify charvak_jobs legacy reference in main.py
- Anti-cheating Layer A (blocks Career Assessment Phase 2b)
- Career Assessment Phase 2b (coding + SQL via Judge0 sandbox)



## Session 26 CLOSED (2026-10-05) - Security sweep + cautious cleanup

Three items investigated; zero deletions made. The system is cleaner
than the audit implied.

**Item 1 - Security sweep on new admin endpoints (PASSED)**

Ran the 4-scenario matrix on 10 admin routes from Sessions 22-25:
- Anonymous -> 401
- Non-admin user (valid token) -> 403
- Admin -> 200 or 400
- Zero security gaps

Also confirmed: 10 pre-existing admin routes (analytics, settings,
users, purchases, testimonials x5, cleanup-users) rely on
`admin_auth_guard` middleware alone (no require_admin in body).
Verified with non-admin token: all return 403.

**Item 2 - Legacy /api/assessment/* routes (KEPT, not deleted)**

Initial audit flagged 7 routes as dead. Deep audit revealed they
must stay:
- COMMITMENT.md documents them as deliberately preserved
- Two underlying engine methods have OTHER live call sites
  (main.py:10614 and main.py:10581)
- audits/audit-routes.json catalogs all 8
- No proof exists of zero external callers

Action: tombstone comment added above the block documenting the
decision. Routes left in place.

Note: POST /api/assessment/mcq/generate IS live (used by mcq.html).

**Item 3 - charvak_jobs reference (NOT dead, no action)**

`charvak_jobs` is a LIVE table used by:
- main.py:1629 - active /api/jobs/post route
- api_sync.py - DoketsRB integration (jobs sync)
- ats_engine.py - ATS provider integration
- job_board_engine.py - the engine that owns the table
- 4 public routes verified live: /api/jobs, /search, /stats, /applications

The table serves the public job board, distinct from
`charvak_client_roles` which serves the CBREX staffing pipeline.
Both are live. Neither supersedes the other.

Action: no action. Table and routes stay.

**Process lesson:**

Simple greps miss real usage. In both cases, only cross-referencing
multiple file types + historical tracker decisions revealed the truth.

Rule for future audits: grep across ALL file types including
historical trackers and audit artifacts.

**Next session (27) candidates:**

- Anti-cheating Layer A (blocks Career Assessment Phase 2b)
- Career Assessment Phase 2b (coding + SQL via Judge0)
- AuditBot Continuous
- Rotate Render Postgres password (still pending)


---

---

---

---

## Session 18 CLOSED (2026-10-04) - Train stage resurrection

Custom-course generator (Phase 1) plus critical Train-stage bug fixes.
The lesson player went from broken to fully functional.

**Highlights:**
- Custom-course generator: users can generate a private course for any
  weak topic without a matching catalog course (50 credits each)
- Learning path is now fully self-contained (no external links)
- Fixed charvak_enrollments missing recipient_name column
- Fixed charvak_certificates missing recipient_name column
- Fixed my-course.html missing updateProgress() function
- Fixed all my-course.html POST fetches (auth headers)
- complete_week() now auto-issues a certificate on the final week

**Verified:** Course completed end-to-end, certificate CERT-9C1DBCD84B4E
issued, verify URL live.

**Session 19:** Phase 2 size upgrade CTA (10 -> 20 question upsell)
**Session 20:** Certificate enhancement (signature, HMAC, QR)
**Session 21:** Sprint B /my-jobs

---

**HEAD:** f2dbf00
**Last updated:** 2026-10-04 (Session 16 - Premium Report product shipped)
**Version:** `v3.5-session-16-20261004`

---

## Where we are (Session 16)

Session 16 shipped the **Premium Report** product (Rs 199 / 400 credits)
end-to-end across 5 commits.

**Commits this session:**
- `aa8a279` feat(pdf): add PDF engine for Premium Report generation
- `c60a9a5` feat(premium-report): add report generator engine + routes
- `961a3dc` feat(premium-report): PDF download route + SendGrid email
- `a2537e6` feat(premium-report): frontend unlock flow + /my-reports
- `980bbdc` fix(premium-report): accept ?token= for browser/email downloads

### Shipped

**Premium Report product**
- `pdf_engine.py` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â fpdf2-based PDF renderer with branded cover page,
  headers, footers, sections, severity badges, Unicode via DejaVu
- `premium_report_engine.py` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â one OpenAI call produces 5 AI sections
  from the source product's free-tier scan data; persists to
  `charvak_premium_reports`; falls back to a template if AI is down
- 3 report types: `auditbot`, `lock_in_breaker`, `skill_twin`
- Credit key: `premium_product_report` (400 cr) ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â separate from the
  existing `premium_report` (25 cr) used by assessment reports
- SendGrid email with the PDF as a base64 attachment
- `templates/includes/premium-upsell.html` rewritten to be
  config-aware (reads `window.CHARVAK_PREMIUM`); falls back to
  notifyMe() on the 24 other pages that include it
- `/my-reports` dashboard listing the user's reports with
  Download PDF buttons

### E2E verified
- Full flow: free scan ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ unlock ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ AI generation ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ PDF ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ email ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ download
- Credit deduction: exact 400 per report
- 3 premium reports generated during testing
- Email delivered to test-register email
- Download works from both the inline upsell and the dashboard

### Notes
- Browser <a href> navigations don't send Authorization headers, so
  the download route accepts ?token= as a fallback. `/generate`
  includes the caller's token in the returned `download_url`.
- Fixed a latent bug: `auditbot.html` never set
  `window.lastAuditResult`, so the upsell always said "Run a scan
  first". The other two premium pages already did.

---

## Where we are

Session 15 completed Silent-Killer 9b (continuous monitoring cron +
state-change email alerts) plus several smaller items.

**Commits this session:**
- `5e64b1a` feat(payments): expose PAYPAL_MODE in /api/payment/status
- `1f1f834` docs: sync SCHEMA.md (128->164 tables) + PAGES-INVENTORY delta
- `f468c50` feat(silent-killer): continuous monitoring cron + alerts (Session 9b)

### Shipped

**Silent-Killer 9b (headline)**
- enhanced_email.send_silent_killer_alert() - SendGrid email on state change
- products_engine.silent_killer_due_watches() - due-watch selector
- POST /api/cron/silent-killer-scan - X-Cron-Secret auth
- Full frontend rewrite of the script block (previous version had 15
  lines with malformed JS strings; page rendered but nothing worked)
- "Notify Me" button retired; live badge replaces it
- Render cron job silent-killer-scan runs every 5 min, verified firing

**Observability**
- /api/payment/status now returns paypal_mode ("live" | "sandbox")
- Fixed CRON_SECRET typo in local .env (colon -> equals)
- Set PAYPAL_MODE=live on Render; confirmed via /api/payment/status
- Added CRON_SECRET to silent-killer-scan cron's environment

**Docs**
- SCHEMA.md regenerated: 128 -> 164 tables
- PAGES-INVENTORY.md header bump + Sessions 8-15 delta section

### Verified E2E

Local:
- Cron without secret -> 401
- Cron with wrong secret -> 401
- Cron with correct secret -> 200
- Due watch detection -> only due watches scanned
- fail -> ok flip -> alerted: 1, email sent to owner
- Browser: page fully functional (panel, recheck, history, delete)

Prod:
- /api/payment/status: paypal_mode = "live"
- Render cron silent-killer-scan: 200 + {"status":"success",...}
- Created a test watch directly in prod DB; Render cron picked it up
  and ran the scan within 5 minutes (confirmed scan row with 200 OK).
  Test watch was cleaned up afterward.

### Local vs Prod database

Local .env.local points at charvak_dev on localhost:5432.
Prod uses vouchai on Render Postgres.

### Flagged for Session 16

- Career Assessment Phase 2b: coding + SQL via Judge0 (2-3 days)
- Premium Report product (8-12 hrs, product decision)
- Doc pass on remaining stale files (DEFERRALS, DEV-SETUP, DOC-STYLE)
- Rotate PayPal + SYNC keys (external dashboards)

---

## Career Assessment product status

| Phase | Status |
|---|---|
| Phase 1 (MCQ) | Shipped |
| Phase 2a (7 more formats) | Shipped |
| Phase 3 (adaptive + skill gap + learning paths) | Shipped |
| Phase 2b (coding + SQL) | Session 16+ |
| Phase 4 (certs, badges) | Future |

---

## Environment

- HEAD: f468c50
- Local Python: 3.11.9 venv
- Local DB: Postgres 15 (charvak_dev)
- Prod DB: Render Postgres (vouchai)
- Prod: https://www.charvakit.com
- Render service: srv-d9hhljd8nd3s73d2hoeg
- Render cron jobs: send-emi-reminders, cleanup-notifications,
  send-queued-emails, silent-killer-scan (new)

---

## Session 17 COMPLETE ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Sprint A shipped (2026-10-04)

Sprint A of the Proof Layer framework is live. The free Role Readiness
Certificate is end-to-end: landing page -> assessment -> shareable
certificate URL with HMAC verification.

**7 commits shipped:**
- 14b2bb8  feat(readiness): Sprint A backend (engine + 5 routes + benchmarks)
- 4fc158e  feat(readiness): readiness.html (public certificate page)
- 2c09632  feat(readiness): readiness-check.html + route (public landing)
- 87aa95a  feat(readiness): ai-assessment deep-link + certificate CTA
- 814db5e  fix(readiness): percentile floor 5..99, level/passing fallbacks, OG tags
- <next>   fix(readiness): move var _a out of string concat

**Live at:**
- GET /readiness-check     ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â public free landing
- GET /readiness/{id}      ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â public shareable certificate
- GET /api/readiness/{id}  ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â public read
- GET /api/readiness/verify/{hash}  ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â public verification
- POST /api/readiness/generate      ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â auth-gated certificate creation
- GET /api/readiness/list/{email}   ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â auth-gated list

**Verified E2E on local:**
- Dropdowns populate [107, 67, 8] for role/industry/level
- Free check start -> deep-link -> questions skip Step 1
- Answer -> result page (with green certificate CTA)
- Get My Certificate -> /readiness/RDC-XXXX
- Certificate renders with score, benchmark, percentile (floor 5), hash
- Verify URL returns {valid: true}
- Tampered hash returns {valid: false}

**Session 17d (2026-10-04):** Made the certificate discoverable.
/my-results now lists readiness certificates with a filter pill + stat
card. Top nav has a "Readiness Check" link. User dropdown has a
"My Certificates" button. Closes the discoverability gap on the Sprint
A certificate.

**Session 18 scope (next):**
1. Custom-course generator (replace external links with Charvak-hosted
   custom courses in learning paths)
2. Size upgrade CTA on quick-check results (10 -> 20 questions for
   below-benchmark users)
3. Sprint B kickoff: /my-jobs verified matching

---

## Session 17 priority (locked)

**Scope:** Gap 1 (Role Readiness Score) + Gap 3 (Anti-Cheating Layer A)
alongside Career Assessment Phase 2b (coding/SQL via Judge0).

**Why:** Gap 3 is a prerequisite for Phase 2b ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â without integrity signals,
employers will dismiss the coding/SQL assessments. Shipping 2b without
anti-cheating produces a technically complete feature that fails commercially.

**Reference:** See `COMPETITIVE-STRATEGY.md` for the full analysis, the 4 gaps,
the roadmap, and the metrics we're tracking. Re-read at the start of every
session.

**Gaps 2 and 4 (deferred, documented):**
- Gap 2: Multilingual Voice AI ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Sessions 20+
- Gap 4: AuditBot Continuous Compliance ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Sessions 18-19

---

## Recommended next session (Session 16)

Option A: Career Assessment Phase 2b (coding + SQL) - 2-3 days.
Option B: Premium Report product - 8-12 hrs.
Option C: Doc pass + cleanup - ~1.5 hrs.

Recommendation: A.

**Post-Session 16 update:** Premium Report shipped. Session 17 is now
open to:
- Career Assessment Phase 2b (coding + SQL via Judge0 sandbox)
- Or a doc pass on the remaining stale files
- Or a security sweep (Session 14 style)

<!-- BEGIN SESSION-48 -->

## Session 48 Close-Out (2026-10-18)

**HEAD:** 1399073 (feat(cohorts): Session 48 - Cohort Mode)
**Wave 1:** 100% complete

### Session 48 Shipped

- Cohort Mode: batch leaderboards
- cohorts_engine.py (5 methods)
- 3 tables + 8 routes + 2 templates
- base.html + passport.html integration

### Session 47.5 Shipped (same week)

- scripts/run_migrations.py (idempotent runner)
- Wired into Render start command
- Fixed 3 migration warnings
- 89 migrations clean on prod

### Wave 1 Arc Complete

Sessions 46-A, 46-B, 47, 48 all shipped. All four flywheel layers live on prod.

### Fresh Chat Resume Prompt

Paste this when starting Session 49:

Resume from 1399073. Session 48 (Cohort Mode) closed clean.
Wave 1 complete: Passport, Skill Twin, Daily Drills, Cohort Mode.
All 4 live on prod. HEAD=origin/main=1399073. Tree clean.
Prod healthy, 89 migrations applied.

Session 49 plan: [OPTION A/B/C/D from COMMITMENT.md]

<!-- END SESSION-48 -->

<!-- BEGIN SESSION-49 -->

## Session 49 + 49.5 Close-Out (2026-10-19)

**HEAD:** d3de41b (feat(cohorts): Session 49.5 - public cohort toggle)
**Wave 1:** 100% complete with production polish

### Session 49 Shipped (commit 5525cd7)

- Cohort RBAC: leave, rename, delete, promote, demote
- Discovery: list_public_cohorts + public discovery section
- Owner actions menu + member list with role badges
- 3 critical fixes: role in cache path, cache invalidation on join/leave,
  modals moved to {% block modal %} slot

### Session 49.5 Shipped (commit d3de41b)

- Public cohort toggle (checkbox in create modal + button in owner actions)
- is_public in get_leaderboard response (both cache paths)
- New POST /api/cohorts/{id}/visibility route

### Wave 1 Arc Complete + Polished

Sessions 46-A, 46-B, 47, 48, 49, 49.5 all shipped.
All four flywheel layers live and polished on prod.

### Fresh Chat Resume Prompt

Paste this when starting Session 50:

Resume from d3de41b. Session 49.5 (cohort polish) closed clean.
Wave 1 complete with production polish.
HEAD=origin/main=d3de41b. Tree clean. 89 migrations applied.
Prod healthy.

Session 50 plan: [OPTION A/B/C/D from COMMITMENT.md]
Recommended: A (Trust Score Public API - GET /api/passport/{handle}/verify)

### Also pending

- Amrita CDC reply to Prof. Raj (draft exists in this session's context)
- Render Postgres password rotation (Session 19 flag)
- ~~/api/lms/progress ownership check~~ RESOLVED 2026-10-19 (main.py:8844-8857)

<!-- END SESSION-49 -->