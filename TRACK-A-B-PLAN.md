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