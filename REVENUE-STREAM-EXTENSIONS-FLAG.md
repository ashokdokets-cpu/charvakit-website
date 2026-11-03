# REVENUE STREAM EXTENSIONS — FLAGGED FOR LATER BUILD

**Flagged:** 2026-11-04
**Status:** NOT STARTED — demand-triggered
**Effort:** 10-13 sessions if all 4 builds executed
**Trigger:** See "Trigger to Build" section below

---

## THE HONEST MAPPING — 11 CONCEPTS vs CHARVAK TODAY

Three source documents analyzed (11 concepts total):

**Doc 1:** Ghost-Hire, Shadow-Track, Interview Escrow
**Doc 2:** Career Proof-of-Stake, Job-Sim AI Bounties, Reversity
**Doc 3:** Skill-Swap Bounties, Inversed ATS, Proof-of-Output Badging,
Pay-on-Placement Escrow

| Concept | Charvak coverage |
|---|---|
| Pay-on-Placement Escrow | ~85% built (micro-internship escrow) |
| Skill-Swap Bounties | ~80% built (micro-internships) |
| Inversed ATS (vector search) | ~50% built (assessments + ability_engine) |
| Proof-of-Output Badging | ~60% built (HMAC certs + integrity) |
| Ghost-Hire | Partial (micro-internships) |
| Interview Escrow | Partial (escrow infra) |
| Job-Sim AI Bounties | Partial (Judge0 for coding only) |
| Reversity (Reverse Bidding) | Partial (reverse-staffing) |
| Shadow-Track (passive monitoring) | DO NOT BUILD (illegal) |
| Career Proof-of-Stake | DO NOT BUILD (gambling) |
| US pricing model | Adjust to India reality |

**4 builds worth executing. 2 concepts do not build. 1 narrative needs adjustment.**

---

## THE 4 BUILDS WORTH DOING

### Build 1 — Pay-on-Placement Escrow (HIGHEST ROI, 85% built)

**What:** Employer deposits 1 month salary in escrow on offer. Released:
- Day 1: 20% to platform
- Day 30: 80% to candidate (or auto-refunded if candidate leaves in <30 days)

**Already have:** escrow_engine.py, Razorpay, micro-internship escrow,
hire tracking

**Missing:** source='placement' support, trial_period_days,
trial_end_at, cron auto-release, refund flow, trial status widgets

**Effort:** 2 sessions

**Trigger:** First employer says "how do we know the hire will work out?"

**Revenue:** 10% escrow fee per placement.
₹5L salary hire → ₹50K fee → 20/month = ₹10L/month

**Why this is the single best build:** Fintech, not AI. Charges on real
transaction value (salary), not abstract credits. India-relevant
(employers want risk protection). 85% already built.

---

### Build 2 — Skill-Swap Bounties (extend micro-internships)

**What:** Instead of 2-4 week micro-project, allow 1-hour micro-bounties.
Candidate completes → if top 10% → guaranteed interview.

**Already have:** micro_internship_engine, charvak_micro_projects,
escrow, application flow, submission

**Missing:** Bounty spec (15-60 min), AI task scoring, top-10% → interview
flow, bulk bounty posting, browse bounties page

**Effort:** 2-3 sessions

**Trigger:** First startup says "we need quicker way to test candidates
than 4-week internship"

**Revenue:** ₹149-499 per bounty + ₹499 interview unlock.
100 bounties/month × ₹199 = ₹20K/month + 8% hire success fee

---

### Build 3 — Inversed ATS (vector-based recruiter search)

**What:** Recruiters search by capability vectors, not keywords:
"Python execution velocity 85+, analytical speed 90th percentile,
salary < 30L" → matching candidates with evidence.

**Already have:** career_assessment_engine, ability_engine,
charvak_user_ability, recruiter_dashboard, jd_calibration, 106 roles,
518 skills

**Missing:** Multi-dimensional vector model (Execution Velocity,
Analytical Rigor, Communication Clarity, Problem-solving Speed, Domain
Depth), charvak_candidate_vectors table, slider-based search UI, query
builder, auto-invite flow

**Effort:** 3-4 sessions

**Trigger:** First recruiter says "I want to search by capability, not
keywords"

**Revenue:** ₹999-4,999/month per recruiter seat.
20 recruiters × ₹999 = ₹20K/month; 100 = ₹1L/month

**Why this is defensible:** Saral has 150M candidate moat but no
multi-dimensional capability scores. Only Charvak has these vectors.

---

### Build 4 — Proof-of-Output Badging (30-second playback)

**What:** When recruiter clicks cert, they see 30-second playback of
how candidate solved each question (timing, revisions, etc.).

**Already have:** HMAC certs, integrity signals, per-question timing,
public verify URL

**Missing:** Session replay recording (consented), per-question timing
JSONB, playback frontend viewer, consent toggle

**Effort:** 3-4 sessions (session replay is complex)

**Trigger:** First employer says "how do I know the candidate actually
did this and not an AI?"

**Revenue:** ₹49 per premium cert (vs free basic) OR bundled into
Proof Pass subscription

**Why this beats POWN's version:** POWN's shadow tracking requires
surveillance (legal risk). Your version is opt-in and legal.

---

## WHAT NOT TO BUILD (LEGAL / REPUTATIONAL RISK)

### Shadow-Track (passive work monitoring)

Doc 1: "Privacy-first browser extension monitors real-day problem-solving
activity"

**DO NOT BUILD:**
- Violates GDPR + DPDP + India IT Act
- Employers would need consent (they won't give)
- Candidates won't install (trust barrier)
- One lawsuit = platform shutdown
- This is surveillance disguised as career tool

Safe alternative: micro-bounty system (candidate actively submits work,
not passively monitored)

### Career Proof-of-Stake (financial staking by peers)

Doc 2: "Peers stake ₹500-2,000 on candidate readiness; slashed if
candidate lies"

**DO NOT BUILD:**
- Legal: gambling under Public Gambling Act 1867 in India
- Practical: requires an entire staking industry to exist
- Reputational: staker loses money on friend = fight
- Ethics: turns referral into financial betting

Safe alternative: Skill-Swap Bounties (candidates do real work for real
startups, not bets)

### US pricing narrative

All 3 docs use: \-2,999/mo SaaS, \-20/bounty, \-200 escrow

**Reality:** Indian enterprises pay ₹5K-15K/month for ATS/recruiting

Adjust:
- \/mo → ₹4,999/mo
- \/bounty → ₹149/bounty
- \ escrow → ₹499 escrow

Global buyers: keep USD. India-first launch.

---

## THE COMPLETE REVENUE STREAM MAP (AFTER 4 BUILDS)

| # | Stream | Pricing | 12-month monthly |
|---|---|---|---|
| 1 | Credit purchases (existing) | ₹199-999 one-time | ₹10K-50K |
| 2 | University subs (existing) | ₹49,999-4,99,999/yr | ₹1L-3L |
| 3 | CAS API (existing, unbilled) | Free today | ₹0 (bill later) |
| 4 | Placement escrow (NEW) | 10% of salary | ₹50K-5L |
| 5 | Skill-Swap bounties (NEW) | ₹149-499/bounty | ₹20K-1L |
| 6 | Inversed ATS SaaS (NEW) | ₹999-4,999/mo | ₹20K-5L |
| 7 | Proof-of-Output (NEW) | ₹49/cert premium | ₹5K-50K |
| 8 | Proof Pass (POWN build 4) | ₹499/mo | ₹0 (wait for 1 paying) |
| 9 | API billing (POWN build 5) | ₹500/5K calls | ₹0 (wait for 3 paying) |

**12-month conservative:** ₹1-3L/month recurring
**18-month realistic:** ₹5-10L/month recurring
**24-month stretch:** ₹20-30L/month if one stream hits

**None of this happens without 1-3 paying customers first.**

---

## THE HONEST EXECUTION SEQUENCE

### This week (20 min total)

1. Fix SMTP (10 min) — username hr@charvakit.com, port 587, TLS
2. Rotate Render password (2 min)
3. Send batch 2 from hr@charvakit.com (after SMTP fix, 30 min)

**Do NOT build anything this week.** Wait for replies.

### After 1-3 replies (next week)

**Pick ONE build:**

**Recommended first: Pay-on-Placement Escrow (2 sessions)**
- 85% built (fastest to ship)
- Highest revenue per transaction
- Fintech, not AI (no LLM cost)
- Every Indian employer wants it
- Positions Charvak as "risk-free hiring"

### After 1 employer uses Placement Escrow

**Build: Skill-Swap Bounties (2-3 sessions)**

### After 3 employers use Skill-Swap

**Build: Inversed ATS (3-4 sessions)**

### After 5 paying employers

**Build: Proof-of-Output Badging (3-4 sessions)**

**Do NOT build all 4 at once.** Each build triggered by 1 paying
customer's specific ask.

---

## RANKED BUILD ORDER (WHEN TRIGGERED)

| # | Build | Effort | Trigger |
|---|---|---|---|
| 1 | Pay-on-Placement Escrow | 2 sessions | Employer asks about risk |
| 2 | Skill-Swap Bounties | 2-3 sessions | Startup wants faster test |
| 3 | Inversed ATS | 3-4 sessions | Recruiter wants capability search |
| 4 | Proof-of-Output | 3-4 sessions | Employer asks about AI cheating |

**Total if all 4:** 10-13 sessions
**Likely to be built:** 4-6 sessions (Build 1 + 2 first)

---

## WHY THIS IS FLAGGED, NOT BUILT

- 0 paying customers
- SMTP broken (blocks batch 2)
- Amrita follow-up sent 2026-11-03, no reply yet
- 3 overdue actions: SMTP fix, Render password, batch 2

**Build POWN/revenue features ONLY after:**
1. SMTP fixed
2. Batch 2 sent from hr@charvakit.com
3. 1-3 replies from Amrita OR candidates

**The pattern from 106 sessions:** Strategic documentation is a form of
avoidance. Feels productive. Doesn't pay rent. Commit the flag, then
do the SMTP fix. Not the reverse.

---

## RELATED FLAGS

- POWN-VIABILITY-FLAG.md — 5 POWN builds (this flag extends with 4 more)
- END-TO-END-PIPELINE-EXTENSION-FLAG.md — Discover, Fit %, Reach
- TSPL-OPPORTUNITY-FLAG.md — 40K workers/year customer
- BYTEXL-COMPETITIVE-ANALYSIS-FLAG.md — LMS competitor
- ZERAVIA-COMPETITIVE-ANALYSIS-FLAG.md — career navigation
- KAMPHIRE-COMPETITIVE-ANALYSIS-FLAG.md — campus recruitment
- INVERTED-MARKETPLACE-FLAG.md — Sessions 102-104
- A4_LMS_BRIDGE_FLAG.md — plug into existing LMS

All demand-triggered. None built until a paying customer asks.

---

**Last updated:** 2026-11-04
**Next review:** 2026-12-04 (30 days) OR when any build trigger fires
**Owner:** Bhavya M