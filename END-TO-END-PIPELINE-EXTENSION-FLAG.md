# END-TO-END PIPELINE EXTENSIONS — FLAGGED FOR LATER BUILD

**Flagged:** 2026-11-03
**Status:** NOT STARTED — demand-triggered
**Effort:** 6-9 sessions total (3 extensions, 2 optional sub-features)
**Trigger:** See "Trigger to Build" section below

---

## THE STRATEGIC FRAMING

Charvak is not a competitor to Saral AI. Charvak is the entire
end-to-end pipeline from "fresher" to "placed." Saral is a sourcing
slice — one of eight stages.

**The 8-stage pipeline:**

| # | Stage | Charvak status |
|---|---|---|
| 1 | Discover | Partial — needs /discover page |
| 2 | Assess | Complete (106 roles, 8 formats) |
| 3 | Upskill | Complete (AI courses, tutor, FYP) |
| 4 | Prove | Complete (HMAC certs, verify URL, passport) |
| 5 | Match | Partial — needs fit % on jobs + candidates |
| 6 | Reach | Missing — needs email sequences, GitHub, WhatsApp |
| 7 | Place | Complete (employer portal, hire tracking) |
| 8 | Measure | Complete (Dean/Proof PDF backend) |

Current coverage: 5 of 8 fully, 2 partial, 1 missing.
After extensions: 8 of 8 complete.

Competitive comparison:
- Saral AI covers stages 1 and 6
- HackerRank covers stages 2 and 4
- Naukri covers stage 5
- Charvak after extensions covers all 8

---

## EXTENSION 1 — "What Should I Become?" Career Discovery

The gap: When a fresher lands on Charvak, they take an assessment,
but they often do not know what to take. They need a "discover" layer.

What Saral does (candidate-side equivalent): Natural-language search
that maps "Bangalore mein backend engineer" to a ranked shortlist.

What Charvak will do (candidate-side, not recruiter-side):
- /discover page with a search bar
- User types: "I want to work with data in Bangalore"
- LLM parses → maps to 106-role catalog → returns 3-5 fit careers
- Each career card shows: fit %, skill gaps, time to ready, entry salary
- One-click "Start readiness check for [role]"

Build plan:
- Session 1: LLM parse + role-matching engine
  - Reuse jd_parser_engine.parse_jd() pattern
  - Build career_discovery_engine.py
  - New route: POST /api/discover/parse
  - Input: free-text query
  - Output: careers list with role, fit_pct, gaps, weeks_to_ready, salary_band
- Session 2: /discover frontend
  - Search bar with example queries
  - Career cards with fit %, gaps, CTA
  - Mobile-first

Builds on existing:
- career_assessment_engine (106 roles, 66 industries, 7 levels)
- jd_parser_engine (LLM parsing pattern)
- openai_compat (GPT-5 ready)
- Language support (34 languages)

Revenue impact:
- More candidates → more readiness checks
- More readiness checks → more certificates
- More certificates → more placement-ready talent for employers

Trigger to build:
- After Amrita signs OR
- After TSPL commits OR
- First college asks "how do students find the right assessment?"

---

## EXTENSION 2 — "Am I Ready?" Fit % on Jobs and Candidates

The gap: Charvak has /jobs/unified (job board + staffing + gigs),
but no fit score. A candidate sees a job but does not know if they are ready.

What Saral does: Every candidate card has Excellent/Good/Partial/Weak
fit with source-linked evidence.

What Charvak will do (both directions):

Candidate side:
- Every job card gets a "Your fit: 72%" badge
- Click to see: skills you have, skills you lack, course to close gap
- Sort by fit % — "Jobs you are ready for today" vs "Stretch roles"

Recruiter side:
- Every candidate in /recruiter/dashboard gets "match %" for the role
- Filter by minimum fit %
- Evidence attached: which skills match, which do not

Build plan:
- Session 1: Match scoring engine
  - New: match_scoring_engine.py
  - Input: candidate_id (assessment data) + role_id (skills_required)
  - Reuse: jd_calibration.py overlap logic
  - Reuse: skill_catalog.py (518 skills)
  - Output: fit_pct, matched_skills, missing_skills, recommended_course
- Session 2: Frontend display
  - Fit % badge on /jobs/unified cards
  - Fit % column on /recruiter/dashboard table
  - Sort/filter options

Builds on existing:
- charvak_jobs, charvak_client_roles, charvak_micro_projects
- career_assessment_engine (candidate skill data)
- jd_calibration.py (overlap logic exists)
- career_v2.html (career center shell)

Revenue impact:
- Candidates apply only where they will succeed
- Employers get higher-quality applicants
- Fewer wasted interviews → higher placement rate

Trigger to build:
- After Amrita signs OR
- First recruiter says "I want to see candidate-role fit before contacting"

---

## EXTENSION 3 — "Reach" Layer (the missing stage)

The gap: Charvak has candidates, employers, and proof — but no
systematic way to reach out. Current flow is manual: click candidate →
open email client → type message.

What Saral does: Waterfall enrichment + multi-channel outreach.

What Charvak will do (3 sub-features):

### 3a. Email sequences (1 session)

- Recruiter creates a campaign for a role
- Selects 20 candidates
- Sets a 3-email sequence (Day 0, Day 2, Day 4)
- Each email auto-personalized: "Hi [name], your Charvak score
  matches our [role] opening..."
- Reply detection → stops sequence
- Reply-to: recruiter's email

Builds on: email_engine (SendGrid), recruiter_dashboard

Trigger: First employer asks for outreach automation

### 3b. GitHub public signal reader (1-2 sessions)

- For each candidate with a public GitHub linked, fetch:
  - Recent commit activity
  - Top languages
  - Public repos
  - Star count
- Display on their Charvak profile and on recruiter's view
- Legal, free, no scraping risk (GitHub explicitly allows public API)

Builds on: candidate_profile_engine, passport_engine

Trigger: First technical hire request

### 3c. WhatsApp template message (1-2 sessions + Meta approval)

- WhatsApp Business API (needs approval, 2-4 weeks)
- Template message: "Hi [name], you matched our [role] at [company].
  Interested?"
- Candidate replies → recruiter notified

Builds on: Meta Business API (external block, per Session 45-A4)

Trigger: 3rd employer asks for WhatsApp outreach

Total Extension 3 effort: 3-5 sessions (dependent on WhatsApp approval)

Revenue impact: Recruiters do 5-10x more outreach per session.
Higher placement rate → higher ARR.

---

## WHAT NOT TO BUILD (Even Though Saral Has It)

| Saral feature | Why not to build it |
|---|---|
| 150M profile scraper | Legal exposure (LinkedIn ToS, DPDP). Not viable. |
| Waterfall contact enrichment | Rs 50K-2L/year vendor costs. Not worth it until 10+ employers ask. |
| LinkedIn automation | Permanent account bans. Full stop. |
| X/Twitter scraping | 100-500 USD/month API. Low signal for Indian hiring. |
| Switch-intent from LinkedIn | Same scraping risk. Infer from Charvak activity instead. |

The pattern: Do not build what requires scraping or vendor contracts.
Build what uses existing public APIs (GitHub) and existing Charvak
signals (assessments, retakes, JD scans).

Saral 150M is likely inflated. Probably 30-50M scraped profiles,
not 150M verified. Not a moat you can cross in a session plan.

---

## THE COMPLETE PIPELINE (AFTER EXTENSIONS)

    Stage 1: DISCOVER (NEW)
    - /discover — "I want to work with data in Bangalore" → 3-5 fit careers
    - Career quiz (existing) → 3 fit careers
    - JD Scanner (existing) → "What roles match this JD?"

    Stage 2: ASSESS (EXISTING)
    - /readiness-check (existing) → Score + skill gaps

    Stage 3: UPSKILL (EXISTING)
    - /ai-courses (existing) → AI-designed courses
    - /final-year-project (existing) → FYP assistant
    - /ai-tutor (existing) → chat tutor

    Stage 4: PROVE (EXISTING)
    - HMAC certificate (existing)
    - Public verify URL (existing)
    - Career Passport (existing)

    Stage 5: MATCH (ENHANCED)
    - /jobs/unified with fit % (NEW)
    - Recruiter dashboard with match % (NEW)
    - Micro-internships (existing)

    Stage 6: REACH (NEW)
    - Email sequences (NEW)
    - GitHub signals on profile (NEW)
    - WhatsApp template messages (NEW, after Meta approval)

    Stage 7: PLACE (EXISTING)
    - Employer portal (existing)
    - Hire tracking (existing)
    - Proof dashboard (existing)

    Stage 8: MEASURE (EXISTING)
    - Dean/Proof dashboard PDF (existing backend)

---

## THE END-TO-END PITCH (ONCE BUILT)

Charvak is the only end-to-end talent pipeline for Indian colleges:
- Discover — Freshers find the right career
- Assess — They know exactly where they stand
- Upskill — AI courses close their gaps
- Prove — HMAC certificates verify their skills
- Match — Jobs ranked by their actual readiness
- Reach — Recruiters contact them with real proof attached
- Place — Verified talent, verified hire
- Measure — Deans and CHROs get the impact report

No other platform covers all 8 stages. Saral covers 1 and 6.
HackerRank covers 2 and 4. Naukri covers 5. Charvak covers all 8.

---

## RANKED BUILD ORDER (WHEN TRIGGERED)

| # | Extension | Effort | Trigger |
|---|---|---|---|
| 1 | Fit % on jobs + candidates | 1-2 sessions | After Amrita signs |
| 2 | Discover page | 2 sessions | After Amrita signs |
| 3 | Email sequences | 1 session | First employer asks |
| 4 | GitHub signals | 1-2 sessions | First technical hire |
| 5 | WhatsApp | 1-2 sessions | 3rd employer asks |

Total: 6-9 sessions.

But DO NOT BUILD YET. You have 0 paying customers and 3 overdue
emails. Build these AFTER Amrita or TSPL commits.

---

## WHY THIS IS FLAGGED, NOT BUILT

- 0 paying customers
- 3 overdue actions (password rotation, Amrita follow-up, candidate emails)
- The pipeline already has 5 of 8 stages complete — the missing 3 are
  extensions, not foundations
- Every stage after Extension 1 and 2 requires a customer paying for it

The single highest-leverage action: complete the 3 overdue emails.
Then build Extension 2 (smallest, highest value). Then Extension 1.
Then Extension 3 gated on employers asking.

---

## RELATED FLAGS

- BYTEXL-COMPETITIVE-ANALYSIS-FLAG.md — LMS competitor
- ZERAVIA-COMPETITIVE-ANALYSIS-FLAG.md — career navigation
- KAMPHIRE-COMPETITIVE-ANALYSIS-FLAG.md — campus recruitment
- TSPL-OPPORTUNITY-FLAG.md — customer pipeline
- INVERTED-MARKETPLACE-FLAG.md — Sessions 102-104
- DEAN_REPORT_FRONTEND-FLAG.md — Dean self-serve access
- A4_LMS_BRIDGE_FLAG.md — plug into existing LMS
- EMPLOYER-JD-CALIBRATION-FLAG.md — whitelist before employer email

All demand-triggered. None built until a paying customer asks.

---

**Last updated:** 2026-11-03
**Next review:** 2026-12-03 (30 days) OR when Amrita/TSPL commits
**Owner:** Bhavya M