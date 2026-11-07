# NEXT SESSION PLAN - Charvak

**Created:** 2026-10-30 (Session 101 close)
**HEAD at creation:** a859b21

## Session 102+ - What is Queued

### Immediate (per user decision 2026-10-30)

| # | Task | Effort | When |
|---|---|---|---|

## Session 107 — ACTIVE BUILD (2026-11-07)

**Purpose:** Job board ingestion for Bench-Placement Agent
**Full spec:** `JOB-BOARD-EXTENSION-FLAG.md`

### In-flight (this session)

- C1: Remotive + Arbeitnow adapters (`job_ingest_engine.py`)
- Migration: `charvak_jobs.source`, `external_job_id`, `raw_json` columns
- Routes: `POST /api/admin/job-sources/sync`, `GET /api/admin/job-sources`
- Admin UI: `templates/admin-job-sources.html`

### Queued (after C1)

- C2: Dice manual paste adapter (Session 108)
- C3: TechFetch manual paste adapter (Session 109)
- C4: Admin UI polish + cron (Session 110)

### Do NOT build

- LinkedIn, Indeed, Glassdoor scrapers (ToS violation)
- Browser automation for job board scraping
- Any feature that requires mass-scraping

### Real-world testing continues (parallel track)

While we build C1, user continues:

- Forwarding real JDs to `jd-parser@charvakit.com`
- Watching `/admin/bench-matches`
- Submitting PREM/ABHINAYA/Haritha
- Tracking replies in Gmail

Real-world testing = independent track from build work.

### Recently closed flags (2026-11-07)

- ✅ OpenAI GPT-4o-mini retirement — env vars verified on Render (`gpt-5.4-nano` + `gpt-5.4-mini`)
- ✅ Amrita CDC pilot — closed by user (not interested)
- ⏳ Render Postgres password rotation — user doing Monday 2026-11-09

---
| 1 | Send Amrita email to Prof. Raj | 5 min | Monday |
| 2 | Send 5 university one-pagers | 30 min | Monday |
| 3 | Rotate Render Postgres password | 2 min | Weekend |
| 4 | Email Mismatch Auto-Link Flow | ~2 hrs | When free |

### What is NOT queued (flagged)

See INVERTED-MARKETPLACE-FLAG.md for the 3-session marketplace plan.
Do NOT build until a paying customer exists.

---


---

## FLAGGED (2026-11-03) — byteXL Competitive Analysis

Full analysis in `BYTEXL-COMPETITIVE-ANALYSIS-FLAG.md`.

**7 gaps identified, all demand-triggered:**
1. LMS Bridge (5 sessions) — trigger: institution asks about LMS
2. CEFR English (3 sessions) — trigger: tier-2/3 college asks
3. Coding Practice Curriculum (4 sessions) — trigger: candidate/college asks
4. Voice Screen Agent (2 sessions) — trigger: employer asks
5. Microsoft Learn Integration (1 session) — trigger: institution asks
6. Browser IDE — PARTNER, don't build
7. Virtual Labs — SKIP entirely

**Do NOT build speculatively.** No trigger has fired.

**What's actually left:**
- Send candidate/user emails (already drafted)
- Send Amrita follow-up #1 (overdue since Oct 28)
- Rotate Render Postgres password (overdue since Session 19)

**Category-of-one positioning:**
"Keep your LMS. Add Charvak as the proof layer."

---

---

## FLAGGED (2026-11-03) — Zeravia Competitive Analysis

Full analysis in `ZERAVIA-COMPETITIVE-ANALYSIS-FLAG.md`.

**8 gaps identified, all demand-triggered:**
1. Public Trust Infrastructure (MSME + Startup India + NSQF) — 30 min
2. Partnership Credibility Page — 1 session
3. Pricing Clarity Page — 1-2 sessions
4. Free 3-Day Charvak Challenge — 1 session
5. Role Intelligence Page — 1 session
6. Certification Partner Links — 1 session
7. Surface the Moat (homepage) — 30 min
8. Testimonial Depth — 1 session

**Do NOT build speculatively.** No trigger has fired.

**3 strategic moves:**
1. "The verification layer they don't have"
2. "The proof is honest. The JD check is honest."
3. "Personalized path. Not fixed programs."

**What's actually left:**
- Rotate Render Postgres password (overdue)
- Send Amrita follow-up #1 (overdue)
- Send candidate/user emails (drafted)

**Category-of-one positioning:**
"Zeravia gives you a certificate. Charvak gives you proof."

---

---

## FLAGGED (2026-11-03) — KampHire Competitive Analysis

Full analysis in `KAMPHIRE-COMPETITIVE-ANALYSIS-FLAG.md`.

**6 gaps, all demand-triggered:**
1. Campus hiring workflow automation — 3 sessions
2. CEFR English assessment — 2-3 sessions
3. AI video interview — 3-4 sessions
4. Ready-to-use assessment templates — 1-2 sessions
5. Bulk registration + shortlisting — 1-2 sessions
6. Branded registration page — 2 sessions

**Do NOT build speculatively.** Closest competitor so far (Charvak 12/28,
KampHire 12/28, 4 ties) but different buyer and product.

**Strategic positioning:**
"KampHire replaces your recruitment workflow. Charvak plugs into it as
the proof layer."

**What's actually left:**
- Rotate Render Postgres password (overdue)
- Send Amrita follow-up #1 (overdue)
- Send candidate/user emails (drafted)

---
---

## FLAGGED (2026-11-03) — TSPL Opportunity

Full analysis in `TSPL-OPPORTUNITY-FLAG.md`.

TSPL Group is a potential CUSTOMER (not competitor): 40K workers/year,
470+ partner companies, 6 govt apprenticeship schemes.

**Charvak can serve today:** NATS/AEDP degree apprentices.
**Cannot serve today:** NAPS/MAPS/FLEXI ITI blue-collar (needs trade
roles + reading-level-aware prompts + mobile UI).

**Scoped plan:**
1. Send NATS-only pilot email (not full 40K)
2. Collect TSPL cohort data (program mix, roles, reading levels)
3. Build blue-collar support ONLY after pilot committed

**When triggered (TSPL pilot committed):**
- Blue-collar role catalog (24-30 roles) — 2 sessions
- Reading-level-aware prompts — 1 session
- Multilingual question verification — 30 min to 1 session
- Mobile-first UI — 1 session
- Total: 4-5 sessions minimum

**What's actually left:**
- Rotate Render Postgres password (overdue)
- Send Amrita follow-up #1 (overdue)
- Send candidate/user emails (drafted)

------

## FLAGGED (2026-11-03) — End-to-End Pipeline Extensions

Full analysis in END-TO-END-PIPELINE-EXTENSION-FLAG.md.

Charvak is the full pipeline (8 stages), Saral is a slice (2 stages).
Currently 5 of 8 stages complete. 3 extensions close the gap.

The 3 extensions:

1. Discover page (2 sessions) — Freshers find the right career
2. Fit % on jobs and candidates (1-2 sessions) — Ready-vs-stretch ranking
3. Reach layer (3-5 sessions) — Email sequences + GitHub + WhatsApp

Total: 6-9 sessions.

Do NOT build scraping-based features (LinkedIn, X, waterfall
enrichment). Build only what uses public APIs (GitHub) and existing
Charvak signals.

Build order when triggered:
1. Fit % (smallest, highest value) — after Amrita/TSPL commits
2. Discover page — after Amrita/TSPL commits
3. Email sequences — after 1st employer asks
4. GitHub signals — after 1st technical hire
5. WhatsApp — after 3rd employer asks

What is actually left:
- Rotate Render Postgres password (overdue)
- Send Amrita follow-up #1 (overdue)
- Send candidate/user emails (drafted)

------

## FLAGGED (2026-11-04) — POWN Viability Analysis

Full analysis in POWN-VIABILITY-FLAG.md.

POWN pitch is 45% built in Charvak already. 3 features worth building,
2 features would create legal risk, 4 features are nice-to-have.

5 builds (10-12 sessions total if all done):
1. Domain-agnostic sandbox (3-4) — HIGHEST, unlocks 10x market
2. Career pivot engine (2)
3. Reverse bidding marketplace (2-3)
4. Proof Pass subscription (2)
5. API billing (1)

DO NOT BUILD:
- Shadow Benchmark (passive PR/SOP ingestion) — legal risk
- Binding auto-offers — unenforceable
- \ ARR India pitch — unrealistic pricing

POSITIONING PLAY (no build needed):
"Charvak is the Proof of Work Network. Saral finds candidates.
HackerRank scores them. Naukri lists them. Charvak proves them."

Use this pitch in demos today.

BUILD GATE:
- After 1-3 replies from Amrita OR candidate emails
- After SMTP fix (batch 2 waiting)
- After Render password rotation

What's actually left:
- Fix SMTP (10 min)
- Rotate Render password (2 min)
- Send batch 2 from hr@charvakit.com
- Log every reply

------

## FLAGGED (2026-11-04) — Revenue Stream Extensions

Full analysis in REVENUE-STREAM-EXTENSIONS-FLAG.md.

3 blueprint docs, 11 concepts analyzed. 4 worth building, 2 DO NOT BUILD.

4 BUILDS:
1. Pay-on-Placement Escrow (2 sessions) — HIGHEST ROI, 85% built
2. Skill-Swap Bounties (2-3 sessions) — 80% built
3. Inversed ATS (3-4 sessions) — 50% built
4. Proof-of-Output Badging (3-4 sessions) — 60% built

3 DO NOT BUILD:
- Shadow-Track (surveillance, illegal)
- Career Proof-of-Stake (gambling)
- US pricing narrative (India reality is ₹5-15K/mo)

HONEST SEQUENCE:
- This week: SMTP fix, Render password, batch 2 (20 min)
- After 1-3 replies: Build Placement Escrow
- After 1 employer uses it: Build Skill-Swap
- After 3 employers: Build Inversed ATS
- After 5 employers: Build Proof-of-Output

Do NOT build all 4 at once. Each triggered by 1 paying customer's ask.

What is actually left:
- Fix SMTP (10 min)
- Rotate Render password (2 min)
- Send batch 2 from hr@charvakit.com

------

## FLAGGED (2026-11-05) — Two Agent Products

Two separate products, two separate builds:

### 1. Bench-Placement Agent — BUILD NOW (4 sessions)

**File:** BENCH-PLACEMENT-AGENT-FLAG.md

**What:** Internal sales tool for US staffing. Finds US contract roles matching H1B/OPT bench, surfaces daily, one-click submission to vendors.

**Why now:** Zero legal risk (own inbox + own bench + own vendor emails). Immediate value. Funds the auto-apply agent build.

**Sessions:**
1. Vendor JD Inbox Parser (~6-8h)
2. Bench Candidate Profile (~6-8h)
3. Matching Engine (~6-8h)
4. Daily Digest + Submission (~6-8h)

**Start:** This week. Session 1 begins after this commit.

### 2. Auto-Apply Agent — BUILD LATER (5 sessions)

**File:** AUTO-APPLY-AGENT-FLAG.md

**What:** Candidate-facing agent. Finds roles, matches to Charvak US candidates, notifies candidate, handles approval, submits to direct clients.

**Trigger:** 10+ bench placements AND 100+ US candidates AND 5-10 direct clients.

**Sessions:**
5. Direct Client Role Pipeline
6. Candidate-Facing Matching
7. Candidate Approval Flow
8. Client Submission
9. Auto-Apply Dashboard

**Do NOT build until trigger fires.**

---

**What's actually left:**
- Build Bench Agent Session 1
- Rotate Render Postgres password (still pending)
- Avenoir email (India staffing, vendor registration)
- India startups/direct clients

**Order:**
1. Flag both agents (this commit)
2. Start Session 1 of Bench Agent
3. In parallel: Avenoir + India outreach

---
