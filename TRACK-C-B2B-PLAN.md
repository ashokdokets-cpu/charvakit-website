# TRACK C — B2B / University Partnership Plan

**Created:** 2026-10-13
**Trigger:** First university pilot (Amrita CDC, Nov 2026)
**Status:** Flagged, not started
**Owner:** Product roadmap

---

## Why This Exists

Track A (B2C) ships consumer features. Track B (CSR) is a separate
business model. Track C is B2B university partnerships — the
institutional side of the platform.

Track C activates when the first university signs a pilot. Currently
that's Amrita CDC (meeting 15 Oct 2026).

---

## Ground Truth (as of 2026-10-13)

### What EXISTS today

| Component | Status |
|---|---|
| Mock drives with 18 company-specific patterns | ✅ Live |
| Role Readiness Certificate (HMAC-signed) | ✅ Live |
| Career Assessment (106 roles × 66 industries × 7 levels) | ✅ Live |
| AI courses (25 catalog) + custom course designer | ✅ Live |
| Credit system | ✅ Live |
| Public certificate verification | ✅ Live |
| University subscription flow (3 tiers) | ✅ Live |
| `add_student`, `record_outcome` | ✅ Live |
| `get_first_destination_report` (placement outcomes) | ✅ Live |
| `get_university_dashboard` (roster + placement) | ✅ Live (basic) |

### What DOES NOT exist today

| Component | Status |
|---|---|
| Bulk cohort invite link | ❌ Not built |
| Credit-grant script | ❌ Not built |
| Aggregate readiness dashboard | ❌ Not built |
| Weekly report generator | ❌ Not built |
| Per-student delta script | ❌ Not built |
| Bulk CSV student onboarding | ❌ Not built |
| Placement-outcome tracking (interview/offer pipeline) | ❌ Not built |
| Employer-facing verification portal | ❌ Not built |
| Annual impact report generator | ❌ Not built |
| SSO integration | ❌ Not built |

**Honest framing:** the readiness engine is world-class. The institutional
wrapper (cohort management, reporting, dashboards) is not built.

---

## What We Need to Build (Track C Roadmap)

### Phase 1 — Pilot Infrastructure (~5 hours)

**Trigger:** University says yes to a pilot.

| # | Build | Effort | Purpose |
|---|---|---|---|
| C1 | Cohort invite link (`/pilot/{cohort_id}`) | 30 min | Bulk signup tracking |
| C2 | Credit-grant script (`scripts/grant_cohort_credits.py`) | 30 min | N credits × M students |
| C3 | Weekly report generator (`scripts/weekly_cohort_report.py`) | 2 hrs | Aggregate PDF per week |
| C4 | Per-student delta script (Week 1 vs Week 4) | 1 hr | Progress tracking |
| C5 | Kickoff email template | 1 hr | Student onboarding email |

**Total:** ~5 hours. Doable in one day when a pilot is confirmed.

### Phase 2 — Cohort Dashboard (~11 sessions)

**Trigger:** Pilot completes successfully; university wants year-round.

| # | Build | Effort | Purpose |
|---|---|---|---|
| C6 | Bulk CSV import | 1 session | Roster onboarding |
| C7 | Cohort dashboard v1 (aggregate view) | 2 sessions | CDC admin UI |
| C8 | Per-student tracking (multi-week) | 2 sessions | Progress dashboard |
| C9 | Department/batch filtering | 1 session | Segment the cohort |
| C10 | Weekly automated reports (email) | 1 session | No manual sending |
| C11 | Placement tracking (offer letters) | 2 sessions | Extend current outcome tracker |
| C12 | Employer portal (bulk verification) | 2 sessions | B2B verification |

**Total:** ~11 sessions (~5-6 weeks of work).

### Phase 3 — Scale (Year 2+)

**Trigger:** 3+ universities signed.

| # | Build | Effort |
|---|---|---|
| C13 | SSO integration (Google Workspace / SAML) | 2-3 sessions |
| C14 | Custom analytics per university | 2 sessions |
| C15 | Annual impact report generator | 1 session |
| C16 | API access for university IT | 2 sessions |
| C17 | Mobile app (optional) | 5+ sessions |
| C18 | Multi-campus support | 2 sessions |

**Total:** ~15-20 sessions.

---

## Critical Design Decisions (to be made when we build)

1. **Multi-tenant vs single-tenant per university?**
   Recommendation: Single-tenant with `university_id` column. Multi-tenant is over-engineering for the first 5 customers.

2. **SSO creates students, or we pre-create?**
   Recommendation: Hybrid. CSV import for pilot; SSO for year 2.

3. **Where does the aggregate dashboard live?**
   Recommendation: `/university/{university_id}/dashboard` — extends existing route.

4. **Custom university branding?**
   Recommendation: Defer to Phase 3. Certificate already supports `document_title`.

5. **Free credit policy per student, per year?**
   Recommendation: 100 credits per student per academic year (~₹5,000 cost at ₹0.50/credit). Bundled into license.

---

## Commercial Model (locked)

| Tier | Students | Annual price | Notes |
|---|---|---|---|
| Pilot | 100-500 | ₹0 | 4 weeks |
| Department | ≤ 500 | ₹49,999/yr | 1 dept, basic dashboards |
| Campus | ≤ 5,000 | ₹1,99,999/yr | Full dashboards, co-branded certs |
| University | Unlimited | ₹4,99,999/yr | All campuses, SSO, priority |

**Add-ons:**
- SSO integration: ₹1,00,000 one-time
- Custom branding: ₹25,000/yr
- Employer portal: ₹50,000/yr
- On-campus training: ₹15,000/session

---

## Success Metrics (Track C)

| Metric | Target |
|---|---|
| Universities signed (pilot) | 1 by Dec 2026 |
| Universities signed (paid) | 3 by Jun 2027 |
| Annual revenue (Track C) | ₹6L by Dec 2027 |
| ARR per university | ₹2L average |

---

## The One-Paragraph Strategy

Track A pays the bills. Track C builds enterprise credibility. Together
they justify the "Local-to-Global talent pipeline" narrative. The first
university pilot (Amrita) is free — the goal is to learn what the CDC
office actually needs, then build the institutional wrapper with their
input. If Amrita converts, we have the reference for 20 more Indian
universities.

---

**Keep this file in sync as Track C evolves.**