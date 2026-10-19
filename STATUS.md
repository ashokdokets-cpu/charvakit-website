# Charvak IT Consulting - Project Status

**Last updated:** 2026-10-20 (Sessions 63-64b - Track D + CAS complete)
**Version:** v3.5-session-64b-20261020
**Live:** https://www.charvakit.com
**HEAD:** 2cff7e2

## Session 2026-10-20 - Sessions 63-64b Complete

**Commits:** `bb0ecea` (S63), `ef5974f` (S64), `2cff7e2` (S64b)
**31 commits shipped today across sessions 51-64b.**

### Sessions Closed

- **S63 - Track D Phase A 100%:** JD parser wired into Career Assessment
  ("I have a JD" toggle + fuzzy-match prefill + CTA URL params)
- **S64 - CAS Admin UI backend:** list_api_keys gets search + sort;
  /api/admin/cas-keys/list accepts params; new /list.csv route
- **S64b - CAS Admin UI frontend:** Toolbar (search + sort + CSV),
  bulk selection + approve, 6 gated patches with node --check

### Platform Status

- Wave 1: 100%
- Wave 2: 100%
- Track D Phase A: 100%
- UI Modernization: 100%
- CAS backend + frontend: 100%
- GPT-4o-mini Phase 1-3b: 100%
- Zero open bugs
- Zero broken features

### Remaining (all 5-min tasks)

- Amrita reply to Prof. Raj
- Rotate Render Postgres password
- Phase 3c env flip (Nov 3 target)

---
## Session 2026-10-19 - Sessions 52-54 Complete

### Wave 2 Complete (Sessions 50-52)

- Trust Score Public API (`/api/passport/{handle}/verify`)
- Employer Dashboard (`/employer/dashboard`, `/employer/verify/{handle}`)
- Certificate-as-a-Service (`/employer/cas`, `/api/cas/verify-batch`)
- CAS Admin UI (Session 53: `/admin/cas-keys`)

### GPT-4o-mini Migration (Sessions 53-54)

- Phase 1: Centralized in global_config (S43)
- Phase 2: Evaluated 5 candidates, chose gpt-5.4-nano + gpt-5.4-mini
- Phase 3a: openai_compat shim + ai_service.py (S53)
- Phase 3b: All 10 files migrated (S54) — 36 call sites total
- Phase 3c: Env var flip (pending, target Nov 3)

### Employer Dashboard Polish (Session 54)

- Sort dropdown (score/recent/handle)
- CSV export (up to 1,000 rows)
- Empty-state CTA to /readiness-check

### Wave 1 Complete (Sessions 46-48)

- Career Passport, Skill Twin Challenges, Daily Drills, Cohort Mode

### Site Health

- Prod: all endpoints 200
- 192 tables live
- 89+ migrations clean
- Pre-push hook: 14/14 IELTS relevance checks
- Zero open bugs
- 2 cosmetic flags (deploy.yml Python version, Render password)

### Remaining Work

**Immediate (5 min each):**
- Send Amrita reply to Prof. Raj
- Rotate Render Postgres password
- Fix deploy.yml Python 3.9 -> 3.11

**Next Session:**
- Phase 3c: Flip env vars on Render (Nov 3 target)
- Track D (JD2P) — after Amrita pilot Week 2

---
## Session 2026-10-13 - A1.8 + A1.9

### Shipped

- WhatsApp/LinkedIn share instrumentation across 4 templates
- Placement-prep promotion + UTM attribution
- 2 new helper functions in base.html
- 6 new GA4 events in the funnel

### Bugs fixed

- `readiness.html` share buttons were plain anchors; tracking
  wrapped in dead `rdOpenShare()` and never fired. Fixed.

### Next

- A2 (Certificate round 3) or A3 (FYP features)
- Or cleanup pass: rdOpenShare removal, PayPal E2E for A1.6

---

## Session 2026-10-13 - Session 43-A1.7

**HEAD:** `731b70a`

### Shipped

- IELTS Deep Report micro-paywall (Rs 99)
- 9 files changed, +1,885 / -1
- 4 new routes, new engine, new frontend, new PDF renderer

### Bugs fixed mid-session

- Country detection returning full names
- fpdf2 X-drift crash on multi_cell after cell
- EmailEngine.send_email signature mismatch
- PDF header showing "Charvak Premium Report"

### Next

- A1.8 (WhatsApp loop) or A2 (Certificate round 3)
- A1.6 country-code cleanup (5 min)
- Prod smoke test after deploy

---

# Charvak IT Consulting - Project Status

**Last updated:** 2026-10-12 (Session 43 - FYP MBA calibration + integrity fact panel)
**Version:** v3.5-session-43-20261012
**Live:** https://www.charvakit.com
**Status:** Track A active. Track B flagged.

## Session 2026-10-12 - Session 43

**HEAD:** 3fd8ad7

Two commits, four real fixes, one flagship feature.

### Shipped

- Integrity fact-panel certificate redesign (facts, not verdicts)
- FYP discipline-aware topic generation (MBA/commerce support)
- 8 MBA courses generated and promoted to public catalog
- MBA role calibration verified for 5 roles

### Commits

- e6daf79 — feat(integrity): fact-based certificate panel + reweighted classifier
- 3fd8ad7 — feat(fyp): discipline-aware topic generation - MBA/commerce support

### Site health

- 182 page routes: all 200 or legit redirect
- 155 API routes: all reachable
- 0 broken buttons
- 0 hidden elements without unhide logic
- 0 HTTP 500s

### Meeting prep

- Charvak-TPO-Demo folder with 7 PDFs on Desktop
- Amrita CDC meeting pending confirmation

### Next

See TRACK-A-B-PLAN.md for the full sequence.

**Track A batches:**
- A1: Small cleanup (45 min)
- A2: Certificate round 3 (1 session)
- A3: FYP features (1 session)
- A4: Personalized training views (1 session)
- A5: DoketsRB sync (2 sessions)

**Track B stages (after A2):**
- B1: Vocational calibration proof
- B2: CSR Assessment API
- B3: Pilot with one TP
- B4: First paid contract

**Estimate:** Track A ~6-7 weeks. Track B ~4-5 months.

<!-- BEGIN SESSION-48 -->

## Session 2026-10-18 - Session 48 (Cohort Mode)

**HEAD:** 1399073
**Wave 1:** 100% complete

### Shipped

- Cohort Mode (batch leaderboards)
- 8 routes, 3 tables, 2 templates
- base.html nav + footer links
- passport.html "My Cohorts" section

### Verified

- /cohorts returns 200 on prod
- /cohorts/{id} returns 200 on prod
- /passport/{handle} renders "My Cohorts" for owner
- Migration 20261018_cohorts.sql applied automatically
- Pre-push hook passes 14/14

### Site Health

- All Wave 1 API endpoints returning 200
- Payment API returns live credentials
- 89 migrations clean on prod

### Next

See COMMITMENT.md "Session 49 candidates" for options A/B/C/D.

<!-- END SESSION-48 -->

<!-- BEGIN SESSION-49 -->

## Session 2026-10-19 - Session 49 + 49.5 (Cohort Polish)

**HEAD:** d3de41b
**Wave 1:** 100% complete with production polish

### Shipped

**Session 49 (5525cd7):**
- 6 new engine methods (leave, rename, delete, promote, demote, discover)
- 6 new API routes
- Owner actions menu + member list + leave button + 3 modals + public discovery
- 3 critical fixes: role cache path, cache invalidation, modal placement

**Session 49.5 (d3de41b):**
- Public cohort toggle (checkbox in create modal, button in owner actions)
- is_public in create_cohort + set_cohort_visibility + get_leaderboard
- POST /api/cohorts/{id}/visibility route

### Verified

- /cohorts returns 200 on prod
- /api/cohorts/public returns 200, correct empty shape
- 14/14 pre-push checks passing (both commits)
- Full browser E2E: create, promote, demote, leave, delete, toggle visibility

### Bugs caught by E2E (not code review)

- Role missing from cache hit path (would break promote/member list)
- Cache not invalidated on join/leave (stale member count/leaderboard)
- Modals trapped in <main> (faded backdrop, would block create flow)
- is_public missing from API response (toggle label stuck at default)

### Site Health

- All Wave 1 API endpoints returning 200
- Prod healthy after both deploys
- Zero regressions on existing features
- 89 migrations applied cleanly (no new migrations this session)

### Next

See COMMITMENT.md "Session 50 candidates" for options A/B/C/D.
Recommended: A (Trust Score Public API) opens Wave 2.

<!-- END SESSION-49 -->
