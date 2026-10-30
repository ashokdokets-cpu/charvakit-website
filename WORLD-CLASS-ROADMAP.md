# World-Class Roadmap - FLAGGED

**Flagged:** 2026-10-30 (Session 105 close)
**Status:** NOT BUILT - roadmap only
**Purpose:** The strategic plan to make Charvak a world-class, globally-suitable
advanced assessment platform. All tiers documented, none built.

**TL;DR:** The current platform is world-class in depth (5-layer abuse
protection, HMAC identity, JD calibration honesty). It is NOT world-class
in breadth (41 skills, 1 code language pair, no proctoring, no SOC 2).
The roadmap below closes the breadth gap - but ONLY funded by paying
customers.

Do NOT build speculatively. Build when demand triggers.

---

## The Core Principle

**"World-class" is not a bigger platform. It's a platform that solves
one problem better than anyone else, then expands based on what customers
actually ask for.**

The current platform is world-class in 4 specific dimensions:
- HMAC identity binding (rare in Indian assessment market)
- 5-layer abuse protection (ahead of 90% of competitors)
- Honest JD calibration ("we can verify 80% of your JD")
- Task-class transparency (nobody else names the exact task classes)

Where it is NOT world-class:
- Breadth: 41 calibrated skills vs. HackerRank's 200+
- Proctoring: no video, no screen share, no liveness detection
- Global compliance: documented but not enforced (SOC 2, EU AI Act)
- Multi-language coding: 4 languages, not 15

**The roadmap below is honest about the gap. It is not urgent.**

---

## Tier 1 - Ship After 5 Paying Customers (~6 sessions)

**Trigger:** 5 paying customers exists, first 20 real placements have
happened, and customers are asking "what else can you verify?"

| # | Enhancement | Effort | Why It Matters |
|---|---|---|---|
| 1 | **Anti-plagiarism (embedding similarity)** | 2 sessions | Detect copied answers via semantic hashing. Use OpenAI embeddings to compare current answer to prior answers across users. Flag suspiciously identical responses for review. |
| 2 | **Real-time proctoring (browser fingerprint)** | 2 sessions | Session-based identity verification. Track device fingerprint across attempts. Alert on device changes mid-assessment. |
| 3 | **Question difficulty calibration (IRT/Elo)** | 3 sessions | Adaptive difficulty per candidate. Reuses ability_engine (already exists). Calibrate question difficulty from historical pass rates. |
| 4 | **Multi-language coding (Rust, Kotlin, Swift)** | 1 session | Global market coverage. Judge0 CE supports all 3. Seed task classes per language. |
| 5 | **PostgreSQL/MySQL sandbox (real SQL engines)** | 2 sessions | Replace SQLite approximation. SQLite is honest but not representative of production SQL. Real Postgres sandbox unlocks real SQL certification. |

**Total Tier 1: ~10 sessions over 6 weeks (after trigger fires)**

---

## Tier 2 - Ship After 20 Paying Customers (~8 sessions)

**Trigger:** 20 paying customers, 100+ real placements, first enterprise
deal is in negotiation and asks "do you have video proctoring?"

| # | Enhancement | Effort | Why It Matters |
|---|---|---|---|
| 1 | **Video proctoring (facial recognition, liveness)** | 4 sessions | Enterprise compliance requirement. Legal review required for biometric data (India DPDP). Camera-based identity check at assessment start + periodic liveness snapshots. |
| 2 | **Live assessment monitoring (screen share)** | 2 sessions | Higher-stakes assessments. Optional WebRTC screen share during coding assessment. Requires legal review + candidate consent. |
| 3 | **Advanced metrics (percentile, cohort, longitudinal)** | 3 sessions | Institutional buyers require. Year-over-year comparisons, cohort analytics, source attribution (which channels produce hires). |
| 4 | **API for ATS integration (Greenhouse, Lever)** | 2 sessions | Enterprise workflow. Bidirectional webhook sync. Push verified candidates into employer's ATS. |

**Total Tier 2: ~11 sessions over 8 weeks (after trigger fires)**

---

## Tier 3 - Multi-year (20+ sessions)

**Trigger:** 50+ paying customers OR $1M ARR OR VC funding round.

| # | Enhancement | Effort | Why It Matters |
|---|---|---|---|
| 1 | **AI interviewer (voice + video)** | 6 sessions | Replace human screening rounds. Combines ElevenLabs TTS + Whisper STT + video analysis. High complexity. |
| 2 | **Multi-tenant white-label** | 4 sessions | Enterprise licensing. Each university/employer gets branded subdomain with their own certs. |
| 3 | **SOC 2 Type II** | 12 months | Enterprise gate. Vendor (Vanta/Drata ~$15K/yr) + controls implementation + audit (~$25K). |
| 4 | **Global compliance enforcement** (NYC 144, EU AI Act, DPDP) | 3 sessions | Currently documented on /compliance but not enforced in code. Bias audit, transparency logs, candidate rights portal. |

**Total Tier 3: 20+ sessions over 12-18 months (after major trigger)**

---

## What Makes It Actually World-Class

**NOT more features. These 4 things:**

### 1. Verifiability

Every certificate is HMAC-signed, identity-bound, and publicly
verifiable. A recruiter anywhere in the world can click a URL and see:
- Who the candidate is
- What they were tested on
- When it expires
- Whether it's been tampered with

**Only Charvak does this in the Indian market.** LinkedIn Learning
certificates don't have this. Coursera certificates don't have this.
HackerRank certificates don't have this.

### 2. Abuse Resistance

5-layer defense: attempt limits + identity binding + question rotation
+ multi-account detection + expiration.

**Most assessment platforms have 1-2 of these. You have 5.**

### 3. Honest Calibration

"we can verify 80% of your JD" beats "we verify everything" 10x.

**The calibrated_skills whitelist makes this honest.** Employers know
exactly what they're getting.

### 4. Task-Class Transparency

The certificate names the exact task classes tested: "arrays, dynamic
programming, SQL window functions." Not just "score: 91."

**Recruiters see WHAT was tested, not just HOW WELL.**

---

## The Test for "World-Class"

**Ask yourself before building anything from this roadmap:**

> "If I had 3 world-class engineers tomorrow, would the current
> platform be a better product, or just a bigger product?"

The answer right now is "bigger" because:
- 41 skills is not world-class breadth (HackerRank has 200+)
- 1 coding language pair is not world-class coverage
- No proctoring is not world-class integrity

But the answer is "better" in the dimensions that matter:
- HMAC identity (very rare)
- 5-layer abuse protection (ahead of most)
- Honest JD calibration (nobody else does this)
- Task-class transparency (nobody else does this)

**The roadmap closes the breadth gap. The 4 core dimensions are already
world-class.**

---

## Recommended Build Order (When Triggered)

1. **Tier 1 (#1 anti-plagiarism)** - highest leverage. Reuses existing
   embedding infrastructure. Detects AI answer copying.

2. **Tier 1 (#5 real SQL sandbox)** - highest revenue impact. SQL
   certification on real Postgres is more defensible than SQLite.

3. **Tier 2 (#4 ATS API)** - highest enterprise impact. Greenhouse/Lever
   integrations unlock enterprise deals.

4. **Tier 2 (#1 video proctoring)** - highest compliance impact. Required
   for enterprise buyers, requires legal review.

5. **Everything else in priority order**

---

## What NOT to Build (Even Now)

- Do not add 100 more roles to the career assessment (breadth without depth)
- Do not add 20 more languages (use existing 34 well)
- Do not add 50 more companies to mock drives (18 is enough)
- Do not add another AI product (you have 16)
- Do not add another AI tool (you have 12)

**The world-class gap is not breadth. It is depth in 4 dimensions + 
specific gaps in proctoring / SQL / compliance / ATS integration.**

---

## Revisit Cadence

**Read this file:**
- When a paying customer asks "do you have X feature?"
- When you're about to plan a new session
- When the trigger conditions fire
- Every 90 days to reassess market

**Do NOT read this file to:**
- Decide what to build when bored
- Justify building features without customer demand
- Skip sales work

---

## The One-Line Rule

> **The world-class roadmap is a menu, not a checklist. You pick items
> from it based on customer demand, not on ambition.**

---

**Last updated:** 2026-10-30 (Session 105 close)
**Next review:** 2026-01-30 (90 days)
**Or immediately if:** 5+ paying customers OR customer asks for a Tier 1 item