# Charvak Competitive Strategy & Global Positioning

**Created:** 2026-10-04 (Session 16 close)
**Owner:** Product strategy
**North star:** The best integrated platform for the Local-to-Global talent journey.
**Review cadence:** Re-read at the start of every session; update quarterly.

---

## Executive Summary

Charvak is not competing to be the best point solution. We cannot out-HackerRank
HackerRank, out-Snyk Snyk, or out-Darwinbox Darwinbox. What we *can* do — and what
none of them do — is own the **full Local-to-Global talent journey** in one
integrated platform:

    Assess  ->  Prove  ->  Upskill  ->  Match  ->  Place

Every piece of Charvak's stack contributes to one stage of that journey. Every
feature we ship should either (a) make one stage dramatically better, or
(b) make the handoff between two stages seamless.

**The defensible moat:** A verified pipeline. When a candidate proves their
skills on Charvak, upskills on Charvak, and gets matched on Charvak — the
employer trusts the whole chain because it's one system, not five disconnected
tools.

---

## Where We Stand Today

| Capability | Charvak has | Category leader | Gap |
|---|---|---|---|
| MCQ assessments (career, exam, language) | Yes, 106 roles x 66 industries x 7 levels | TestGorilla (400+ tests) | Breadth |
| Coding/SQL assessments | Phase 2b (in progress) | HackerRank, Codility | Execution + integrity |
| Role readiness scoring | Partial (raw score only) | Knovia (role-readiness cert) | Positioning |
| AI code quality (slop) | Yes (AI-Slop Quarantine) | Snyk, SonarQube | Depth |
| AI security scanning | Yes (AuditBot) | Snyk, SonarQube | Continuous vs one-shot |
| Vulnerability remediation | Yes (AuditBot fix tier) | Snyk Fix, Sonar AI | Enterprise integration |
| Multilingual assessments | 34 languages (written MCQ) | Hunar.AI (voice, 20+ Indian) | Voice modality |
| Voice AI interviews | No | Hunar.AI, Vahan.ai | Full absence |
| Staffing / placement | Yes (Reverse Staffing, Micro-Squads) | Darwinbox, Rippling | Brand + scale |
| Premium deep-analysis reports | Yes (Session 16, 5 products) | None direct | Unique position |
| Ecosystem integration | Yes (Hire-Train-Deploy loop) | None | **Category of one** |

### The category-defining move

Every competitor is a **point solution**. Charvak is the only platform where a
candidate can:

1. Take a Career Assessment calibrated to (role x industry x level)
2. Receive a **Role Readiness Score** benchmarked against real market data
3. Get an AI-generated learning path from the same platform
4. Complete AI-led courses that are assessed by the same engine
5. Get matched to verified employers using the same verified skill data
6. Attach a **Premium Report** (a paid, employer-shareable PDF) to applications

No competitor can do steps 1-6 in one seamless loop. This is our moat.

---

## The Four Critical Gaps

### Gap 1 — Role Readiness Score (Session 17, Priority 1)

**What's missing:**
Career Assessment currently produces a raw score (0-100) and a pass/fail badge.
Global leaders like Knovia sell a "Role Readiness Score" that hiring managers
actually trust and reference in interviews.

**Why it matters:**
- A raw MCQ score is noise. A Role Readiness Score calibrated to what an
  employer actually needs for a specific role is signal.
- It converts the assessment from a self-improvement tool into an
  employer-facing artifact.
- It's the natural monetization point: candidates pay for the verified score;
  employers pay to see verified candidates.

**How to close it:**
1. Add a `role_readiness` score computation to `career_assessment_engine.py`.
   Formula: weighted blend of (topic coverage, skill-gap closure, cross-assessment
   ability baseline, and calibration against real role requirements).
2. Benchmarks per (role x industry x level) sourced from:
   - Historical Charvak assessment data (accumulate over time)
   - `ability_engine.get_ability` baselines
   - Curated "market benchmark" seeds per role category
3. A shareable **"Verified Role Readiness Certificate"** page:
   `/readiness/{assessment_id}` with:
   - Role, industry, level
   - Readiness score (0-100) + percentile
   - Skill-gap bar chart vs benchmark
   - "Employer Verification" badge with a signed hash
4. `/my-results` dashboard shows all readiness scores with a trend line
5. Optionally: cross-sell to the candidate's Premium Report (Session 16 product)

**Effort:** 1-2 sessions.

**Success metric:** 30% of Career Assessment completions produce a shared
readiness certificate. Employers reference it in outreach.

**Implementation sketch:**
```python
# career_assessment_engine.py
def compute_role_readiness(assessment_id):
    assessment = load_assessment(assessment_id)
    skills = aggregate_skill_gap(...)  # existing Phase 3 data
    ability = ability_engine.get_ability(email, skill=f"career_{format}")
    benchmark = get_benchmark(role, industry, level)  # new
    readiness = weighted_score(skills, ability, benchmark)
    percentile = rank_against_cohort(readiness, role, industry, level)
    return {
        "readiness_score": readiness,
        "percentile": percentile,
        "benchmark": benchmark,
        "gaps": skills,
        "certificate_url": f"/readiness/{assessment_id}",
    }
```

---

### Gap 3 — Anti-Cheating & Assessment Integrity (Session 17, Priority 2)

**What's missing:**
Global technical assessment leaders have deep integrity infrastructure:
proctoring, plagiarism detection, behavioral signals, AI-resistance design.
When Career Assessment Phase 2b ships coding + SQL via Judge0, employers will
dismiss the results without credible integrity controls.

**Why it matters:**
- The moment you announce "we do technical assessments," employers ask
  "how do you prevent cheating?"
- Every assessment platform that has failed to answer this question has
  lost enterprise deals.
- AI-assisted cheating (Copilot, ChatGPT) has made this an existential
  problem for the entire assessment industry. It is *the* differentiator
  for trusted assessments in 2026.

**How to close it:**

Three layers, shippable independently:

**Layer A — Environment Signals** (must ship with Phase 2b)
- Track copy/paste events in the code editor (Judge0 sandbox)
- Track tab-switching / window-blur count
- Track time-on-first-keystroke (unusually fast = suspicious)
- Record submission velocity (chars/minute, edits, idle gaps)
- Persist signals to `charvak_career_assessment_signals`
- Surface a "Trust Score" alongside the assessment result

**Layer B — Question Design** (design principle, applied during Phase 2b)
- Every coding question requires reasoning, not lookup
  - E.g. "Given this buggy code and this failing test, identify the root cause"
  - Not: "Write a function that sorts a list"
- AI-resistant prompts: require explaining *why*, not just *what*
- Randomized variables per candidate (e.g. different test inputs)
- Deferred-solution design: no single "correct answer" fits every AI prompt

**Layer C — Behavioral Analytics** (post-Phase-2b, Session 18+)
- Cross-candidate patterns: same question answered suspiciously fast across users
- Plagiarism detection via embedding similarity on free-text answers
- Retake integrity: a 40-point score jump in 24 hours is flagged, not hidden

**Effort:** 1-2 sessions for Layer A; Layer B is a design habit; Layer C is
Session 18+.

**Success metric:** Verified candidates have a "Trust Score" badge. Employers
can filter by minimum trust. Retake-jump anomalies are flagged in the admin
dashboard.

**Implementation sketch — Layer A:**
```javascript
// templates/ai-assessment.html — during the coding/SQL format
let signals = {
    tab_switches: 0,
    copy_paste_events: 0,
    first_keystroke_ms: null,
    total_keystrokes: 0,
    start_ts: Date.now(),
};
window.addEventListener('blur', () => signals.tab_switches++);
editor.on('paste', () => signals.copy_paste_events++);
editor.on('change', () => {
    if (signals.first_keystroke_ms === null) {
        signals.first_keystroke_ms = Date.now() - signals.start_ts;
    }
    signals.total_keystrokes++;
});
// On submit: send signals with the answer payload
```

```python
# career_assessment_engine.py
def compute_trust_score(signals, question_count):
    """
    0-100. Higher = more trustworthy.
    Penalties: tab switches, copy-paste events, unnatural speed.
    """
    base = 100
    base -= min(30, signals['tab_switches'] * 5)
    base -= min(30, signals['copy_paste_events'] * 10)
    # Implausibly fast: first keystroke under 3s on a hard problem
    if signals['first_keystroke_ms'] and signals['first_keystroke_ms'] < 3000:
        base -= 15
    return max(0, base)
```

---

### Gap 2 — Multilingual Voice AI (Documented, Session 20+)

**What's missing:**
Charvak has 34 written languages but no voice modality. Competitors like
Hunar.AI and Vahan.ai run voice AI interviews in 20+ Indian languages and
are already winning the massive frontline/blue-collar Indian market.

**Why it matters:**
- Blue-collar hiring in India is a multi-billion-rupee market.
- Voice is the primary modality for frontline workers — reading MCQ
  assessments is not realistic for that segment.
- Charvak has ElevenLabs infrastructure already; the building blocks exist.

**How to close it (Phase 1 — minimum viable):**
1. New feature: **"Voice Screening"** at `/voice-screening`
2. Flow: candidate calls a number -> IVR prompt in their language -> AI
   asks 5 questions from a role-specific question set -> answers recorded
   and transcribed via Whisper -> scored by the existing assessment engine
3. Uses ElevenLabs for TTS prompts, Whisper for STT
4. Multilingual: Telugu, Tamil, Hindi, Kannada, Malayalam first (Charvak's
   home market + Indian staffing clients)

**Effort:** 3-5 sessions (voice infrastructure, telephony, IVR, latency
optimization).

**Success metric:** 100 voice screenings completed in the first month;
average call duration under 8 minutes; candidate NPS above 40.

**Deferred to Session 20+ — do not start without a paying client on the
frontline/staffing side.**

---

### Gap 4 — AuditBot Continuous Compliance (Documented, Session 18-19)

**What's missing:**
AuditBot generates a one-time PDF report. Enterprise CISOs need continuous
monitoring with compliance dashboards. SonarQube and Snyk sell this as
recurring SaaS revenue; we sell a one-shot credit purchase.

**Why it matters:**
- Converts a one-time purchase into a subscription — the single biggest
  revenue multiplier available.
- Enterprise buyers prefer "always-on" over "run a scan."
- The Silent-Killer cron job already proved the pattern works.

**How to close it:**

**Phase 1 — Continuous mode for AuditBot** (Session 18-19)
- New tier: "AuditBot Continuous" (credits/month or INR/month)
- New table: `charvak_auditbot_repos` (email, repo_url, provider, last_scan_at)
- New cron: `auditbot-repo-scan` (every 6 hours or daily)
- New dashboard: `/my-repos` with per-repo compliance status:
  - OWASP Top 10 status (X/10 passed)
  - Findings trend chart
  - Last-scan timestamp
- Email alerts on new HIGH/CRITICAL findings

**Phase 2 — Enterprise integration** (Session 20+)
- GitHub App for PR comments (like Snyk)
- Slack / Teams integration for alerts
- SAML SSO for team access

**Effort:** 2-3 sessions.

**Success metric:** 20 repos on continuous mode within 2 months; MRR from
continuous AuditBot exceeds one-time credit revenue.

**Depends on:** AuditBot's current scan engine (exists).

---

## The Strategy — Best in Class for Global Users

### Positioning statement

> **Charvak is the best integrated platform for the Local-to-Global talent
> journey. We assess, prove, upskill, and match talent — all in one verified
> pipeline that no point solution can replicate.**

### What we say to candidates

> "Use Charvak to prove your skills with a **Role Readiness Score** benchmarked
> to global standards. Close your gaps with AI Courses and voice-enabled
> assessments in your own language. Get matched to verified global employers
> with a **trust-verified portfolio** no resume can fake."

### What we say to employers

> "Source pre-vetted, role-ready talent from India's vast talent pool. Our AI
> assessments (Career + AuditBot + Voice) give you **integrity-verified proof
> of skill**, not just a resume. Every candidate's readiness is measurable and
> every assessment is anti-cheat hardened."

### The loop we own

    Candidate                 Employer
       |                         |
       v                         v
    [Career Assessment]  <--  [Job Requirement]
       |                         |
       v                         |
    [Role Readiness]  ---------->|
       |                         |
       v                         |
    [AI Course path]             |
       |                         |
       v                         |
    [Verified Certificate] ----->|
       |                         |
       v                         v
    [Premium Report]  ----->  [Hire]

Every arrow in that diagram is a Charvak feature. No competitor has all of
them.

### Metrics we track to know we're winning

| Metric | Target | Current baseline |
|---|---|---|
| Career Assessment completions/month | 1,000 | Track from next month |
| Readiness certificates shared/month | 300 (30%) | Zero today |
| Verified candidates with Trust Score >= 80 | 500 | Zero today |
| Premium Reports generated/month | 100 | Zero today |
| Continuous AuditBot repos | 20 | Zero today |
| Voice screenings/month | 100 | Not shipped |
| Employer outreach with Charvak verification referenced | 20/month | Zero today |

---

## Session-by-Session Roadmap

| Session | Scope | Effort |
|---|---|---|
| **17** | Role Readiness Score + Anti-Cheating Layer A + Career Assessment Phase 2b (coding/SQL via Judge0) | 2-3 days |
| **18** | AuditBot Continuous Phase 1 (repo scanner + dashboard + cron) | 1-2 days |
| **19** | AuditBot Continuous Phase 2 (GitHub App + Slack alerts) + Anticheat Layer C (behavioral analytics) | 2-3 days |
| **20** | Multilingual Voice Screening — infrastructure + Telugu pilot | 3-5 days |
| **21** | Voice Screening — expand to 4 more languages + candidate experience | 2-3 days |
| **22+** | Enterprise integrations, employer-side verification portal, further growth | ongoing |

---

## What we do NOT do

- **Don't compete on breadth.** TestGorilla has 400+ tests. We have 8 formats
  but the readiness + integrity layer makes ours fundamentally different.
- **Don't build a general-purpose HCM.** Darwinbox and Rippling are trillion-
  dollar companies. We partner with them (data export), not against them.
- **Don't build a full SAST engine.** Snyk and SonarQube have hundreds of
  engineers. We build the *workflow* layer (AI fixes + continuous monitoring)
  that complements their engines.
- **Don't chase enterprise sales yet.** Land SMEs and Indian staffing clients
  first. Enterprise trust features (Gap 4 Phase 2) come after traction.

---

## The Bet

Our bet: **in 18 months, the ability to prove skill integrity end-to-end
will be the single most valuable thing in the talent market.** AI-assisted
cheating has broken every existing assessment platform. Every employer
knows it. Nobody has solved it.

We have all the pieces: assessment, benchmark, integrity signals, verified
certificates, employer matching. All we have to do is wire them together.

The Premium Report we shipped in Session 16 is the first artifact of that
vision — a paid, employer-shareable, AI-generated, integrity-backed deep
analysis. Every future session should extend that pattern.

**2026-10-04 — Session 16 close.**

---

## The Proof Layer - Sprints A through D (added 2026-10-04)

The strategic analysis identified four gaps (Role Readiness, Anti-Cheating,
Voice AI, Continuous Compliance). Execution framework: four sprints that
connect what already exists in the codebase rather than build new subsystems.

### Gap 6 - The "Where Are They Now" Data Story (NEW)

**What's missing:** No public proof that the assessment predicts on-job
success. Employers trust scores only when they see correlation with hires
who worked out.

**How to close:** Sprint C. Public `/outcomes` page with anonymized
interview/offer rates by readiness score band. Sample-size floor of 50
applications before publishing.

**Why it matters:** Credibility flywheel. Every blog post, LinkedIn share,
and investor conversation can start with the correlation number.

### Gap 7 - Vernacular Voice Assessment (Priority: Sprint D)

**What's missing:** Written MCQ is a barrier for students whose primary
medium is Telugu / Tamil / Kannada / Malayalam. Competitors are Hindi-
English bilingual at best.

**How to close:** Sprint D. Voice-based version of the same Role Readiness
Certificate, delivered by phone call, in 5 languages first.

**Strategic note:** Voice ships AFTER the written certificate (Sprint A)
because voice produces the SAME certificate URL. Doing voice first gives
voice certificates that nobody shares and no jobs to apply to.

---

## Sprint Framework - Proof Layer

| Sprint | Deliverable | Effort | Depends on |
|---|---|---|---|
| **A** | Free Role Readiness Certificate + shareable URL at `/readiness/{id}` | 2-3 sessions | Nothing |
| **B** | `/my-jobs` - verified job matching; applications carry certificate_id | 2 sessions | Sprint A live |
| **C** | `/outcomes` - public anonymized data story | 1-2 sessions | Sprint B has >=50 apps |
| **D** | Voice readiness check in 5 Indian languages | 3-5 sessions | Sprint A live |

### Why this order

1. Sprint A produces a shareable URL - the traffic driver
2. Sprint B makes the certificate USEFUL (unlocks jobs)
3. Sprint C makes the certificate TRUSTED (employer proof)
4. Sprint D extends REACH to non-English-medium students

Each sprint produces an acquisition artifact that the next one builds on.

---

### What already exists to build on

The four sprints do not require new subsystems. They connect:

- `career_assessment_engine.py` (900 lines, 8 formats, 106 roles)
- `ability_engine.py` (Elo math, per-skill baselines)
- `charvak_career_assessments` + `charvak_career_assessment_answers` (live)
- `charvak_jobs`, `charvak_applications`, `charvak_career_saved_jobs` (live)
- `charvak_candidates` (with existing `skill_score` field)
- `charvak_badges` + `/badge` route (public artifact precedent)
- `Premium Report` product (Session 16) - PDF/email/share pattern
- 34 languages in `global_config.LANGUAGES` (written)
- ElevenLabs + Whisper (already in stack)
- `charvak_career_interviews`, `charvak_career_offers` (outcome tracking)

The gap is not capability. It is connection. Every sprint wires existing
tables and routes into one candidate-facing loop.

---



Keep this doc updated after every session. It is the north star.
