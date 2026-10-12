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
| A1.6 | AI Tools one-off purchases at Rs 99 (Resume Roast, etc.) | 1 session | New revenue line, impulse-buy |
| A1.7 | IELTS deep diagnostic micro-paywall (Rs 99) | 1 session | Higher revenue per user |
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
