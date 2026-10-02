# Career Assessment Product — Design Plan

**Created:** 2026-10-02
**Status:** Planned (not yet built)
**Sessions:** 10 (Phase 1), 11 (Phase 2), 12 (Phase 3), 13+ (Phase 4)
**Owner:** Session context, product roadmap

---

## Why This Exists

/ai-assessment currently renders ai-bridge.html — the URL says
"AI Career Assessment" but the content is the AI Bridge product. The URL
and the content don't match, and no career-assessment flow exists.

This plan replaces that mismatch with a real, dedicated product:
a 3-step career assessment calibrated to (role x industry x level)
with all major exam formats, skill gap analysis, and a learning path.

---

## The Product Shape

    Step 1: Pick your target role + industry + experience level
            (+ pick format(s), or accept the preset for your industry)
                    |
                    v
    Step 2: Answer AI-generated questions calibrated to that combo,
            across formats you actually face in real exams
                    |
                    v
    Step 3: Get a Career Readiness Report:
            - score
            - per-topic skill gap
            - recommended learning path (courses + resources)
            - persistent at /my-results

---

## The Complete Roles Catalog

Global roles, grouped by function. This is the source of truth — the
backend serves it via /api/career-assessment/options and the frontend
populates the dropdowns from that response.

### Engineering & Software
- Frontend Engineer
- Backend Engineer
- Full-Stack Engineer
- Mobile Engineer (iOS)
- Mobile Engineer (Android)
- Mobile Engineer (Cross-Platform / React Native / Flutter)
- Data Engineer
- ML Engineer
- AI Engineer
- DevOps Engineer
- Site Reliability Engineer (SRE)
- Platform Engineer
- Cloud Engineer (AWS / GCP / Azure)
- Security Engineer
- Application Security Engineer
- Penetration Tester / Ethical Hacker
- QA / Test Engineer
- Automation Test Engineer
- Embedded Systems Engineer
- Firmware Engineer
- Solutions Architect
- Enterprise Architect
- Technical Program Manager
- Technical Writer
- Developer Advocate

### Data & Analytics
- Data Analyst
- Data Scientist
- Business Intelligence Analyst
- Analytics Engineer
- Quantitative Analyst
- Statistician
- Machine Learning Researcher
- Applied Scientist

### Product & Design
- Product Manager
- Technical Product Manager
- Product Owner
- Project Manager
- Scrum Master
- Program Manager
- UX Designer
- UI Designer
- Product Designer
- UX Researcher
- Interaction Designer
- Visual Designer
- Motion Designer
- Graphic Designer
- Service Designer

### Business & Strategy
- Business Analyst
- Systems Analyst
- Management Consultant
- Strategy Consultant
- Operations Manager
- Operations Analyst
- Finance Analyst
- Financial Analyst
- Accountant
- Auditor
- Investment Banking Analyst
- Risk Analyst
- Compliance Officer
- Legal Counsel
- Corporate Lawyer
- Paralegal

### Go-to-Market
- Marketing Specialist
- Growth Marketer
- Performance Marketer
- Content Strategist
- Content Writer / Copywriter
- SEO Specialist
- Social Media Manager
- Brand Manager
- Product Marketing Manager
- Demand Generation Manager
- Sales Executive (SDR/BDR)
- Account Executive
- Account Manager
- Sales Engineer
- Customer Success Manager
- Customer Support Specialist
- Partnerships Manager
- Community Manager
- Events Manager

### People & HR
- Recruiter / Talent Acquisition
- HR Generalist
- HR Business Partner
- HR Operations Specialist
- Learning & Development Specialist
- Compensation & Benefits Analyst
- People Analytics Specialist

### Domain-Specific
- Healthcare Administrator
- Clinical Research Associate
- Pharmacovigilance Specialist
- Medical Coder
- Teacher / Educator
- Curriculum Designer
- Academic Researcher
- Civil Engineer
- Mechanical Engineer
- Electrical Engineer
- Chemical Engineer
- Industrial Engineer
- Petroleum Engineer
- Aerospace Engineer
- Biomedical Engineer
- Environmental Engineer

---

## The Complete Industries Catalog

    IT / Tech (general)
    SaaS / B2B Software
    FinTech / Payments
    InsurTech
    RegTech
    WealthTech
    Banking / BFSI
    HealthTech / Digital Health
    BioTech / Life Sciences
    MedTech / Medical Devices
    Pharma
    EdTech
    LegalTech
    AgriTech
    FoodTech
    PropTech / Real Estate
    Construction Tech
    LogisticsTech / Supply Chain
    Mobility / Transportation
    Aviation / Aerospace
    Automotive (EV / Traditional)
    Robotics
    Semiconductors
    Cybersecurity
    Cloud Infrastructure
    AI / ML Research
    Data Infrastructure / Analytics
    Web3 / Blockchain / Crypto
    Gaming / Esports
    Media & Entertainment
    Streaming / OTT
    Music
    Publishing
    AdTech
    MarTech
    RetailTech / E-commerce
    D2C / Consumer Brands
    Marketplace / Platform
    Travel & Hospitality
    Food & Beverage / QSR
    Telecom
    Energy / Oil & Gas
    Renewables / CleanTech
    Utilities
    Mining & Metals
    Chemicals
    Consumer Packaged Goods (CPG)
    Fashion & Apparel
    Beauty & Wellness
    Sports & Fitness
    Non-profit / NGO
    Government / Public Sector / GovTech
    Defense & Space
    Education (K-12 / Higher Ed)
    Consulting / Professional Services
    Staffing & Recruiting
    Freelance / Gig Economy
    HR Tech
    Legal Services
    Accounting / Audit
    Investment / PE / VC
    Insurance
    Print / Packaging
    Agriculture / Farming
    Fishing / Aquaculture
    Forestry

---

## The 7 Experience Levels

    1. Intern / Student       — no professional experience, or in education
    2. Junior                 — 0-2 years
    3. Mid-Level              — 2-5 years
    4. Senior                 — 5-10 years
    5. Staff / Principal      — 10+ years, deep IC track
    6. Manager / Director     — people leadership
    7. Executive (VP/C-level) — organizational leadership

The prompt to OpenAI uses the level to calibrate difficulty and
question focus:

- **Intern/Junior** — fundamentals, tooling, basic problem solving
- **Mid** — applied knowledge, trade-offs, real-world scenarios
- **Senior** — architecture, strategy, cross-functional influence
- **Staff/Principal** — org-wide impact, systems thinking, technical vision
- **Manager/Director** — people leadership, prioritization, delivery
- **Executive** — strategy, P&L, board-level decisions

---

## The Complete Formats Catalog

| Format | Default count | Time estimate | Notes |
|---|---|---|---|
| mcq | 15 | 15-20 min | Was 10, bumped to 15 for statistical reliability |
| coding | 3 | 45-60 min | 1 easy, 1 medium, 1 hard — calibrated to level |
| sql | 5 | 20-30 min | 1 basic join, 1 aggregation, 1 window fn, 2 scenarios |
| system_design | 1 | 30-45 min | Open-ended prompt, AI-scored on a rubric |
| debugging | 3 | 20-30 min | Buggy code snippets, user explains fix |
| ehavioral | 5 | 15-20 min | STAR-format, AI-scored |
| case_study | 1 | 30-45 min | Business/analytics scenario, AI-scored |
| short_answer | 10 | 10-15 min | Rapid-fire, one-line answers |
| 
umeracy | 5 | 10-15 min | Quantitative reasoning for business roles |
| situational_judgment | 10 | 15-20 min | SJT for management roles |

### Industry presets (default formats offered)

**Software / Engineering roles:**
MCQ (10) + Coding (3) + System Design (1) + Debugging (2)

**Data roles:**
MCQ (10) + SQL (5) + Case Study (1) + Coding (2, Python/R)

**Product / Design:**
MCQ (10) + Case Study (1) + Behavioral (5) + System Design (1)

**Business / Consulting:**
MCQ (10) + Case Study (1) + Behavioral (5) + Numeracy (5)

**Go-to-Market / Sales:**
MCQ (10) + Behavioral (5) + Case Study (1)

**People / HR:**
MCQ (10) + Behavioral (8) + Case Study (1)

**Management / Director+ (any function):**
MCQ (10) + Behavioral (5) + Situational Judgment (10) + Case Study (1)

**Executive (VP/C-level):**
Case Study (2) + Situational Judgment (10) + Behavioral (5)

User can override and pick their own formats and counts, within per-
format min/max bounds (e.g. coding: 1-5, case_study: 1-3).

---

## Credit Model

| Assessment size | Credits |
|---|---|
| **Quick** (MCQ only, 15 Q) | 15 |
| **Standard** (2-3 formats, ~25 Q) | 30 |
| **Full Mock** (4+ formats, ~35 Q) | 50 |
| **Retake within 30 days** | Free |

Rationale:
- Real value scales with formats and questions
- Retake-free rewards engagement and learning
- Higher ceiling for serious users, cheap entry for explorers
- Matches patterns already in the codebase (mock-drive 25 cr,
  advanced assessment pricing)

Credit keys:
- career_assessment_quick: 15
- career_assessment_standard: 30
- career_assessment_full: 50

Retake-free logic: charvak_career_assessments records the first
attempt timestamp per (email, role, industry, level, formats_hash).
If a matching assessment exists within 30 days, the start route
returns 
etake_free: true and does not deduct credits.

---

## Phase Breakdown

### Phase 1 (Session 10, ~4-5 hrs) — Foundation

**Goal:** skeleton works end-to-end with MCQ only.

Deliverables:
- New namespace /api/career-assessment/* (clean, no collision)
- New template 	emplates/ai-assessment.html (3-step wizard)
- Roles + industries + levels served from /api/career-assessment/options
- Two tables:
  - charvak_career_assessments (assessment_id PK, email, role,
    industry, level, formats_json, status, score, started_at,
    completed_at, retake_of, credits_used)
  - charvak_career_assessment_answers (answer_id PK,
    assessment_id FK, question_index, format, question_json,
    answer_json, correct, ai_score, ai_feedback, answered_at,
    UNIQUE(assessment_id, question_index))
- Routes:
  - GET  /api/career-assessment/options — public, returns catalogs
  - POST /api/career-assessment/start — auth + credits, creates
    assessment, generates MCQ questions via OpenAI, returns
    assessment_id + questions
  - POST /api/career-assessment/answer — auth, idempotent per
    question
  - POST /api/career-assessment/complete — auth, scores, saves to
    charvak_assessment_results for /my-results, returns report
  - GET  /api/career-assessment/history/{email} — auth, past
    assessments
  - GET  /api/career-assessment/{assessment_id} — auth, resume or
    view a specific assessment
- Credit keys: career_assessment_quick, _standard, _full
- Fix /ai-assessment route to render 	emplates/ai-assessment.html
- ai-bridge.html untouched (Bridge product keeps working at
  /bridge and /ai-bridge)

**Success criteria:** a user can pick any of ~70 roles, any of ~65
industries, any of 7 levels; get 15 AI-generated MCQs calibrated to
that combo; submit answers; receive a score + skill gap; see the
result at /my-results.

**Persists and reuses:**
- charvak_assessment_results — already used by IELTS, Versant, Mock
  Drives, so /my-results "just works"
- bility_engine.py (from Session C4) — Phase 3 adaptive will plug
  in here
- credit_guard.require_credits_from_data — same pattern as every
  other paid route

**Test user:** 	est-register-2026-09-24@example.com

### Phase 2 (Session 11, ~5-6 hrs) — Format expansion

**Goal:** add all the formats users actually face in real exams.

Deliverables:
- Format registry in the engine (single source of truth for
  format-specific prompts, question counts, scoring)
- Per-format question generation:
  - mcq (exists from Phase 1)
  - coding — Glider/HackerRank style. Phase 2a: read-only code
    snippet + free-text explanation (easier). Phase 2b: full editor +
    runner (needs sandboxing — separate session).
  - sql — query editor + expected output comparison
  - system_design — free-text essay, AI-scored on a rubric
  - debugging — buggy code + user explains fix, AI-scored
  - ehavioral — STAR-format, AI-scored against framework
  - case_study — scenario + AI scoring against a rubric
  - short_answer — rapid-fire, exact/near-match AI scoring
  - 
umeracy — quantitative reasoning, exact scoring
  - situational_judgment — SJT scoring logic
- Format picker on Step 1 (with industry presets)
- Per-format rendering on Step 2

**Stretch (Session 11b if needed):** real code execution sandbox for
coding/SQL formats. Otherwise free-text explanation only.

### Phase 3 (Session 12, ~4-6 hrs) — Adaptive + learning paths

**Goal:** make it smart and give real guidance.

Deliverables:
- Adaptive difficulty — question N+1 depends on how N went, using
  bility_engine.update_from_assessment (from Session C4)
- Skill gap analysis — per-topic breakdown
- Recommended learning path — map weak topics to courses in
  charvak_courses + external resources; AI-curated
- History + progress dashboard — chart improvement over retakes
- Per-combo leaderboard (optional, privacy-gated)

### Phase 4 (future, multi-session) — Advanced

- Certificates for top scores
- Voice-based rounds (reuse Versant)
- AI interviewer persona for behavioral rounds
- Employer-visible badges (reuse Skill-Twin)
- Peer benchmarking (with privacy controls)
- Integration with /bridge so candidates can attach their
  Career Readiness Report to applications

---

## Technical Notes

### Namespace decision

/api/career-assessment/* is clean. It does NOT touch the legacy
/api/assessment/* routes (which are marked for deletion in the
tracker but never removed). Those stay dormant; this product uses
its own namespace.

### Why not extend /api/assessment/*?

Three reasons:
1. Legacy routes are marked for potential deletion — extending them
   creates a false dependency
2. The namespace /api/assessment/* is generic and collides with
   versant, mcq, mock-drive, skill-gap, companies, scorecard routes
   that already exist under different prefixes
3. A dedicated namespace makes the product's API surface obvious and
   debuggable

### Persistence

All data goes to charvak_career_* tables. On completion, one row
also goes to charvak_assessment_results with
ssessment_type='career_readiness' so /my-results picks it up
automatically.

### Prompt engineering

The prompt to OpenAI takes (role, industry, level, formats, counts)
as structured input. Question generation is one call per format, not
one call per question, to keep latency reasonable:
- MCQ: 1 call for 15 questions
- Coding: 1 call for 3 problems
- Behavioral: 1 call for 5 prompts
- Etc.

Scoring calls happen on /complete — again, one call per format,
producing the score + skill gap + feedback in one response.

### Rate limits

- /options — public, 120/min
- /start — 20/min (credits gate anyway)
- /answer — 120/min
- /complete — 20/min
- /history — 120/min

### Security

Every route except /options uses:
- 
equire_auth_for_email(request, email) — email match
- except HTTPException: raise FIRST in the try/except chain (the
  147-clause fix from Session C)

---

## Test Plan (Phase 1)

E2E with 	est-register-2026-09-24@example.com:

1. GET /api/career-assessment/options — returns ~70 roles,
   ~65 industries, 7 levels, ~10 formats
2. POST /api/career-assessment/start with Data Scientist +
   HealthTech + Mid-Level — 15 cr, returns assessment_id + 15
   questions about health-tech data science
3. POST /api/career-assessment/answer for all 15 — idempotent
4. POST /api/career-assessment/complete — scores, writes to
   charvak_assessment_results
5. GET /api/career-assessment/history/{email} — shows the
   assessment
6. Retake within 30 days — 
etake_free: true, no deduction
7. Auth mismatch on /history for a different email — 403
8. Load /ai-assessment in browser — shows new template, not
   ai-bridge.html
9. Load /my-results in browser — shows the new assessment alongside
   IELTS/Versant/etc.

---

## What's OUT of Scope (deliberately)

- Real code execution sandbox (Phase 2b, separate session)
- Live human proctoring (never)
- AI voice interviewer (Phase 4)
- Employer matching integration (Phase 4)
- Skill certifications (Phase 4)
- Multi-attempt benchmark data (Phase 3+)

---

## Dependencies

- enhanced_email.send_career_assessment_result() — new method, add
  in Phase 1 (optional: emails the report)
- bility_engine.py — exists, Phase 3 uses it
- 
esults_system.record_assessment_result() — exists, Phase 1 uses
  it
- charvak_courses — exists, Phase 3 maps weak topics to courses
- OpenAI GPT-4o-mini — exists, all phases use it
- credit_guard — exists, all phases use it

---

## Session Prompt for Session 10

When starting Session 10, paste this:

    Read CAREER-ASSESSMENT-PLAN.md. We're building Phase 1.
    Confirm HEAD is 69e3daa or later. Confirm tree is clean.
    Stop uvicorn. Run discovery greps on:
      - templates/ai-assessment.html (probably doesn't exist yet)
      - main.py route for /ai-assessment
      - ai_credit_engine.py for career_assessment keys
      - how results_system.record_assessment_result is called
      - how /my-results displays entries
    Then write the patch.

---

**Keep this file in sync as the product evolves. It is the source of
truth for Sessions 10-13.**
---

## Phase Split (updated 2026-10-02)

Phase 2 was originally one session. It's now split because coding and
SQL require real execution sandboxes that deserve their own focused
session.

### Phase 2a (Session 11, this session)

Seven formats that don't need code execution:

| Format | Question shape | Answer shape | Scoring |
|---|---|---|---|
| short_answer | {q, expected_answer, keywords} | 1-3 sentence text | AI-near-match |
| numeracy | {q, correct_number, tolerance} | number | Exact / tolerance |
| situational_judgment | {scenario, options, best_index, worst_index} | choice pair | Deterministic |
| behavioral | {prompt, rubric_star} | free-text STAR | AI batch-scored |
| system_design | {prompt, rubric} | free-text | AI batch-scored |
| debugging | {buggy_code, correct_fix_summary} | free-text | AI batch-scored |
| case_study | {scenario, rubric} | free-text | AI batch-scored |

**UX:** single-format per assessment. User picks one format at Step 1,
does N questions of that format, gets scored.

**Scoring:** one OpenAI call at /complete returns per-answer scores
for all answers. Batch AI scoring ~= 0.01-0.02 USD per assessment.

**Credit model:** a multiplier applies for AI-scored formats since
they cost more at scoring time. Recommended:
- Deterministic formats (mcq, numeracy, SJT, short_answer): 15 cr (quick)
- AI-scored formats (behavioral, system_design, debugging, case_study): 20 cr (quick)

Sizes scale linearly: standard = 1.5x, full = 2x.

### Phase 2b (Session 12, separate)

Two formats that need a real execution sandbox:

| Format | Needs |
|---|---|
| coding | External executor (Judge0 or Piston). Real code, run against test cases. |
| sql | Sandbox DB (e.g. a fresh Postgres schema per request). Run query, compare output. |

**Options:**
1. Judge0 hosted API - quick to integrate, has a free tier
2. Piston self-hosted - no vendor lock, but needs infra
3. Custom Docker sandbox on Render - most control, most work

Recommendation: Judge0 hosted for Phase 2b. It's a 1-day integration,
handles the security (they run code in isolated containers), and gives
us language coverage for Python, JS, Java, C++, Go, etc.

### Phase 3 (Session 13+)

- Adaptive difficulty (uses ability_engine from C4)
- Skill gap analysis per format
- Recommended learning path (maps weak topics to charvak_courses)

### Phase 4 (future)

- Certificates, voice rounds, employer badges, peer benchmarking
- Multi-format assessments (all formats in one session)
- Live mock interview mode

---

## Format Catalog (Phase 2a)

The catalog becomes richer. Each format describes:

- key - machine name
- label - display name
- scored_by - ai | deterministic | hybrid
- available - bool (Phase 2a -> some are True, coding/sql are False)
- question_count - default per size
- credit_multiplier - 1.0 for deterministic, 1.33 for AI-scored

Formats available in Phase 2a:
- mcq (Phase 1)
- short_answer
- numeracy
- situational_judgment
- behavioral
- system_design
- debugging
- case_study

Formats shown but disabled (Phase 2b):
- coding
- sql

The frontend shows the disabled formats greyed out with a "Coming soon"
tooltip so users know they're planned.

---

## Backend Architecture (Phase 2a)

### New methods in career_assessment_engine.py

- _generate_format_batch(format_key, role, industry, level, count)
  - dispatches to per-format prompt builders
- _build_prompt_for_format(format_key, ...)
  - one prompt template per format
- _score_deterministic(format_key, question, answer)
  - handles numeracy, SJT, short_answer (keyword match)
- _score_ai_batch(format_key, questions, answers)
  - one OpenAI call for all answers of one AI-scored format
- _shuffle_mcq_options - kept for MCQ
- _shuffle_sjt_options - new, for SJT (shuffles scenario options
  while tracking best_index / worst_index)

### Per-format question shapes

The questions_json column holds an array of dicts. The shape varies
by format. Frontend renders based on the format field of the
assessment.

- mcq: {q, options: [4], correct_index}
- short_answer: {q, expected_answer, keywords: [...]}
- numeracy: {q, correct_number, tolerance}
- situational_judgment: {scenario, options: [5], best_index, worst_index}
- behavioral: {prompt, rubric_star: {situation, task, action, result}}
- system_design: {prompt, rubric: [criteria]}
- debugging: {buggy_code, language, correct_fix_summary, bug_class}
- case_study: {scenario, questions: [sub-questions], rubric}

### Answer shapes stored

charvak_career_assessment_answers currently has selected_index INTEGER.
For text formats we need a text field. Migration:

    ALTER TABLE charvak_career_assessment_answers
        ADD COLUMN IF NOT EXISTS answer_text TEXT,
        ADD COLUMN IF NOT EXISTS ai_score INTEGER,
        ADD COLUMN IF NOT EXISTS ai_feedback TEXT;

Deterministic formats keep using selected_index + is_correct.
AI-scored formats use answer_text + ai_score (0-100).
The overall score is a weighted average across questions.

### Scoring aggregation

For each format, questions contribute:
- Deterministic: 0 or 100 per question (binary)
- AI-scored: 0-100 per question (continuous)
- Overall = sum(per_question_score) / total_questions

Passing threshold stays at 70.

---

## Frontend Architecture (Phase 2a)

### Step 1 - Picker gets a Format selector

New select element with id carFormatSelect with all formats. Disabled
options are shown but greyed:
    <option value="coding" disabled>Coding (coming soon)</option>

When the format changes, the size selector updates to reflect the
credit multiplier:
- Deterministic formats: "10 questions - 15 credits"
- AI-scored formats: "10 questions - 20 credits"

### Step 2 - Questions render per format

renderQuestions(assessment) dispatches on assessment.format:
- mcq / situational_judgment -> radio buttons
- short_answer -> 2-line textarea
- numeracy -> number input
- behavioral / system_design / debugging / case_study -> multi-line textarea

### Step 3 - Result unchanged, but AI feedback shown per question

On complete, the response includes per-question scoring. A collapsible
details element per question shows:
- Question
- User's answer
- Score (0-100)
- AI feedback (if applicable)

---

## Test Plan (Phase 2a)

E2E for each of the 7 new formats, with the same test user.

For each format:
1. Start quick assessment (10 Q) at the standard role/industry/level
2. Verify the question shape matches the format
3. Submit all-wrong or junk answers -> expect low score
4. Resubmit correct or strong answers -> expect high score
5. Verify charvak_career_assessment_answers.answer_text holds the input
6. Verify AI feedback populated for AI-scored formats

Specific tests:
- short_answer - submit a single-word answer -> AI says it's incomplete
- numeracy - submit a number that's 5% off with tolerance=10% -> passes
- situational_judgment - submit best_index for all -> high score
- behavioral - submit "I did stuff" -> AI gives low rubric score
- system_design - submit a structured 200-word answer -> high score
- debugging - submit "add a null check" for a null-check bug -> high score
- case_study - submit a structured analysis -> high score

---

## Credit Pricing (Phase 2a final)

| Format type | Quick (10 Q) | Standard (15 Q) | Full (20 Q) |
|---|---|---|---|
| Deterministic (mcq, numeracy, SJT, short_answer) | 15 | 25 | 35 |
| AI-scored (behavioral, system_design, debugging, case_study) | 20 | 30 | 40 |

New credit keys:
- career_assessment_ai_quick: 20
- career_assessment_ai_standard: 30
- career_assessment_ai_full: 40

Route picks the right key based on the selected format.

---

**Keep this file in sync. It is the roadmap for Sessions 11-13.**