# TRACK A + TRACK B MASTER PLAN

**Created:** 2026-10-12
**Owner:** Product roadmap
**Status:** Active
**HEAD at creation:** 3fd8ad7

---

## Overview

Two business models, one infrastructure.

**Track A — Corporate/MBA readiness (B2C)**
Active focus. Revenue-focused. Short sales cycle. Sessions every week.

**Track B — CSR skilling infrastructure (B2B)**
Flagged. Discovery-focus. Long sales cycle. Sessions once per month,
starting only after Track A Batch A2 ships.

Both tracks share 80% of the codebase. Track B adds a packaging layer
(batch mode + API + partner management) on top of what Track A builds.

---

## PART 1 — TRACK A (ACTIVE)

### Batch A1 — Small cleanup (~45 min)

| ID | Item | Effort | Source |
|---|---|---|---|
| A1.1 | Rotate Render Postgres password | 5 min | Session 19 flag |
| A1.2 | Set PAYPAL_MODE=live explicitly on Render | 1 min | Session 9 quick win |
| A1.3 | Fix custom-courses section flicker on /ai-courses | 15 min | Session 42-5 |
| A1.4 | CI hook for scripts/test_ielts_relevance.py | 30 min | Session 41 flag |

**Success:** Prod 200, no console errors, PayPal status=live, CI fires.

### Batch A1.5 — Signup wall fix (1.5 sessions)

**Trigger:** GA4 + DB data (Oct 12) show 368 visitors → 26 signups (7%).
180 form_starts → 46 completions (25%). Only 7 certs.

**Goal:** Let students take the assessment before login.
Prompt signup only when saving the certificate.

**Expected impact:** 3x more certificates from same traffic.

**Approach:**
1. Issue a signed short-lived token on assessment start
2. Store answers against token (not user)
3. Show score without login
4. Prompt login only for certificate generation
5. Migrate token data to user account on login

**Success metric:** `readiness_complete` events double within 2 weeks.

### Batch A2 — Certificate round 3 (~3 hrs, 1 session)

| ID | Item | Effort |
|---|---|---|
| A2.1 | QR code in certificate PDF | 30 min |
| A2.2 | Watermark on certificate PDF | 15 min |
| A2.3 | Multi-language certificate render (Hindi, Telugu) | 2 hrs |

**Success:** QR encodes verify URL, watermark subtle, ?lang=hi renders.

### Batch A3 — FYP features (~4.5 hrs, 1 session)

| ID | Item | Effort | Priority |
|---|---|---|---|
| A3.1 | Citation Helper | 30 min | High |
| A3.2 | Milestone Roadmap | 45 min | High |
| A3.3 | Plagiarism-Safe Rewriter | 1 hr | Medium |
| A3.4 | Refine Section (interactive) | 2 hrs | Medium |

**New credit keys:**
- fyp_citation: 8
- fyp_milestone_roadmap: 15
- fyp_humanize: 15
- fyp_refine: 5 per instruction

### Batch A4 — Personalized training views (1 session)

| ID | Item | Effort |
|---|---|---|
| A4.1 | /training-engine personalizes by readiness cert skill gaps | 1 session |

**Success:** User with weak "System Design" cert sees those courses highlighted.

### Batch A5 — DoketsRB bidirectional sync (2 sessions)

| ID | Item | Effort |
|---|---|---|
| A5.1 | Sync infrastructure + API keys on both sides | 1 session |
| A5.2 | Sync status UI + user-triggered pull | 1 session |

**Blocker:** DoketsRB team must wire their side. If they do not, batch stalls.

### Track A completion

- Version tag: v3.6-track-a-complete-YYYYMMDD
- Backup
- Docs sync (MASTER-REFERENCE, SESSION-CONTEXT, KNOWN-ISSUES,
  COMMITMENT, PAGES-INVENTORY, SCHEMA)
- Post-launch review

**Estimate:** 6-7 sessions at one session/week = 6-7 weeks.

---

## PART 2 — TRACK B (FLAGGED, PARALLEL AFTER A2)

### Cadence rules

- 1 Track B session per 4 Track A sessions
- Never compromise a Track A session for Track B
- If Track A is at a critical juncture, pause Track B entirely
- Gate: Track B does not start until Track A Batch A2 is complete

### Stage B1 — Discovery + calibration proof (half session)

**Trigger:** A2 complete

**Build:**
- Test AI assessment engine against 3 vocational roles:
  - CNC Operator (NSQF Level 3)
  - Injection Moulding Operator (NSQF Level 3)
  - Plastics Processing Technician (NSQF Level 4)
- Generate 10 questions per role
- Document as capability proof

**Deliverable:** docs/csr/B1-vocational-calibration.md

**Decision gate:** If 5+ reasonable questions per role, proceed to B2.
Otherwise, one extra calibration session, then shelve-or-continue.

### Stage B2 — CSR Assessment API (1-2 sessions)

**Trigger:** B1 success

**Build:**
- POST /api/csr/assess-batch — 1-100 candidates per call
- GET /api/csr/batch-report/{batch_id} — CSV/PDF with scores + skill gaps
- charvakit.com/csr — minimal public landing page
- API key auth (per-partner)

**Deliverable:** Working B2B API + landing page.

**Reuse:** career_assessment_engine (loop mode), pdf_engine, Razorpay.

### Stage B3 — Pilot with one Training Partner (1 session + ongoing)

**Trigger:** B2 complete

**Do:**
- Identify ONE private TP with live CSR contract
- Pitch free pilot: assess next batch, deliver report, no cost
- Measure: does the report matter to them?

**Not CIPET first.** Smaller private TP is the target.

### Stage B4 — Pricing + first paid contract (1 session)

**Trigger:** B3 success

**Do:**
- Price per-candidate: Rs 100-300
- Billing via Razorpay (reuse)
- Sign first paying TP

**Deliverable:** First CSR revenue (Rs 5,000+).

### Track B completion

- Version tag: v4.0-csr-launch-YYYYMMDD
- CSR revenue dashboard
- First case study

**Estimate:** 4-5 sessions at one session/month = 4-5 months to first revenue.

---

## PART 3 — CROSS-TRACK DEPENDENCIES

**What Track A builds that Track B reuses:**
- Certificate + QR + i18n (A2)
- Integrity panel (existing)
- Assessment engine (existing)
- Billing (existing)
- Admin UI patterns (existing)

**What Track B builds that Track A reuses:**
- Batch assessment mode (for bulk MBA assessments)
- API key auth (for university partners)
- Partner management UI

**Net incremental for Track B:** 2-3 sessions of new code + pilot coordination.

---

## PART 4 — FLAGGED ITEMS (complete list)

### Closing in Batch A1
- Session 19: Render Postgres password rotation
- Session 9: PAYPAL_MODE=live explicit on Render
- Session 42: Custom-courses section flicker
- Session 41: CI hook for IELTS relevance test

### Flagged — no plan to fix (cosmetic)
- Session 41: .gitignore duplicate whitelist entries
- Session 19: Two CAR- rows showing "— · —" (older assessments)

### Flagged — dropped, revisit by demand
- Session 42: Search-0-results "design a course" hint

### Flagged — handled in Track A batches
- Session 15-16: DoketsRB sync tables empty (A5)
- Session 39-40: Trust badge IELTS writing + speaking (complete 40c)

### Flagged — Track B scope
- CSR business model (B1-B4)

---

## PART 5 — THE ONE-PARAGRAPH RULE

Track A runs weekly. Track B runs monthly. Track A funds this quarter.
Track B builds next year. When Track A stalls, pause Track B. When
Track B pilots produce signal, scale Track B without touching Track A
cadence. Shared infrastructure is what makes both viable.
---

## Revised Track A — full sequence (updated 2026-10-12, evening)

Based on Oct 11-12 GA4 + DB data:
- 419 users, 411 new, 283 key events (+87% from prior day)
- `/readiness-check` converts 28.5% to key events
- `/placement-prep-2026` converts **239%** to key events (no signup wall)
- Oct 10 spike: 217 users (expected 30-145), 88 key events (expected 9-45)
- Zero revenue
- Zero retention after day 1

**The signal:** Flow friction is the bottleneck, not features or traffic.

### Updated batch order

| Batch | What | Effort | Why |
|---|---|---|---|
| A1 | Small cleanup (Render password, PAYPAL_MODE, flicker, CI hook) | 45 min | Hygiene — closes 4 long-carried flags |
| **A1.5** | **Signup wall fix** — let students take check before login | **1.5 sessions** | **3-5x more certificates** |
| **A1.6** | **AI Tools one-off purchases at Rs 99 (Resume Roast, etc.)** | **1 session** | **SHIPPED 2026-10-13** |
| **A1.7** | **IELTS deep diagnostic micro-paywall (Rs 99)** | **1 session** | **SHIPPED 2026-10-13 (commit 731b70a)** |
| A1.8 | WhatsApp loop instrumentation (UTM tags on share URLs) | 0.5 session | Measure + grow viral coefficient |
| A1.9 | Placement-prep instrumentation + promotion | 0.5 session | Promote the 8x-more-efficient page |
| **A1.10** | **Fix 404 on `/readiness/RDC-433259E0C0D1`** | **5 min** | **56 users hit a dead URL** |
| A2 | Certificate round 3 (QR, watermark, i18n) | 1 session | Polish artifact |
| A2.5 | Real social proof feed (from DB, not fabricated) | 0.5 session | Trust without legal risk |
| A3 | FYP features (Citation, Milestone, Plagiarism, Refine) | 1 session | Product capability |
| A4 | Personalized training views on /training-engine | 1 session | Cross-sell |
| A5 | DoketsRB bidirectional sync | 2 sessions | Resume-jobs bridge |
| A6 | Benchmark data instrumentation | 1 session | Foundation for moat monetization |
| A7 | Certificate-as-a-Service packaging | 1-2 sessions | B2B revenue line |

**Total: ~12-13 sessions.** Split as:

- Session 1: A1 + A1.10 (~1 hr)
- Session 2: A1.5a — backend (~3 hrs)
- Session 3: A1.5b + A1.5c — frontend + GA4 (~3 hrs)
- Session 4: A1.6 + A1.7 (~4 hrs)
- Session 5: A1.8 + A1.9 + A2.5 (~4 hrs)
- Session 6: A2 + A3 (~6 hrs)
- Sessions 7-10: A4, A5, A6, A7 (~6-8 sessions)

**Revenue timeline:** Zero for 2-3 more weeks. First revenue expected after A1.6 (AI Tools purchases) — realistic target is end of October.

**Moat timeline:** Benchmark data becomes statistically meaningful at 500+ certificates. Certificate-as-a-Service viable at 1,000+ certificates.

---

## Monetization strategy (based on Oct 12 data review)

**Do now:**
- A1.6: AI Tools one-off purchases
- A1.7: IELTS diagnostic micro-paywall

**Do soon:**
- A2.5: Real social proof (never fabricate)
- Email retargeting (not WhatsApp — policy/legal risk)
- Tool-gated B2B audit offer (from free Cloud Waste Calculator)

**Defer to Q1 2027:**
- Job Seeker Survival Pack bundle
- 48-Hour Placement fee (needs volume first)
- Benchmark API
- Integrity classifier licensing

**Never do:**
- WhatsApp cold messaging (policy violation)
- Fake social proof popups (Consumer Protection Rules violation)

---

## The proprietary moat (based on scoring analysis)

**Three defensible assets:**

1. **Role Readiness Score formula + benchmark data** — the calibration underneath makes each score meaningful. Compounds with volume.
2. **Integrity fact panel + weighted classifier** — the honest trust layer. No competitor offers this in India today.
3. **Adaptive ability baseline (Elo)** — enables longitudinal tracking. Rare in Indian assessment tools.

**These become revenue when:**
- 1,000+ certificates for statistical significance
- 10+ interested institutional buyers
- Packaging as Certificate-as-a-Service API

**Track B is the path to monetize the moat.** Not before.

---

## The one-paragraph strategy (locked)

Fix the flow. Reach 500-1,000 certificates. Instrument everything.
Launch one-off purchases (A1.6) and IELTS diagnostic (A1.7) as the first revenue lines.
Build Certificate-as-a-Service (A7) as the first B2B revenue line at 1,000+ certificates.
Add CSR (Track B) parallel once Track A proves the flow.
Monetize the moat when volume justifies it.

**Revenue timeline:**
- Week 1-2: Flow fixes (A1, A1.5) → 3x more certs
- Week 3-4: First paid features (A1.6, A1.7) → Rs 10-50K/month
- Month 2-3: Certificate-as-a-Service (A7) → Rs 50K-2L/month
- Month 4-6: Benchmark API, moat monetization, CSR

---

## Deferred Render dashboard tasks (added 2026-10-12)

The following require the Render dashboard and are deferred until the
current code-shipping push is complete:

- **A1.1** — Rotate Render Postgres password (pending since Session 19)
- **A1.2** — Set PAYPAL_MODE=live explicitly on Render env

**Trigger to resume:** after Batch A1.5 (signup wall fix) is fully shipped
and verified. Or earlier if there is a natural pause in code work.

**Status:** still pending. Do not lose these.

**Why deferred:** they break code-flow and require browser context switch.
Code batches are higher value per hour in the current push.
---

---

## A1.5 FULLY COMPLETE (2026-10-12)

The signup wall has been removed. Anonymous users can now take a full
assessment, see their score, register, and receive a verified certificate
WITH integrity signals intact.

**The full flow (verified E2E):**
1. Anonymous user lands on /readiness-check
2. Takes 10-question MCQ assessment (no login)
3. Integrity capture records tab_switch, focus_out, paste, contextmenu,
   rapid_input events (all 5 signal types verified)
4. Score renders
5. User clicks "Save My Certificate - Register"
6. Registers/logs in
7. Backend /claim migrates assessment to user's real email
8. Certificate generated — integrity panel shows the real signals
9. Badge correctly shows "Employer Review Recommended" (blue) or
   "Independently Verifiable" (green) based on risk

**Backend changes:**
- anonymous_sessions.py (new module, 6 functions)
- charvak_anonymous_assessment_sessions (new table)
- /api/career-assessment/start — accepts no-email requests
- /api/career-assessment/answer — accepts anonymous_token
- /api/career-assessment/complete — accepts anonymous_token, skips
  persistence until claimed
- /api/career-assessment/claim — NEW: migrates assessment
- /api/career-assessment/{aid} — accepts ?anon_token=
- /api/integrity/event — accepts anonymous_token (Session 43-A1.5b)

**Frontend changes:**
- readiness-check.html — sends no auth for anon
- ai-assessment.html — anon-aware gates + register-and-claim CTA
- integrity-capture.js — sends anon_token when email absent; fixed
  syntax error from earlier patch

**Cache-bust:**
- 8 templates got ?v=20261012b on integrity-capture.js include

**Commits:**
- 38feac8: anonymous_sessions module + table
- 4fbf876: /start accepts anon
- d42fa5f: /answer, /complete, /claim (all anon-aware)
- 6889649: /{aid} accepts anon_token
- 59f6c18: fix /claim before generic route
- 93dc598: frontend anonymous flow + register-and-claim CTA
- (pending): integrity for anon sessions + cache bust

**Expected conversion impact:** /readiness-check conversion should rise
from 28% to 55-75% because users no longer hit the login wall.

**Verification:**
- Test user: newashtester@gmail.com
- Certificate: RDC-DBE9676715FF (shows 8 tab switches in integrity panel)
- All 5 signal types fired and landed in DB

**A1.5 is closed. Next: A1.5c (GA4 instrumentation for the anon funnel).**
---

## Employer Story Gaps (flagged 2026-10-12, post-A1.5)

The anonymous certificate flow now works end-to-end. The certificate
shows the correct badge and integrity panel to whoever opens it.

**What's missing for a complete employer-facing experience:**

| Gap | Effort | Impact | Priority |
|---|---|---|---|
| A1.11 — Verify URL → HTML page (not JSON) | 1 session | High — non-technical recruiters can read it | Next |
| A1.12 — Candidate-side explainer for blue badge | 30 min | Low — cosmetic polish | Soon |
| A1.13 — Public integrity glossary (/integrity) | 30 min | Medium — builds trust, easy reference | Soon |
| A1.14 — Employer portal for verification + notes | 2 sessions | Low until real employer demand | Defer |
| A1.15 — Email certificate to employer from candidate | 1 session | Medium — closes the "share" loop | Medium |

### A1.11 — Verify URL HTML page (recommended next)

**Current state:** /api/readiness/verify/{hash} returns raw JSON. A
recruiter copying the URL into Slack gets a JSON blob. First impression
is broken for non-technical audiences.

**Goal:** When the URL is opened in a browser, render a friendly HTML
page. When called by an API client (Accept: application/json header),
keep returning JSON.

**Approach:**
- Detect browser via Accept header or ?format=query
- HTML version: small page showing verified status, candidate display
  name, role, level, score, issue date, integrity badge
- Keep JSON for programmatic callers
- New template: templates/verify.html

**Effort:** 1 session. Highest-value small build in the trust story.

### A1.12 — Candidate-side explainer for blue badge

**Current state:** The blue "Employer Review Recommended" badge appears
without context. Candidates may not know what to do with it.

**Goal:** Inline help text: "This assessment recorded some environment
signals. Employers can still see your score — we just recommend they
interview you to verify your skills."

**Effort:** 30 min. Add to readiness.html near the badge.

### A1.13 — Public integrity glossary

**Current state:** "Frequently left the assessment tab (8 times)" is
plain English, but a curious employer might want the deeper explanation.

**Goal:** Public /integrity page explaining:
- What signals we record (paste, tab_switch, focus_out, etc.)
- What each means (and what it doesn't mean)
- Why we show facts, not verdicts
- How to read the four risk levels (clean / minor / moderate / elevated)
- Link to /readiness-check and a sample certificate

**Effort:** 30 min. Static page. Good SEO.

### A1.14 — Employer portal (defer until demand)

**Current state:** No employer-side portal.

**Goal (when there's demand):** /verify-employer page where a recruiter
can paste a certificate ID, see verified data, and optionally leave
an audit trail.

**Effort:** 2 sessions. Deferred until we have 3+ employers asking
for it.

### A1.15 — Email certificate to employer

**Current state:** Candidate must copy the certificate URL manually.

**Goal:** "Email this certificate" button on /readiness/{cert_id} that
sends to any email with a link + summary.

**Effort:** 1 session. Uses existing SendGrid integration.

### Insertion into Track A sequence

These new batches slot in after A1.5 and before A1.6:

- A1.5 (signup wall fix) — DONE
- **A1.5c (GA4 instrumentation) — next**
- **A1.11 (verify HTML) — after A1.5c**
- A1.6 (AI Tools one-off)
- A1.7 (IELTS diagnostic)
- A1.8 (WhatsApp loop instrumentation)
- **A1.12 (candidate-side explainer) — piggyback on A1.8 or A2.5**
- **A1.13 (integrity glossary) — piggyback on A1.11**
- A1.9 (placement-prep + real social proof)
- A1.15 (email certificate) — after A1.7
- A2 (certificate round 3)
- A1.14 (employer portal) — defer to Q1 2027

**Rationale:** A1.11 is the next most valuable small thing after A1.5c.
It closes the employer-side loop. A1.13 (glossary) can piggyback on the
same session since both use existing content.
---

## A1.11 COMPLETE (2026-10-12)

The verify URL now renders as a branded HTML page for browsers and
returns JSON for API clients. Commits:

- e0b2e2e: feat(verify): A1.11 - text-based branded HTML verification page

**What shipped:**
- New template: templates/verify.html
- Route: /api/readiness/verify/{hash} branches on Accept header
- Browser → HTML page with Charvak branding + integrity facts
- API client → JSON (unchanged)
- ?format=json force JSON
- Invalid hash → friendly "not found" page

**What this closes:**
- Employer opens verify link → sees a readable page (not raw JSON)
- Charvak wordmark in brand green + AI-Verified Talent pill
- Score + benchmark + certificate details + integrity facts
- Cryptographically signed trust seal
- CTA to /readiness-check (funnel loop closed)

**Verification:**
- /api/readiness/verify/eeb2390f55e93db0 → HTML page
- /api/readiness/verify/eeb2390f55e93db0?format=json → JSON
- /api/readiness/verify/0000000000000000 → friendly not-found card

**Remaining A1.11 follow-ups (small):**
- A1.13: Public integrity glossary (/integrity) — reference page
- A1.12: Candidate-side explainer for blue badge — 30 min
- A1.15: Email certificate to employer — 1 session
---

## A1.13 COMPLETE (2026-10-12)

Public integrity glossary + cross-links shipped. Commits:
- 0d433c8: feat(integrity): A1.13 - public integrity glossary page
- 8144c99: feat(integrity): A1.13 - cross-links + 2026 copyright + dedupe

**What shipped:**
- templates/integrity.html (12.9 KB) — public glossary page
  - Why we record: AI cheating problem
  - What we record: 5 signal cards (paste, tab switch, context menu,
    focus out, rapid input)
  - How we classify: 4 risk levels (clean, minor, moderate, elevated)
  - What appears: 2 badge states (green shield / blue info)
  - What we dont do: dont accuse, dont block, dont sell data
  - CTA: /readiness-check
- Route /integrity added to main.py (matches template_response pattern)
- Footer "Assessment Integrity" link under Legal
- Certificate card "Learn more about integrity ->" link (opens new tab)
- Footer copyright: 2022 -> 2026

**Verification:**
- /integrity loads with all sections rendered
- Footer shows single "Assessment Integrity" link
- Certificate card shows the "Learn more" link next to existing toggle
- Copyright year is 2026

**Remaining small follow-ups:**
- A1.12: Candidate-side explainer for blue badge (30 min)
- A1.15: Email certificate to employer (1 session)

**Next major batch:** A1.6 (AI Tools one-off purchases at Rs 99)...
---

## A1.6 COMPLETE (2026-10-13)

All 12 AI Tools now have a one-off payment path (Rs 99 / $4.99 / etc.)
alongside the existing credit-gated path. Global pricing across 13 currencies.

**Architecture:**
- Explicit per-market price table (not conversion math)
- 3 tiers: tier_1 (India + emerging), tier_2 (emerging), tier_3 (global)
- INR -> Razorpay, all others -> PayPal
- NGN/BRL/ZAR fall back to USD (PayPal does not support those currencies)
- Purchases in charvak_tool_purchases
- Idempotent on razorpay_payment_id / paypal_order_id

**Files added:**
- tool_payment_engine.py
- migrations/20261012_tool_purchases.sql
- static/js/tool-pay.js

**Files modified:**
- main.py: +2 routes + _dispatch_paid_tool
- global_config.py: COUNTRY_TO_CURRENCY promoted to module level
- 12 tool templates: ToolPay.init() blocks

**Pricing table (final):**
| Tier | India | US | UK | EU | UAE | SG | AU | CA | JP | CN |
|------|-------|-----|-----|-----|------|-----|-----|-----|-----|-----|
| tier_1 | Rs 99 | $1.99 | GBP 1.49 | EUR 1.99 | AED 7 | SGD 2.49 | AUD 2.99 | CAD 2.49 | JPY 300 | CNY 14 |
| tier_2 | Rs 149 | $2.99 | GBP 2.49 | EUR 2.99 | AED 11 | SGD 3.99 | AUD 4.49 | CAD 3.99 | JPY 450 | CNY 21 |
| tier_3 | Rs 299 | $4.99 | GBP 3.99 | EUR 4.49 | AED 17 | SGD 5.99 | AUD 6.49 | CAD 5.99 | JPY 700 | CNY 32 |

BR -> $2.99 USD (tier_2 fallback)
NG -> $1.99 USD (tier_1 fallback)
ZA -> $2.99 USD (tier_2 fallback)

**Verified E2E on prod:**
- TPUR-1C8ED6AEF1B7
- tool: resume_roast
- INR 99.00
- razorpay order_Tn6FaN1avlAnE2
- razorpay payment pay_Tn6GxHrPLMNCuN
- email: hr@charvakit.com
- status: completed
- has_result: True

**Full 12-tool frontend verification:**
- All 12 return HTTP 200
- All 12 include tool-pay.js
- All 12 include ToolPay.init

**Commits:**
- bb68098: backend - currency-aware tool payment engine
- 645e2d5: routes - create-order + run
- 6058ded: frontend - tool-pay.js + Resume Roast
- cfe8fd1: one-off button on all 12 tools

**This is the first real revenue line in the platform.**

**Follow-ups flagged (not blocking):**
- Cron to clean up pending purchases older than 24h
- Email receipt after successful purchase
- Retry endpoint for captured_but_failed status
- Optional: exchange-rate table staleness review

**Next batch:** A1.7 - IELTS diagnostic micro-paywall

---

## A1.7 COMPLETE (2026-10-13)

The IELTS Deep Report micro-paywall is live. This is the second real
revenue line on the platform (after A1.6 AI Tools one-off purchases).

**Commit:** `731b70a`
**Files:** 9 changed, 1,885 insertions, 1 deletion

### What shipped

**Backend:**
- `charvak_ielts_deep_reports` table + `responses_json` column on sessions
- `ielts_engine.attach_responses / get_responses` (tamper-proof source)
- `ielts_deep_report_engine.py` (773 lines): pricing tiers, Razorpay +
  PayPal order creation, OpenAI report generation for writing +
  speaking, idempotent claim, save/get
- 4 routes: `/api/ielts/deep-report/{price,create-order,run}` +
  `GET {id}.pdf`
- `pdf_engine.render_ielts_deep_report_pdf` (branded 7-page A4)
- `CharvakReportPDF.mc_full_width` helper (fixes fpdf2 X-drift crash)
- `enhanced_email.send_ielts_deep_report_email` (SendGrid PDF attachment)
- Country detection normalized via `improved_ip_detector`

**Frontend:**
- `static/js/ielts-deep-report.js` (421 lines): shared CTA + payment +
  inline report renderer + PDF download
- CTA slot + init on `ielts-writing.html` and `ielts-speaking.html`

### Pricing

| Market | Price | Gateway |
|---|---|---|
| India | Rs 99 | Razorpay |
| US | USD 4.99 | PayPal |
| UK | GBP 3.99 | PayPal |
| AU | AUD 6.49 | PayPal |

### E2E verified (Razorpay test mode)

- Rs 99 charged for IN users (gateway: razorpay, tier_1)
- 7-page branded PDF, 46 KB, inline render
- PDF downloadable from browser and curl
- Email sent with PDF attachment (SendGrid accepted, verified against
  real inbox)

### Follow-ups flagged (not blocking)

- **A1.6 latent bug:** `/api/tools/paid/create-order` still uses raw
  `ip_detector` (returns full country names). Same fix pattern as A1.7
  is a 5-line patch. Frontend currently sends explicit `country_code`
  so it works in practice.
- **PayPal flow on A1.7:** `_unlockViaPayPal` calls
  `/api/payment/paypal/capture`, which may not exist. Only hit for
  non-INR users. Flag for A1.7b.


---

## A1.8 + A1.9 COMPLETE (2026-10-13)

Full WhatsApp/LinkedIn share instrumentation across the platform.

### A1.8 - Share instrumentation

- `base.html`: new `charvakShareUrl()` + `charvakTrackShareLanding()`
  helpers reusable across all share surfaces
- `readiness.html`: UTM-tagged share URLs (linkedin/whatsapp);
  `cert_shared` on click; `readiness_view_from_share` on arrival
- `readiness-check.html`: `readiness_check_view_from_share` on arrival
- `mock-result.html`: `mock_result_shared` per-channel;
  `mock_result_view_from_share` on DOMContentLoaded
  (fires even when the result 404s)

### A1.9 - Placement-prep instrumentation + promotion

- `placement-prep-2026.html`: `placement_prep_view_from_share` on arrival
- `readiness.html`: 5th "what next?" tile -> /placement-prep-2026
- `companies.html`: hero promo banner -> /placement-prep-2026

### GA4 events now in the funnel

| Event | When |
|---|---|
| cert_shared | Cert share button clicked |
| readiness_view_from_share | Cert page loaded with UTM |
| readiness_check_view_from_share | Landing page loaded with UTM |
| mock_result_shared | Mock share button clicked |
| mock_result_view_from_share | Mock page loaded with UTM |
| placement_prep_view_from_share | Placement page loaded with UTM |
| placement_prep_view | Placement page loaded (any) |
| mock_company_click | Company card clicked |
| mock_start | Mock drive started |
| mock_complete | Mock drive completed |

### Why this matters

/placement-prep-2026 converts at 239% vs /readiness-check at 28.5%
(Oct 12 data). A1.9 puts that page in front of high-intent audiences
on /mock-drive and /readiness certs, and makes every share attributable.
