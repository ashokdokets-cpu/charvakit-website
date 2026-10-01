# Session Context - Charvak

**HEAD:** `abd653d`
**Last updated:** 2026-10-02 (Session 8 complete - University + Legacy-Shift shipped, C7 17/17)
**Version:** `v3.5-session-8-20261002`

---

## Where we are

Session 8 closed the C7 gap entirely. Every product page that advertised
a paid tier now has a real credits-based purchase flow.

**Commits this session:**
- `2d600f3` feat(university): real subscription flow + security fix
- `abd653d` feat(legacy-shift): ship Rs 4,999 full migration plan tier

### Shipped this session

**University Portal (Rs 19,999 / 49,999 / 99,999 per year)**
- Fixed a security bug: `/api/university/register` was fully open
  (anyone could register a university for any admin_email)
- Removed a shadowing script block that hijacked `registerUniversity`
  and just called `notifyMe`
- New table `charvak_university_subscriptions` (tier, price_inr,
  credits_used, expires_at 365 days)
- New route `POST /api/university/subscribe` (auth + credits)
- Credit tiers (Rs 5/credit):
  - university_starter: 4000 (Rs 19,999/yr)
  - university_growth: 10000 (Rs 49,999/yr)
  - university_enterprise: 20000 (Rs 99,999/yr)
- Frontend: 3 tier buttons wired to `chooseTier(tier)` which registers
  the university (if needed) then subscribes
- Verified E2E: UNI-EA076ACA, tier=starter, 20000 -> 16000, DB row with
  2027-10-02 expiry

**Legacy-Shift (Rs 4,999 migration plan)**
- Free analysis (25 cr) already worked. Migration plan tier was missing.
- New credit key `legacy_shift_migration: 1000`
- New route `POST /api/ai/legacy-shift-migration-plan` (auth + credits)
- OpenAI call returns file-by-file plan + data migration steps +
  test plan + rollback + post-launch checklist
- New table `charvak_legacy_shift_reports`
- Frontend: "Get Full Migration Plan" card appears after free analysis
  renders, with `getMigrationPlan()` + `Copy JSON`
- Verified E2E: LS-225427023418, 16000 -> 14975 (25 + 1000 exact), DB
  row created

### C7 COMPLETE (17/17 templates)

| Session | Templates |
|---|---|
| 3 | AuditBot |
| 4 | Lock-In Breaker |
| 5 | Micro-Squads |
| 6 | Developer Entropy, AI-Slop, Design-Token, Geo-Compliance, Agency-Twin, Reverse Staffing, Bridge, Marketing AI, Team Dashboard, Background Verification |
| 7 | Silent-Killer (honesty), Skill-Twin AA4d, LMS, Hosted booking page |
| 8 | University, Legacy-Shift |

Every paid tier across the product suite is now either:
- A real credits-based purchase flow (backend + frontend + persistence), or
- A notify-me interest capture for features not yet built

---

## Known issues from this session

- **Line length limit reached during chat.** Session 8 spanned two chat
  windows. Full detail is in the two chat exports.

---

## Recommended next session

**Session 9 - Silent-Killer real cron (~4-6 hrs)**

The honesty rewrite in Session 7 replaced three misleading claims
("24/7 monitoring", "Instant alerts", "Auto-hotfix") with a real
"Notify Me When Continuous Monitoring Ships" button. Session 9 builds
the real scheduler:
- Render cron job that runs the scan daily
- Alert emails via SendGrid on new findings
- New table for scan history + alert state
- Frontend dashboard showing scan timeline

**Also queued for Session 9:**
- #3 PayPal live capture test (5 min, $2.39 + refund)
- Full doc pass on 4 trackers
- Hygiene: scripts/_*.py cleanup, git gc, ARCHITECTURE.md static
  section refresh (still references immutable Cache-Control)

---

## Environment

- HEAD: `abd653d`
- Local Python: 3.11.9 venv
- Local DB: Postgres 15 at localhost:5432
- Dev server: `uvicorn main:app --reload --port 8000`
- Prod: https://www.charvakit.com (Render auto-deploy)
- Render service: `srv-d9hhljd8nd3s73d2hoeg`

---

## Session 8 provenance

Two chat windows:
1. University patch + Legacy-Shift first attempt (missed credit key
   anchor — actual cost was 25 not 20, and the route anchor was inside
   a try block)
2. Legacy-Shift retry with corrected anchors + commit + push

Both patches verified E2E against `test-register-2026-09-24@example.com`.
