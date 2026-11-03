# POWN (PROOF OF WORK NETWORK) — VIABILITY ANALYSIS AND FLAG

**Flagged:** 2026-11-04
**Status:** NOT STARTED — demand-triggered
**Effort:** 10-12 sessions IF all viable features built
**Trigger:** See "Trigger to Build" section below

---

## THE HONEST MAPPING — POWN vs CHARVAK TODAY

| POWN concept | Charvak status | Gap |
|---|---|---|
| Micro-Sim Placement Protocol | Partially (Judge0 for coding only) | Domain-agnostic sandbox |
| Automated Proof-of-Skill Hash | Complete (HMAC + 5-layer abuse) | Zero |
| Shadow Benchmark Engine | Partial (public passport + GitHub-ready) | Live artifact ingestion |
| Universal Skill Translation | Partial (106 roles + 518 skills) | Cross-industry vectors |
| Reverse Bidding Marketplace | Partial (jobs/unified + CBREX roles) | Bounty specs |
| Automated Direct Offers | Partial (recruiter dashboard) | Priority invites |
| Enterprise Placement Assurance (8%) | None | Billing structure |
| B2B Candidate Search SaaS | Partial (recruiter dashboard) | Pricing + gating |
| Campus Institutional Licensing | Complete (3 tiers, Rs 49K-5L) | Pricing adjustment |
| B2C Proof Pass | Partial (credit-based) | Subscription tier |
| Verification API (APaaS) | Complete (CAS API) | Pricing + metering |
| Zero-bias skill verification | Complete | Zero |
| PLG via immutable badge | Partial (cert URL shareable) | Badge-first LinkedIn flow |

**Score: 45% built, 30% extendable, 25% speculative or risky.**

---

## THE 5 BUILDS WORTH DOING (RANKED BY ROI)

### Build 1 — Domain-Agnostic Sandbox Scenarios (HIGHEST VALUE)

**The gap:** Your sandbox only works for coding (Judge0). A B.Com
student, marketing fresher, or ops candidate cannot prove skill.

**What to build:**
- Scenario library: 50-100 templates across Finance, Marketing,
  Operations, Sales, Design, HR, Customer Success
- Evaluation engine: AI rubric scoring (reuse openai_compat)
- 30-min timed sessions
- HMAC cert on pass (reuse existing)
- Frontend: /sandbox page

**Effort:** 3-4 sessions

**Trigger:** First non-tech candidate says "I can't take your coding test."

**Revenue impact:** 10x market expansion (every non-tech student in India).

### Build 2 — Universal Skill Translation (CAREER PIVOT ENGINE)

**The gap:** Career pivoters cannot prove transferable skill.

**What to build:**
- Input: current role + years + domain + skills
- Output: 3-5 transferable roles with fit % + transferable/gap skills
- Path: assess -> upskill -> certify
- HMAC "Pivot Certificate"

**Effort:** 2 sessions

**Trigger:** First candidate says "I have 5 years in X, want Y."

**Revenue impact:** New segment (career pivots) + corporate L&D.

### Build 3 — Reverse Bidding Marketplace Extension

**The gap:** Employers post jobs, get resumes. They want auto-matching.

**What to build:**
- Extend charvak_client_roles with:
  - required_assessment_scores (JSONB)
  - match_threshold (percent)
  - auto_invite (bool) -> PRIORITY invite, not binding
- Matching engine: skill overlap + assessment scores + integrity
- Candidate notification with 72h acceptance window
- Recruiter dashboard: "3 matched, 1 clicked, 0 applied"

**Effort:** 2-3 sessions

**Trigger:** First employer says "want proactive matching, not listings."

**Revenue impact:** 8% hire fee + Rs 5-15K/month SaaS (India realistic).

### Build 4 — Proof Pass Subscription (B2C Recurring)

**The gap:** Credit-based only. No recurring revenue.

**What to build:**
- Charvak Proof Pass — Rs 499/month:
  - Unlimited readiness checks
  - Unlimited mock drives
  - 2 AI courses per month
  - Priority candidate surfacing
  - AI Tutor unlimited
  - Priority cert issuance

**Effort:** 2 sessions (Razorpay Subscriptions API)

**Trigger:** First user says "can I subscribe instead of buying credits?"

**Revenue impact:** 100 subs = Rs 50K MRR; 1,000 = Rs 5L MRR.

### Build 5 — Verification API Billing (APaaS)

**The gap:** CAS API is free. No metering.

**What to build:**
- Free tier: 100 calls/month
- Paid: Rs 500/month for 5,000 calls
- Usage tracking per key
- Razorpay auto-charge
- Dev portal at /employer/cas

**Effort:** 1 session

**Trigger:** First partner says "what does bulk verification cost?"

**Revenue impact:** B2B infrastructure layer, sticky.

---

## WHAT NOT TO BUILD (LEGAL / REPUTATION RISK)

### Shadow Benchmark Engine (passive artifact ingestion)

POWN says: "Ingests anonymized pull requests, SOPs, campaign ROIs,
sales call transcripts."

**Do NOT build this.** Legal exposure:
- Employer IP + trade secrets violation
- GDPR/DPDP requires consent from BOTH parties
- One company could sue

**Safe alternative:** Candidate-provided samples only (2-5 page case
study, optional 1 public link). 1 session to build.

### Automated Binding Offers

**Do NOT build "binding" invites.** Legal + abuse risk.

**Safe alternative:** "Priority match invite" with 72h acceptance
window. Non-binding. Built into Build 3.

### \ ARR / \ at 20K customers narrative

**Do NOT pitch to Indian buyers.** Average Indian ATS spend is
Rs 5K-15K/month, not \. Use Rs 5-15K/month (matches existing
Rs 49,999/year university tier).

---

## WHAT'S ALREADY BUILT (POSITIONING PLAY — NO BUILD NEEDED)

**Use this pitch in demos TODAY, without building anything:**

> "Charvak is the Proof of Work Network. Every candidate on our platform
> has:
> - Taken an assessment calibrated to their target role
> - Received an HMAC-verified certificate any recruiter can check in
>   5 seconds
> - Demonstrated integrity signals we disclose
> - Attempt history — 1st or 5th try, you know
> - Public passport URL they can share with any employer
>
> Saral finds candidates. HackerRank scores them. Naukri lists them.
> Charvak proves them."

**This requires zero build. Everything is live.**

---

## RANKED BUILD ORDER (WHEN TRIGGERED)

| # | Build | Effort | Trigger |
|---|---|---|---|
| 1 | Domain-agnostic sandbox | 3-4 sessions | Non-tech candidate asks |
| 2 | Career pivot engine | 2 sessions | Career pivot candidate asks |
| 3 | Reverse bidding marketplace | 2-3 sessions | Employer wants auto-match |
| 4 | Proof Pass subscription | 2 sessions | User wants subscription |
| 5 | API billing | 1 session | Partner wants bulk pricing |

**Total if ALL built:** 10-12 sessions.
**Likely to be built:** 3-5 sessions (Build 1 + 2 first).

---

## WHY THIS IS FLAGGED, NOT BUILT

- 0 paying customers
- 2 lakh candidate DB, 3,000 emailed, signups not yet confirmed
- Amrita follow-up sent 2026-11-03, no reply yet
- 3 overdue actions:
  - Render password rotation (overdue ~90 sessions)
  - SMTP fix for hr@charvakit.com (blocked batch 2)
  - Batch 2 candidate emails (drafted, waiting for SMTP)

**Build POWN features ONLY after:**
1. 1-3 replies from Amrita OR candidate emails
2. SMTP fixed
3. Batch 2 sent from hr@charvakit.com

**The rule:** Every build must be triggered by a real customer request.
Not roadmap ambition. Not a competitor's pitch.

---

## THE RIGHT SEQUENCING

**Phase 0 (this week):**
1. Fix SMTP (10 min)
2. Wait for replies
3. Rotate Render password (2 min)

**Phase 1 (after 1-3 replies):**
- Build 1: Domain-agnostic sandbox (3-4 sessions)

**Phase 2 (after 1 paying customer):**
- Build 2: Career pivot (2 sessions)
- Build 3: Reverse bidding (2-3 sessions)

**Phase 3 (after 3+ paying customers):**
- Build 4: Proof Pass subscription (2 sessions)
- Build 5: API billing (1 session)

---

## RELATED FLAGS

- END-TO-END-PIPELINE-EXTENSION-FLAG.md — Discover, Fit %, Reach
- TSPL-OPPORTUNITY-FLAG.md — customer pipeline
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