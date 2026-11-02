# Session 102 - Candidate Dashboard - FLAGGED

**Flagged:** 2026-10-30 (Session 101 close)
**Status:** NOT STARTED - deferred until trigger fires
**Purpose:** Self-serve candidate dashboard at /career-dashboard

---

## TL;DR

Build this ONLY after:
- 3 Signal Emails sent to VIT, NIT Trichy, BITS
- Amrita intro ask sent
- At least 2 days elapsed since emails went out
- AND at least 1 paying customer exists

Do NOT build in the dark. The dashboard does not create demand. Emails do.

---

## Trigger to Build

Build Session 102 when ANY of these happen:

1. First paying customer signs (Amrita or any institution)
2. First employer pays for candidate access
3. 3+ institutions have replied "build it" to the Signal Email
4. A candidate emails asking "what do I do next?"

Do NOT build because it is "on the roadmap."

---

## What Session 102 Builds (When Triggered)

### Goal

/career-dashboard - one page showing:

1. Current state (score, tier, readiness, cert count, public toggle)
2. Next 3 steps (rule-based recommendations)
3. Matched roles (skill overlap scoring)
4. Recruiter activity (defer to v2 if no view tracking)

### Effort

1 session (~3-4 hrs)

### Dependencies

All data exists. No new tables required for v1.

---

## Files to Touch

| File | Change | Effort |
|---|---|---|
| career_dashboard_engine.py | New file ~150 lines | 1 hr |
| main.py | New route ~15 lines | 10 min |
| templates/career-dashboard.html | New template ~250 lines | 1.5 hrs |
| templates/base.html | 1 nav link line | 2 min |

Total: ~3-4 hours

---

## Next 3 Steps - Rule Logic

Simple if/then rules, no ML:

- If tier is foundation or developing: push "add 1 more cert"
- If no readiness cert in 60 days: push "take fresh readiness check"
- If profile not public: push "make visible to recruiters"

Return max 3 steps.

---

## Match Scoring - v1

Simple skill overlap:

- candidate_skills: from assessment topic tags
- role_skills: from charvak_client_roles.skills_required
- match_pct = overlap / role_skills * 100

v2 (later): Use jd_parser_engine.parse_jd() for richer matching.

---

## What NOT to Build in Session 102

- Recruiter view tracking (defer to v2)
- ML-based role matching
- Progression chart (Session 103)
- Course completion integration
- Role taxonomy expansion
- Notification engine

Session 102 is ONE feature: the dashboard page. Nothing else.

---

## The Data Contract

The dashboard returns this JSON shape:

- candidate: email, handle, tier, charvak_score, readiness_score, cert_count, is_public
- next_steps: array of max 3 items, each has type, title, impact, action_url
- matched_roles: array of max 5 items sorted by match_pct DESC, each has role_id, title, company, match_pct, apply_url

---

## How to Verify When Built

1. Login as test user with passport
2. Navigate to /career-dashboard
3. Verify current score, tier, readiness show correctly
4. Verify at least 1 next step appears
5. Verify matched roles ordered by match_pct DESC
6. Verify clicking apply navigates to /open-roles/ROLE-ID
7. Verify nav dropdown shows new link
8. Login as user WITHOUT passport
9. Verify graceful empty state ("take your first assessment")

---


## Why Deferred

Per Session 101 close (2026-10-30):

- 0 paying customers
- 0 real placements
- 0 institutions replied "build it" yet
- 3 Signal Emails ready but not sent
- Amrita pilot awaiting response

Building Session 102 before any signal exists means:

- 3-4 hrs spent on a page nobody visits
- Zero customer conversations generated
- Delay on the ONE thing that matters (emails out)

The dashboard is enrichment. The emails are demand generation.

Ship the emails first. Then build the dashboard.

---

## When Trigger Fires - How to Start

1. Read this file (5 min)
2. Check EMAILS-LOCKED.md (follow-ups needed?)
3. Confirm data exists: SELECT COUNT(*) FROM charvak_passports WHERE is_public = TRUE
4. If count >= 21: proceed. If under: seed first.
5. Build the 4 files listed above
6. Test with charvak-admin-0b61
7. Commit + push
8. Verify on prod

---

## The Gate (Answer Before Building)

- [ ] 3 Signal Emails sent (VIT, NIT Trichy, BITS)
- [ ] Amrita intro ask sent
- [ ] Render password rotated
- [ ] At least 2 days elapsed since emails sent
- [ ] At least 1 of the trigger conditions is true

If any box is unchecked, do not build. Finish the gate tasks first.

---

## Related Flags

- INVERTED-MARKETPLACE-FLAG.md - Sessions 102-104 full plan
- EMAILS-LOCKED.md - The 12 emails to send first

---

**Last updated:** 2026-10-30 (Session 101 close)
**Next review:** 2026-11-15 (2 weeks after emails sent)
**Or immediately if:** trigger condition fires
