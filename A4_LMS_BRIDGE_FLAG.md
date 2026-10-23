# A4 LMS BRIDGE — FLAGGED FOR NEXT SESSION

**Flagged:** 2026-10-24 (Session 81 close)
**Status:** NOT STARTED
**Trigger:** First institution that says "we already have Moodle/Canvas"

## What A4 Solves

Objection #4 from TPO discovery: "We already have an LMS"

The answer isn't to replace Moodle — it's to plug into it.

## 3 Pillars

### 1. CSV Bridge (1 session, ~3-4 hours) — BUILD FIRST
- Generic CSV export/import (works for any LMS)
- Attendance import (student roster upload)
- Grade export (assessment scores)
- Manual trigger UI in admin
- No external dependencies

### 2. Google Workspace SSO (2 sessions, ~8-10 hours)
- OAuth2 integration with Google Cloud project
- "Sign in with Google" for students
- Auto-enroll based on Google Classroom group
- SAML option for institutions that require it
- Requires: Google Cloud project, OAuth credentials, redirect URI whitelist

### 3. Moodle Plugin (2 sessions, ~8-10 hours)
- PHP plugin installed in institution's Moodle
- Adds "Charvak" activity type
- Syncs assessments as Moodle activities
- Grades flow back to Moodle gradebook
- SSO via existing Moodle session
- Requires: PHP dev environment, live Moodle instance for testing

**Total: ~20-25 hours (~5 sessions)**

## Recommended Build Order

1. **CSV bridge** — no external deps, ships value immediately
2. **Google SSO** — most-requested auth method
3. **Moodle plugin** — most-common Indian LMS

## Trigger to Build

Build when ANY of these happen:
- First paying institution asks "how do we integrate with our LMS?"
- OR first institution says "we won't adopt a new platform"
- OR first institution uses Google Classroom (very common in tier-1 colleges)

**Until then: A4 is flagged, not started.**

## Important Constraints

- **Moodle plugin** needs real Moodle instance — generic testing doesn't work
- **Google SSO** needs Google Cloud project — OAuth consent + redirect URIs
- **CSV bridge** is safe to build blind — standard format

## Alternative: Skip A4

If no institution asks for LMS integration in the next 30 days, redirect A4 effort to:
- Polish A1 v0.4 (referral status UI, employer dashboard filters)
- Build Dean frontend UI (needed when first paying client arrives)
- OR start Phase B (placement tracking, co-branding engine)

A4 is a "when they ask" item, not a "build because it's on the roadmap" item.

## Current Phase A Status (as of 2026-10-24)

| Item | Status |
|---|---|
| A1 — Employer Network | v0.3 SHIPPED (public page + referral + signup + admin approval) |
| A2 — Proof Dashboard | Backend 100%, Dean PDF live, frontend deferred |
| A3 — Engagement Dashboard | v1.0 SHIPPED (streaks, badges, leaderboard, preferences) |
| A4 — LMS Bridge | NOT STARTED (this flag) |

**3 of 4 Phase A items shipped.**

---

**Last updated:** 2026-10-24 (Session 81 close)
**Next review:** When an institution asks for LMS integration, OR 2026-11-24