# KAMPHIRE COMPETITIVE ANALYSIS — FLAGGED FOR LATER BUILD

**Flagged:** 2026-11-03
**Status:** NOT STARTED — demand-triggered
**Effort:** ~14-18 sessions if all gaps built (do NOT build speculatively)
**Trigger:** See "Trigger to Build" section below

---

## THE STRATEGIC POSITION

KampHire is a B2B campus recruitment automation + assessment platform
by Assiduous Infotech Private Limited (Ahmedabad, Gujarat). Positioned
as "Campus Recruitment Software Built for High-Volume Fresher Hiring."

**Different buyer, different user, different product:**
- KampHire: corporate HR / TA lead at scale (200+ hires/year)
- Charvak: CDC directors + students + employers
- KampHire: recruiter-side screening (candidates don't keep results)
- Charvak: candidate-side proof (candidates own their certificates)

KampHire solves the enterprise recruiter's problem.
Charvak solves the college student + CDC director + employer problem.

**Different products serving different buyers** — but they overlap in
one place: the assessment engine, especially for CEFR English and
technical coding.

---

## KAMPHIRE AT A GLANCE

**4 verticals:**
1. Campus Hiring Automation (outreach, branded registration, bulk
   registration, smart shortlisting, integrated assessments, interview
   coordination, offer communication)
2. English Language Assessments (voice/non-voice, CEFR A1-C2, typing/chat,
   customer support, sales)
3. Developer Hiring (MCQ + coding, 400+ templates, 5000+ question bank,
   7 tech-stack tracks)
4. BPO / Call Center Hiring (voice process, chat support, typing accuracy)

**Claims (unverifiable):**
- 45+ domain test types
- 350+ campuses covered
- 30,000+ registrations/assessments (single case study)
- 20,000+ AI interviews conducted
- 1,200+ candidates interviewed
- 4.8 rating (single testimonial — Loginsoft Infotech)
- 2-year customer retention (Loginsoft)

**Tech indications:**
- AI video interviews for communication
- CEFR-aligned English scoring
- AI proctoring / remote assessments
- ATS integration
- Question randomization
- 5000+ question bank + 400+ templates

---

## WHERE KAMPHIRE IS STRONGER

1. Campus hiring workflow automation (full lifecycle)
2. Branded registration pages per company
3. Bulk registration + eligibility-based smart shortlisting
4. Interview coordination + panel management
5. Offer communication automation
6. Multi-campus management (350+ campuses in one drive)
7. ATS integration (explicit)
8. AI video interview (core feature, 20K+ interviews)
9. AI proctoring
10. CEFR English scoring (A1-C2, production quality)
11. Voice/chat/typing assessment (all three)
12. 400+ ready-to-use assessment templates
13. Scale claimed (350+ campuses, 20K+ AI interviews)

---

## WHERE CHARVAK IS STRONGER

1. HMAC verifiable certificates (KampHire has none)
2. Public verify URL (/readiness/{id})
3. Candidate-owned proof (candidates keep their cert)
4. 5-layer abuse protection (attempts + identity + rotation + multi-account + expiry)
5. JD-specific calibration with honest 91% coverage
6. Micro-internships with escrow
7. FYP Assistant (unique)
8. AI Tutor (persistent chat)
9. Dean/Proof Dashboard (PDF report)
10. Career Passport (public profile)
11. Multilingual (34 global + 12 Indian languages)
12. Interview Prep (conversational + adaptive)
13. Assessment depth (10 formats vs KampHire's 3)

**Score: Charvak wins 12 of 28, KampHire wins 12 of 28, 4 ties.**
This is the closest competitor so far — real product, real traction,
but fundamentally different buyer.

---

## THE 6 REAL GAPS (Ranked by ROI)

### Gap 1 — Campus Hiring Workflow Automation (3 sessions)

**What KampHire has:** Complete recruitment automation — branded
registration → bulk upload → smart shortlisting → interview scheduling
→ panel management → offer communication.

**What Charvak has:** Assessment + recruiter dashboard. No workflow.

**What's needed (per INVERTED-MARKETPLACE-FLAG.md):**
- Session 102: Candidate dashboard (candidate-side)
- Session 103: JD → Shortlist (recruiter-side)
- Session 104: Notification engine (scheduling + offer automation)

**Effort:** 3 sessions (already documented)
**Trigger:** First employer or CDC says "I need to manage my whole
hiring drive in Charvak"
**ROI:** Turns Charvak into a workflow tool

### Gap 2 — CEFR English Assessment (2-3 sessions)

**What KampHire has:** CEFR A1-C2 scoring across voice, video, typing,
chat. Automated screening that sends C1-C2 candidates to HR.

**What Charvak has:** IELTS (band 1-9), Versant (5 criteria). Both
English, neither CEFR-aligned for general workplace English.

**What to build:**
- CEFR mapping layer (reuse IELTS/Versant AI scoring)
- Typing speed + chat simulation
- Read aloud / talk about yourself / describe a chart exercises
- Auto-screening with CEFR rating per candidate

**Effort:** 2-3 sessions (reuses IELTS + Versant infrastructure)
**Trigger:** First BPO or customer support client asks for English assessment
**ROI:** Opens the BPO / call center market (Rs 50K-5L per deal)

### Gap 3 — AI Video Interview (3-4 sessions)

**What KampHire has:** "AI-powered video interviews for communication
assessment." Core feature. 20K+ AI interviews conducted.

**What Charvak has:** Text-based Screen Agent. No video.

**What to build (do NOT build full video proctoring):**
- Browser webcam recording (MediaRecorder API)
- 3-5 questions per candidate
- Whisper transcription (already available)
- AI scoring for content + communication (reuse Versant)
- Recruiter dashboard to review

**Effort:** 3-4 sessions
**Trigger:** First employer says "can we do video screening?"
**ROI:** Matches KampHire's AI interview without a full ATS

### Gap 4 — Ready-to-Use Assessment Templates (1-2 sessions)

**What KampHire has:** 400+ ready-to-use assessment templates.

**What Charvak has:** Every assessment generated from scratch. No
pre-built templates.

**What to build:**
- 20-30 curated templates per common role:
  - Frontend Engineer (React) — MCQ + coding
  - Data Analyst — MCQ + SQL + short_answer
  - Customer Support (English) — CEFR + typing
  - Business Analyst (MBA) — MCQ + case study
- Pre-seeded sample questions
- "Start from template" button on /ai-assessment

**Effort:** 1-2 sessions (mostly content authoring)
**Trigger:** First user says "I want a standard test, not a custom assessment"
**ROI:** Cuts assessment launch time from 5 min to 30 seconds

### Gap 5 — Bulk Registration + Smart Shortlisting (1-2 sessions)

**What KampHire has:** CSV upload of 500 candidates → auto-filter by
CGPA/branch → auto-shortlist.

**What Charvak has:** One-by-one registration. Manual filtering.

**What to build:**
- CSV upload endpoint (some infra exists per TRACK-C C6)
- Eligibility filter UI (CGPA range, branch, year, backlogs)
- "Shortlist matching candidates" button
- Bulk invite to assessments

**Effort:** 1-2 sessions
**Trigger:** First CDC requests bulk operations
**ROI:** Makes platform usable for drives above 50 candidates

### Gap 6 — Branded Registration Page Per Drive (2 sessions)

**What KampHire has:** "Company-branded registration pages" — each
drive has its own URL with client's logo/colors.

**What Charvak has:** One generic registration flow.

**What to build:**
- /drive/{drive_id} route with company name, logo, colors
- Leverages existing white-label engine (per B2 Co-Branding Engine
  in INSTITUTIONAL-ROADMAP)
- Configurable via admin UI
- Post-registration, candidates land in that drive's assessment

**Effort:** 2 sessions
**Trigger:** First employer asks "can this be branded to us?"
**ROI:** Makes enterprise deals feel custom without custom engineering

---

## THE 5 MOATS CHARVAK HAS AGAINST KAMPHIRE

### Moat 1 — Candidate owns their certificate

KampHire results go to the recruiter. Candidate owns nothing.
Charvak certificates are HMAC-signed, owned by candidate, verifiable
forever.

**Pitch:** "KampHire tests your candidates. Charvak tests AND equips
them. When they leave your drive, they leave with a certificate they
can share with anyone."

### Moat 2 — Assessment depth (10 formats vs 3)

KampHire: MCQ + coding + AI video interview.
Charvak: MCQ + coding + SQL + system_design + behavioral + case_study +
short_answer + numeracy + situational_judgment + debugging.

For roles that need more than a test — Business Analyst, Product
Manager, HR, Consulting — Charvak assesses; KampHire can't.

### Moat 3 — College-side relationship (CDC director, not recruiter)

KampHire sells to corporate HR. CDC is a supplier in their model.
Charvak sells to the CDC director as a primary customer.

**Pitch:** "KampHire is a tool for companies hiring from your campus.
Charvak is a tool for YOUR campus."

### Moat 4 — Micro-internships with escrow

KampHire is assessment → hire. No trial period.
Charvak is assessment → micro-internship (paid, escrow) → hire.
Candidate proves themselves with real work before the offer.

**Pitch:** "KampHire screens. Charvak screens + trials. When you hire
from us, you've already seen them deliver real work."

### Moat 5 — Zero-cost B2C side

KampHire is B2B only. All 500 students must go through employer's drive.
Charvak lets students self-serve — take free readiness check, prove
skills, apply to jobs. Funnel that feeds employers free verified
candidates.

**Pitch:** "KampHire screens a fixed pool. Charvak keeps building the
pool — thousands of students self-verify on their own time, then enter
your pipeline already proven."

---

## THE STRATEGIC MOVE

**Do NOT build a KampHire clone.** They have 2-3 years of workflow
automation, 350+ campuses, 20K+ AI interviews. You'd be building
catch-up.

**Instead, position Charvak as the missing layer:**

> "KampHire replaces your recruitment workflow. Charvak plugs into it
> — or sits alongside it. We're the proof layer: certified, HMAC-signed,
> candidate-owned, verifiable anywhere. Your candidates come out of
> Charvak verified. Send them to KampHire, Greenhouse, Lever, or any
> ATS. The proof travels with them."

This lets you sell to the same buyers (enterprise HR) without competing
directly on workflow.

---

## RANKED BUILD ORDER (WHEN TRIGGERED)

| # | Action | Effort | Trigger |
|---|---|---|---|
| 1 | Rotate Render password | 2 min | NOW |
| 2 | Send Amrita follow-up #1 | 5 min | NOW |
| 3 | Send candidate emails | 45 min | NOW |
| 4 | 20-30 assessment templates | 1-2 sessions | Next build session |
| 5 | CEFR English mapping | 2-3 sessions | After first BPO ask |
| 6 | AI video interview | 3-4 sessions | After first video ask |
| 7 | Bulk registration + shortlist | 1-2 sessions | After first CDC ask |
| 8 | Campus workflow automation | 3 sessions | After first enterprise ask |
| 9 | Branded registration | 2 sessions | After first employer ask |

**Total if ALL built:** ~14-18 sessions.
**Total likely to be built:** 3-6 sessions (items 4, 5, 6).

---

## WHY THIS IS FLAGGED, NOT BUILT

- 0 paying customers
- 3 pilots (not 350 campuses)
- 674 users (not 20K+ AI interviews)
- KampHire has 2-3 years of workflow automation lead
- Building a KampHire clone would take 14-18 sessions of catch-up

**Build ZERO of these gaps tonight.** Build each one ONLY when a
paying customer asks OR when a specific trigger fires.

The single highest-leverage action right now is sending the emails,
not building features.

---

## RELATED FLAGS

- BYTEXL-COMPETITIVE-ANALYSIS-FLAG.md — broader LMS competitor
- ZERAVIA-COMPETITIVE-ANALYSIS-FLAG.md — career navigation + training
- INVERTED-MARKETPLACE-FLAG.md — Sessions 102-104 (campus workflow)
- A4_LMS_BRIDGE_FLAG.md — plug into LMS, don't replace
- DEAN_REPORT_FRONTEND_FLAG.md — self-serve Dean access
- EMPLOYER-JD-CALIBRATION-FLAG.md — whitelist before first employer email
- CHARVAK-ENTERPRISE-ROADMAP-FLAG.md — F1-F8 enterprise features
- SESSION-102-CANDIDATE-DASHBOARD-FLAG.md — deferred candidate dashboard

All demand-triggered. None built until a paying customer asks.

---

**Last updated:** 2026-11-03
**Next review:** 2026-12-03 (30 days) OR immediately if trigger fires
**Owner:** Bhavya M
