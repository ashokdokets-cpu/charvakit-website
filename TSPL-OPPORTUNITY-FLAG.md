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

---

## EXACT ROLE MATRIX — FROM TSPL'S LIVE PAGES (2026-11-03)

Captured from TSPL Labour Staffing + 5 vertical pages. These are the
actual roles TSPL deploys today. Every one of these needs a Charvak
assessment role when the TSPL pilot is committed.

### Staffing Vertical 1 — Security Guards

| Role | Skills to assess | Reading level |
|---|---|---|
| Office Security Guard | Threat detection, visitor management, access control | Class 10 |
| Factory / Industrial Guard | Perimeter security, incident reporting, emergency protocols | Class 10 |
| Residential Guard | Society protocols, visitor logging, emergency response | Class 8 |
| Event Security | Crowd management, coordination, emergency evacuation | Class 10 |
| Armed Guard | Firearms handling, escalation protocols, threat response | Class 12 + license |

### Staffing Vertical 2 — Skilled & Technical (ITI / Diploma / Cert)

| Role | Skills to assess | Reading level |
|---|---|---|
| Arc Welder | Electrode selection, bead pattern, joint types, safety | Class 10 |
| MIG Welder | Wire feed, gas flow, penetration, spatter control | Class 10 |
| TIG Welder | Torch control, filler selection, clean weld, back purge | Class 10 |
| Gas Welder | Flame adjustment, brazing, cutting, safety | Class 8 |
| Fitter (Assembly) | Tolerance reading, blueprint, hand tools, torque specs | Class 10 |
| Fitter (Maintenance) | Machine disassembly, bearing replacement, alignment | Class 10 |
| Industrial Electrician | Panel wiring, motor control, safety codes, fault finding | Class 10 |
| Residential Electrician | House wiring, earthing, MCB, load calculation | Class 8 |
| CNC Operator | G-code basics, tool offset, part inspection, safety | Class 12 |
| Lathe Operator | Cutting speed, feed rate, tolerance, threading | Class 10 |
| VMC Operator | Tool magazine, fixture setup, program loading | Class 12 |
| Quality Inspector | GD&T, measurement tools, sampling plans, report writing | Class 12 |
| Production Supervisor | Line balancing, shift planning, quality control, reporting | Class 12 + Diploma |

### Staffing Vertical 3 — Housekeeping

| Role | Skills to assess | Reading level |
|---|---|---|
| Commercial Cleaner | Surface types, chemical dilution, equipment, safety | Class 8 |
| Industrial Housekeeping | Floor scrubbing, waste segregation, machine cleaning | Class 8 |
| Hospital Sanitization Staff | Disinfection protocols, PPE, blood-borne pathogens, waste | Class 10 |
| Pantry / Cafeteria Staff | Hygiene, food handling, sanitation, customer interaction | Class 8 |
| Facility Upkeep Staff | Building maintenance basics, tools, safety | Class 8 |

### Staffing Vertical 4 — General Manpower

| Role | Skills to assess | Reading level |
|---|---|---|
| Assembly Worker | Fastening, alignment, quality check, safety | Class 8 |
| Warehouse Helper | Sorting, packing, labeling, material handling | Class 8 |
| Loader / Unloader | Weight limits, stacking, safety | Class 8 |
| Picker / Packer | Order accuracy, scanning, packing, dispatch | Class 8 |
| Forklift Operator | License, load limits, safety, maneuvering | Class 10 + license |
| Scanner / Dispatch Helper | Barcode, dispatch flow, documentation | Class 8 |
| Construction Helper | Material handling, safety, tool familiarity | Class 8 |
| Mason | Mortar mix, brick alignment, plastering, curing | Class 8 |
| Painter | Surface prep, paint mix, coats, safety | Class 8 |

### Staffing Vertical 5 — Contract / Flexible Staffing

Contract roles overlap with the above. Add-on is:
- Multi-shift availability
- Location flexibility
- Quick onboarding readiness

---

## INDUSTRIES TSPL SERVES (from live pages)

8 sectors, each with specific role demand:

1. **Manufacturing** — Production lines, helpers, shop-floor
2. **Automobile** — Assembly operators, CNC machinists, welders
3. **Pharma & Chemicals** — QC inspectors, packing staff, cleanroom
4. **FMCG** — Warehouse crew, packaging helpers, loaders
5. **Engineering** — Technicians, fitters, safety supervisors
6. **Infrastructure** — Masons, electricians, general labor
7. **Logistics & Warehousing** — Forklift operators, scanners, dispatch
8. **IT Parks & Commercial** — Corporate guards, facility housekeepers

**Each sector has reading-level-aware variations** — a warehouse helper at FMCG needs class 8 comprehension; a quality inspector at Pharma needs class 12.

---

## SKILLS-BY-VERTICAL TAXONOMY

When building the role catalog, each role needs these skill dimensions:

### Security (5 roles)
- Physical: patrol, access control, response
- Communication: reporting, escalation, coordination
- Legal: private security regulations, use of force
- Emergency: fire, evacuation, medical first response
- Integrity: background check, police verification

### Skilled & Technical (13 roles)
- Trade-specific: welding types, wiring types, machine operation
- Blueprint reading: symbols, GD&T, measurement
- Safety: PPE, LOTO, fire, hazard identification
- Quality: tolerance, inspection, defect classification
- Tools: hand tools, power tools, precision instruments

### Housekeeping (5 roles)
- Cleaning methods: surface-specific, equipment-specific
- Chemistry: dilution ratios, chemical safety, PPE
- Sanitation: hospital protocols, food safety, hygiene
- Equipment: scrubbers, wet vac, pressure washer, mops

### General Manpower (9 roles)
- Material handling: weight limits, stacking, safety
- Accuracy: order accuracy, scanning, labeling
- Equipment: forklift, pallet jack, scanner, hand truck
- Safety: warehouse safety, PPE, emergency

---

## TSPL'S ADDITIONAL SERVICES (from live pages)

TSPL also sells (beyond staffing):

1. **Compliance Management** — PF, ESI, Labor Law, Factory Act
   - 500+ companies, 50K+ workers, 0 penalty cases
   - Opportunity: bundle Charvak skill verification into compliance package

2. **Payroll Staffing** — End-to-end payroll + PF + ESI + TDS
   - 500+ partners, 15+ years, 100% compliant
   - Opportunity: payroll + skill cert = "verified payroll staff"

3. **ISO 9001:2015 certified** — they care about quality
   - HMAC-verified skill certs fit their quality positioning
   - Pitch: "your ISO certification × our HMAC skill certificate = end-to-end quality"

---

## UPDATED BUILD CHECKLIST (WHEN TSPL COMMITS)

Based on actual TSPL role mix (5 verticals, 32 specific roles):

| Build Item | Roles Covered | Effort |
|---|---|---|
| Security vertical (5 roles) | Guards only | 30 min |
| Skilled & Technical (13 roles) | Welders, fitters, electricians, CNC, inspectors | 1 session |
| Housekeeping (5 roles) | All housekeeping variants | 30 min |
| General Manpower (9 roles) | Warehouse, construction, delivery | 1 session |
| Reading-level prompt param | All 32 roles | 1 session |
| Mobile UI polish | All 32 roles | 1 session |
| Multilingual verification | Hindi, Marathi priority | 30 min |
| **TOTAL** | **32 roles** | **~4.5 sessions** |

**Prioritized build order (when triggered):**

1. **Phase 1 (Week 1-2)** — Skilled & Technical (13 roles)
   Highest margin, best clients (Haier, Hyundai, TATA AutoComp). Class 10-12 reading works with minor prompt tweaks.

2. **Phase 2 (Week 3-4)** — Security (5 roles)
   Bulk volume (TSPL does security for many clients). Simpler skills to assess. 24-48h deployment requires fast assessment.

3. **Phase 3 (Week 5-6)** — General Manpower (9 roles)
   Volume driver. Reading level class 8. Mobile-first mandatory.

4. **Phase 4 (Week 7-8)** — Housekeeping (5 roles)
   Lowest skill complexity, lowest priority.

---

**Last updated:** 2026-11-03
**Source:** TSPL Labour Staffing + 5 vertical pages + Compliance + Payroll (7 pages)
**Next review:** When TSPL pilot is committed OR 2026-12-03