# TSPL OPPORTUNITY — FLAGGED FOR LATER BUILD

**Flagged:** 2026-11-03
**Status:** NOT STARTED — cohort-data-triggered
**Effort:** 4-5 sessions MINIMUM (blue-collar) OR 0-1 session (NATS-only scoped pilot)
**Trigger:** See "Trigger to Build" section below

---

## THE OPPORTUNITY

TSPL Group (TalentCorp Solutions Pvt Ltd) is a government-authorized
apprenticeship + staffing company:
- 40,000+ workers placed over 10 years
- 470+ partner companies (Haier, LG, Hyundai, TATA AutoComp, ITC,
  Voltas, Jabil, Exide, JSW, Mahindra CIE, etc.)
- 570+ sourcing staff, 10,000/month hiring capacity
- 1st Rank TPA (Third-Party Aggregator) in NATS — 2025
- 6 govt schemes: NAPS, NATS, MAPS, WILP, AEDP, FLEXI ITI

**Not a competitor — a potential customer.**

The gap they have that Charvak fills:
- Workers get government "Certificate of Proficiency" (completed)
- But NO portable HMAC-verified skill certificate (verified what they
  actually know, at what level)
- No assessment data on which training centers produce best workers
- No post-placement tracking of retention / promotions
- No upskilling path after placement

**Revenue potential:**
- Scoped NATS-only pilot: ~₹4L-₹20L/year (10% of 40K workers × ₹50-100/assessment)
- Full NAPS + NATS: ~₹10L-₹40L/year
- Multi-client (TSPL + 3 more staffing cos): ~₹1.6Cr/year

---

## CRITICAL — WHAT CHARVAK CAN AND CANNOT DO TODAY

**This section is the whole reason we're flagging this instead of
sending the email immediately.**

### CAN SERVE TODAY (0 new build)

| Worker type | Charvak role | Status |
|---|---|---|
| NATS apprentice (BE/B.Tech) | Mechanical/Electrical/Civil/CS Engineer | ✅ Assessable |
| NATS apprentice (Diploma) | Junior Engineer roles | ✅ Assessable |
| AEDP students (degree-level) | Same as NATS | ✅ Assessable |
| WILP students (degree-level) | Same as NATS | ✅ Assessable |

**These workers read at class 12+ level. Current MCQ engine works.**

### CANNOT SERVE TODAY (needs new build)

| Worker type | Why it breaks |
|---|---|
| NAPS apprentice (10th/12th/ITI) | Question reading level too high; missing trade roles |
| MAPS apprentice (10th+) | Same |
| FLEXI ITI student (8th pass) | Reading level far too high; missing trade roles |
| Contractual labour (welder, cutter) | No role catalog, no practical assessment |

**Missing roles (TSPL-relevant):**
- Welder (Arc / MIG / TIG / Gas)
- Fitter (assembly / maintenance)
- Electrician (residential / industrial)
- Plumber
- Turner (lathe operations)
- Machinist (CNC / conventional)
- Wireman
- Carpenter
- Painter (spray / brush)
- AC Mechanic
- Motor Mechanic
- Auto Electrician
- Forklift Operator
- CNC Operator
- Assembly Line Worker
- Quality Inspector (shop-floor)
- Store Keeper / Inventory Handler
- Warehouse Picker / Packer
- Delivery Associate
- Production Supervisor (junior)
- Fabricator
- Sheet Metal Worker
- Pipe Fitter
- Rigging Worker

**That's ~24 trade roles missing.**

### THE READING LEVEL PROBLEM

Charvak's current MCQ prompt assumes class 12+ English comprehension.
Example from current engine:

  "A three-phase induction motor rated at 15 kW with power factor 0.85
   lagging operates 8 hours/day at 60% load. What is the approximate
   annual energy consumption in kWh?"

For BE/B.Tech: fine.
For ITI electrician (10th pass): concepts understood, but framing
inaccessible.
For FLEXI ITI (8th pass): completely inaccessible.

**Charvak works for class 12+ readers. TSPL's core workers read at
class 8-10 Hindi/Marathi.**

---

## THE BUILD PLAN (WHEN TRIGGERED)

### Trigger to build

Build ONLY when ALL of these are true:
1. You have the actual cohort data from TSPL (or a similar staffing co):
   - How many workers per program (NATS vs NAPS vs MAPS vs FLEXI ITI)
   - What roles they're actually placed into
   - What reading levels (8th pass vs 10th vs ITI vs diploma)
   - Which languages they're fluent in (Hindi? Marathi? Both?)
2. TSPL (or the customer) has said "we want to pilot this"
3. You have 1 paying customer already (Amrita or equivalent) so the
   build isn't speculative

**Do NOT build before all 3 are true.**

### Minimum viable TSPL build (4-5 sessions)

**Session 1 — Blue-collar role catalog**
- Add 24-30 trade roles (welder, fitter, electrician, plumber, etc.)
- Each role: skill list, assessment focus, reading level, practical vs theory split
- Effort: 2 sessions if focused

**Session 2 — Reading-level-aware prompts**
- Add `reading_level` param to career_assessment_engine
- Values: `class_8` / `class_10` / `class_12` / `graduate`
- Prompt modification: vocabulary appropriate, avoid passive voice, use shop-floor scenarios, safety-aware framing
- Effort: 1 session + test on 3 sample roles

**Session 3 — Multilingual question verification**
- Test: take Mechanical Engineer assessment in Marathi. Does it
  return Marathi questions or English questions with Marathi UI?
- If English → fix career_assessment_engine to generate questions in target language
- Effort: 30 min to verify, 1 session to fix if needed

**Session 4 — Mobile-first UI**
- Mobile-first assessment UI (many workers on ₹8K Android phones)
- Low-bandwidth mode
- Simple touch interface
- Effort: 1 session for MVP

### Full TSPL-ready system (8-10 sessions)

Additional:
- Practical assessment (video/simulation) for welder-type roles — 3-4 sessions
- WhatsApp delivery (WhatsApp Business API required) — 1-2 sessions

### Scoped NATS-only pilot (0-1 sessions)

If TSPL only wants NATS/AEDP degree-level apprentices:
- Everything already exists
- Need: CSV bulk upload + co-branded cert + TSPL dashboard
- ~1 session per TRACK-C plan

**This is the fastest path. Do this first if TSPL engages.**

---

## COHORT DATA TO COLLECT FROM TSPL

Before building anything, ask TSPL for:

1. **Program mix:** What % of your 40,000 are NATS vs NAPS vs MAPS vs
   FLEXI ITI vs AEDP vs contractual?
2. **Role mix:** For each program, what roles are they placed into?
   (Send me a list of top 20 roles by volume)
3. **Reading levels:** For NAPS and MAPS, what % are 8th pass vs 10th
   pass vs 12th pass vs ITI vs diploma?
4. **Language mix:** What % are Hindi vs Marathi vs Tamil vs Telugu
   vs Kannada vs Malayalam vs English?
5. **Device mix:** What % of workers have a smartphone (for assessments)?
   What % have reliable 4G?
6. **Client demand:** Which of your 470 partner companies would pay
   for "verified skill certificate"? Which roles are hardest for them
   to hire?

**The answers determine what to build. Don't guess.**

---

## THE SCOPED EMAIL (SEND THIS, NOT THE FULL-SCOPE ONE)

**Only send this after you have cohort data OR decide to open with
NATS-only scope regardless.**

**Subject:** Skill certificate for TSPL's NATS degree apprentices — not NAPS

> Hi Samruddhi,
>
> Congratulations on the #1 TPA rank in NATS 2025 — that's a serious milestone.
>
> I run Charvak (charvakit.com), a skill-verification platform. When I looked at TSPL's model, I noticed something specific about NATS.
>
> NATS apprentices are BE/B.Tech and Diploma holders. They're not welders — they're engineers-in-training who will move into supervisory, quality, and technical roles. They need skill proof that matches those roles: mechanical design, quality engineering, production planning, industrial engineering.
>
> Charvak's assessment engine already covers these roles. 106 roles × 66 industries × 7 levels. HMAC-signed certificate. Verifiable in 5 seconds.
>
> Would you like to pilot Charvak with your next 100 NATS apprentices in Pune? Free assessment. Co-branded certificate. Report back on pass rates, top skills, common gaps.
>
> Here's a sample certificate so you can see what your apprentices would get:
> https://www.charvakit.com/readiness/RDC-112D60571D41
>
> Reply "send it" and I'll have a pilot proposal in your inbox by Friday.
>
> Bhavya
> Charvak | hr@charvakit.com | +91 799 7871 701

**What this does:**
- ✅ Only claims NATS/AEDP degree apprentices (Charvak works today)
- ✅ Explicitly excludes NAPS/ITI/FLEXI ITI
- ✅ Opens the relationship with the segment you CAN serve
- ✅ If pilot works, TSPL pays you to build blue-collar (Phase 2)

---

## WHY THIS IS FLAGGED, NOT BUILT

- 0 paying customers → build would be speculative
- Blue-collar build is 4-5 sessions minimum → don't invest before pilot
- Reading-level + multilingual + mobile are not trivial → real engineering
- Practical assessment (welder) is 3-4 sessions → even bigger
- NATS-only pilot is 0-1 sessions → do this first, build blue-collar only after it works

**The single highest-leverage action:** send the NATS-scoped email.
Everything else waits for TSPL's reply.

---

## RELATED FLAGS

- BYTEXL-COMPETITIVE-ANALYSIS-FLAG.md — LMS competitor
- ZERAVIA-COMPETITIVE-ANALYSIS-FLAG.md — career navigation
- KAMPHIRE-COMPETITIVE-ANALYSIS-FLAG.md — campus recruitment
- A4_LMS_BRIDGE_FLAG.md — plug into existing LMS
- DEAN_REPORT_FRONTEND_FLAG.md — Dean self-serve access
- EMPLOYER-JD-CALIBRATION-FLAG.md — whitelist before employer email
- CHARVAK-ENTERPRISE-ROADMAP-FLAG.md — F1-F8 enterprise features
- INVERTED-MARKETPLACE-FLAG.md — Sessions 102-104 campus workflow
- SESSION-102-CANDIDATE-DASHBOARD-FLAG.md — deferred candidate dashboard

All demand-triggered. None built until a paying customer asks.

---

**Last updated:** 2026-11-03
**Next review:** 2026-12-03 (30 days) OR when TSPL cohort data arrives
**Owner:** Bhavya M
