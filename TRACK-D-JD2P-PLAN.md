# TRACK D — Job-Description-to-Placement (JD2P)

**Created:** 2026-10-13
**Status:** Flagged, not started
**Trigger:** After Amrita pilot is running (Week 2, Nov 2026)
**Strategic priority:** HIGH — this is the closing of the user journey

---

## Why This Exists

The current platform offers:
- Career Assessment (106 roles × 66 industries × 7 levels)
- Mock drives (18 companies, real patterns)
- Courses (catalog + AI designer)
- Certificates (verifiable)

Every piece works. But the journey has a gap: the user has to *choose*
which assessment to take. The platform doesn't' t take the user's target
job and design the assessment for them.

**JD2P closes that gap.** The user pastes a job description. The AI
designs an assessment that mirrors that specific job's interview. The
user takes it, sees where they stand, closes the gaps, and walks into
the interview ready.

---

## The User Journey
Paste JD → AI parses → AI designs assessment → User takes it
→ Diagnostic (score vs JD, gaps) → Learning path (catalog or custom)
→ Practice → Retake → Prove → GET PLACED

text

**The metric that matters:** placements, not enrollments.

---

## What Exists Today (Foundation)

| Component | Status |
|---|---|
| Career Assessment engine (role × industry × level) | ✅ Live |
| Multi-format assessments (mcq, coding, sql, system_design, case_study, behavioral, short_answer, numeracy, situational_judgment, debugging) | ✅ Live |
| AI-generated questions | ✅ Live |
| Section + topic diagnostic | ✅ Live (B1) |
| AI explanation of wrong answers | ✅ Live (B2) |
| Skill gap → course recommendation | ✅ Live (B1) |
| AI Course Designer | ✅ Live |
| Verifiable certificates | ✅ Live |
| Shareable verify URL | ✅ Live (A1.11) |

## What Does Not Exist

| Component | Effort |
|---|---|
| JD parser (paste → structured JSON) | 1 session |
| Assessment designer (structured JD → format/topic/difficulty selection) | 1 session |
| Score normalizer (user score vs JD benchmark) | 0.5 session |
| Frontend `/jd-assessment` flow | 1 session |
| Per-user progression dashboard | 1 session |
| Placement outcome recording (did they get placed?) | 1 session |
| Success attribution reporting | 0.5 session |

**Total Track D effort:** ~6-7 sessions (~4 weeks of focused work).

---

## Phase Breakdown

### Phase A — JD2P Engine (2-3 sessions)

| # | Build | Effort |
|---|---|---|
| D-A1 | `jd_parser_engine.py` — parse a pasted JD into structured data | 1 session |
| D-A2 | `jd_assessment_designer.py` — design formats/topics/difficulty | 1 session |
| D-A3 | `jd_fit_report.py` — score vs JD benchmark | 0.5 session |
| D-A4 | Frontend `/jd-assessment` — paste → design → take → report | 1 session |

**Deliverable:** user can paste a JD and take a calibrated assessment.

### Phase B — MBA-relevant patterns (before Thursday)

| # | Build | Effort |
|---|---|---|
| D-B1 | BA patterns for Deloitte, KPMG, EY, PwC | 45 min |
| D-B2 | BA patterns for TCS, Accenture, Capgemini | 30 min |
| D-B3 | Extend TOPIC_TO_COURSE | 15 min |
| D-B4 | Migration file for 10 MBA courses | 15 min |
| D-B5 | Promote 4 AI courses to public | 10 min |
| D-B6 | Update deck slides 5-7 | 1 hr |

### Phase C — Progress + outcomes (2 sessions)

| # | Build | Effort |
|---|---|---|
| D-C1 | Per-user progression dashboard (score over time) | 1 session |
| D-C2 | Placement outcome tracking | 1 session |
| D-C3 | Success attribution reporting | 0.5 session |

### Phase D — Lateral hiring (future)

| # | Build | Effort |
|---|---|---|
| D-D1 | JD parser supports years-of-experience as primary input | 0.5 session |
| D-D2 | Domain-specific patterns (backend, data, cloud, security) | 2-3 sessions |
| D-D3 | Senior/Staff/Principal calibration | 1 session |

---

## Design Decisions to Make

1. **Where does JD2P live?**
   - Recommendation: new route `/jd-assessment` — the flagship entry point
   - Also integrate as a mode on `/readiness-check` (option: "I have a JD")

2. **Is JD2P free or paid?**
   - Recommendation: **free for the first assessment per user per JD.** Paid for retakes and for the deep report.
   - Free tier: parse + design + take + basic diagnostic
   - Paid tier (Rs 99): deep report + AI explanations + learning path

3. **Does JD2P replace Career Assessment or complement it?**
   - Complement. JD2P is the top-of-funnel. Career Assessment becomes the "I don't have a specific job in mind" path.

4. **Should JD2P have a "Save this JD" feature?**
   - Yes. Users apply to many jobs. They should have a list of "JDs I'm tracking."

5. **Should JD2P feed into the university dashboard?**
   - Yes. When a CDC coordinator loads 100 student JDs, they see "42 students are targeting Deloitte, 12 targeting Swiggy, 8 targeting Amazon." That's a real signal for placement planning.

---

## Success Metrics (Track D)

| Metric | Target |
|---|---|
| JDs parsed | 100/month by Month 3 |
| Assessments completed via JD2P | 60/month by Month 3 |
| Gap closure rate | 40%+ of users show improvement on retake |
| Placement attribution | 10%+ of users report placement within 90 days |

---

## The One-Line Pitch

> "Paste a job description. Get an assessment that mirrors that exact job's interview. Close your gaps. Get placed."

---

## Why This Matters Strategically

Every competitor does one thing:
- HackerRank: coding tests
- TestGorilla: assessment library
- Knovia: role readiness scoring
- Snyk: code security

None of them do **JD-specific assessment design.** They all ask the user to
choose from a catalog. We're saying: **bring your target job. We'll design
the test.**

That's a category of one. And it's the closing of the Local-to-Global
talent journey we've been building for.

---

## Trigger to Start

- Amrita pilot Week 2 data shows users want more specific prep
- OR a paying customer requests JD-specific assessment
- OR Track A completes with headroom

**First priority after Track A + Track C launch.**

---

**Keep this file in sync. This is the strategic arc of the platform.**

## Session 2026-10-19 — Split into Buildable + Blocked Phases

**Decision:** Don't build all 6-7 sessions of JD2P blindly. Split into
two phases:

### Phase A — BUILD NOW (no Amrita dependency, 3 sessions)

Three components, all reusable even if Amrita says no or goes silent:

| # | Item | Effort | Value even without Amrita |
|---|---|---|---|
| A | JD parser engine (`jd_parser_engine.py`) | 1 session | Reusable for any customer with a JD (job boards, recruiters, LinkedIn) |
| B | Standalone `/jd-assessment` MVP (paste → parse → show structured data) | 1 session | Proof-of-concept demo asset for Amrita, employers, recruiters |
| C | Wiring into existing Career Assessment (JD → prepopulate role/industry/level) | 1 session | Faster flow for any user with a JD |

**Effort: ~3 sessions (planned sessions 55, 56, 57).**
**No dependency on Amrita. No wasted work — the parser serves
everyone, not just Amrita.**

### Phase B — BLOCKED until Amrita pilot Week 2 data

Five items that need real user data to build correctly:

| # | Item | Why wait |
|---|---|---|
| D | Assessment designer (JD → formats/topics/difficulty) | Needs Amrita's actual format requirements |
| E | Score normalizer (user vs JD benchmark) | Needs real user benchmark data |
| F | Progression dashboard | Needs users with ≥2 assessments |
| G | Placement outcome recording | Needs real placements |
| H | Success attribution | Needs placement data across a cohort |

**Trigger to unblock Phase B:**
- Amrita pilot Week 2 data shows users want specific prep → proceed
- OR 5+ days of no Amrita response → Phase B stays blocked, but Phase A
  is live and serving users independently

### Session Plan

| Session | What | Status |
|---|---|---|
| 55 | JD parser engine (`jd_parser_engine.py`) | NEXT |
| 56 | `/jd-assessment` MVP (frontend-only, no new tables) | Pending |
| 57 | Wire JD parser into Career Assessment flow | Pending |
| TBD | Phase B items (D-H) | Blocked on Amrita signal |

### Design Principles for Phase A

- **Reusable core first:** JD parser serves any user, not just Amrita
- **No new tables for MVP:** the parser is a function, not a database
- **Demo-ready:** at the end of Session 56, you can paste any JD and
  show structured extraction
- **Stronger Amrita pitch:** "we already built the parser" is better
  than "we could build it if you want"

---

## Session 2026-10-19 (evening) - Track D Phase Split Flagged

**Decision:** Don't wait for Amrita to start Track D. Split into buildable
and blocked phases.

**Build now (Sessions 55-57, ~3 sessions):**
- A: JD parser engine (`jd_parser_engine.py`) — Session 55
- B: `/jd-assessment` MVP (paste → parse → show structured data) — Session 56
- C: Wire JD parser into Career Assessment dropdowns — Session 57

**Blocked on Amrita (no session scheduled):**
- D-H: Assessment designer, score normalizer, dashboard, outcomes,
  attribution

**Rationale:** JD parser is genuinely reusable (job boards, recruiters,
LinkedIn) and works even if Amrita says no. The 3-session MVP is the
lowest-risk buildable slice of Track D. Serves as a stronger Amrita
demo than a promise.

**Full phase split:** See TRACK-D-JD2P.md "Session 2026-10-19 — Split
into Buildable + Blocked Phases"

**Session 55 candidates (revised):**
1. **JD parser engine** (Track D Phase A, item A) — RECOMMENDED
2. Phase 3c GPT-4o-mini env flip — target Nov 3
3. Certificate i18n (Hindi + Telugu) — 1-2 hrs
4. Employer Dashboard → support JD extraction from passport

**Remaining flags: 1**
- Render Postgres password rotation (Session 19, ~30 sessions, 5-min)

