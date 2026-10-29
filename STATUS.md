# Charvak IT Consulting - Project Status

# Charvak IT Consulting - Project Status

**Last updated:** 2026-10-30 (Session 101 - privacy fix shipped)
**Version:** v3.12-session-101-20261030
**Live:** https://www.charvakit.com
**HEAD:** a859b21

## Session 101 - COMPLETE (2026-10-30)

### Privacy-first recruiter visibility

BREAKING BEHAVIOR CHANGE: New passports default to is_public=FALSE.

- Migration: migrations/20261030_passport_privacy.sql
- Engine: set_visibility() + get_visibility() + owner bypass
- Routes: POST/GET /api/passport/visibility
- UI: toggle card on /passport/handle (owner-only)
- Verified on prod: 21 public profiles preserved, routes live, no regressions

### Flagged - Inverted Marketplace (Sessions 102-104)

See INVERTED-MARKETPLACE-FLAG.md. Deferred until paying customer exists.

### What is queued

- Amrita email -> Monday
- Render Postgres password -> Weekend
- One-pagers to 5 universities -> Monday
- Email Mismatch Auto-Link Flow -> ~2 hrs, deferred

---



**Last updated:** 2026-10-24 (Sessions 79-81 — 3 Phase A products shipped)
**Version:** v3.10-session-81-20261024
**Live:** https://www.charvakit.com
**HEAD:** 3243675

## Session 81 — COMPLETE (2026-10-24)

### Phase A items shipped

**A1 — Employer Network v0.3**
- Public `/employers` page showing 8 real CBREX roles (NCS, LENZE, Middle East Group, via Charvak)
- `/employer/signup` self-service form
- `/employer/refer/{role_id}` candidate referral
- `/admin/employer-accounts` admin approval queue
- `charvak_employer_accounts` + `charvak_employer_referrals` tables
- Email notifications via email_engine

**A2 — Proof Dashboard (Backend 100%)**
- `charvak_certificate_views` table
- `university_engine.get_proof_dashboard()` full aggregation
- `pdf_engine.render_dean_report_pdf()` — 4-page Dean-ready PDF
- `/api/proof-dashboard/{id}` + `/api/proof-dashboard/{id}/pdf`
- 3 institutions seeded: Amrita, VIT, NIT Trichy
- Frontend UI deferred (see DEAN_REPORT_FRONTEND_FLAG.md)

**A3 — Engagement Dashboard v1.0**
- `engagement_engine.py` (13.6 KB) — unified aggregation
- `/student/engagement` full dashboard (streak, badges, leaderboard)
- 9 badge types with milestone auto-award
- `charvak_student_preferences` + `charvak_student_badges` + `charvak_engagement_events` tables
- Global leaderboard using real passport scores
- Email nudges ready via `send_engagement_nudge`

### Live URLs
- `/employers`, `/employer/signup`, `/employer/refer/{role_id}`
- `/admin/employer-accounts`
- `/student/engagement`
- `/api/proof-dashboard/{id}`, `/api/proof-dashboard/{id}/pdf`
- `/api/employers/stats`, `/api/student/leaderboard`

### Database additions
6 new tables, 3 extended tables

### Monday priorities
1. Rotate Render Postgres password
2. Send Amrita follow-up with 3 artifacts
3. Next: A4 LMS Bridge OR polish A1 v0.4 OR Dean frontend

---
# Charvak IT Consulting - Project Status

**Last updated:** 2026-10-24 (Sessions 79-80 — enterprise sales package + 3-pillar homepage)
**Version:** v3.9-session-80-20261024
**Live:** https://www.charvakit.com
**HEAD:** 707996c

## Sessions 79-80 — COMPLETE (2026-10-24)

### Flags Closed
- ✅ Flag 1: Amrita email sent to Prof. Raj Oct 23 19:54 (3 PDFs attached)
- ✅ Flag 3: GPT-4o env flip verified (7/7 tests, JD parse + auth gate + 6 endpoints)
- 📅 Flag 2: Render Postgres password rotation (Monday)

### Track A: 5 Enterprise One-Pagers
Location: `C:\Users\lenovo\OneDrive\Desktop\Charvak_Enterprise_Package_20261023\`
- 01-university-portal.pdf (4 KB)
- 02-cas-api.pdf (3.7 KB)
- 03-trust-score-api.pdf (3.6 KB)
- 04-staff-augmentation.pdf (3.8 KB)
- 05-b2c-enterprise-license.pdf (3.5 KB)
- Charvak_Enterprise_Package.pdf (17 KB — 10 pages, all 5 combined)

### Track B: 3-Pillar Homepage Rewrite
Commit: `707996c` (136 insertions, 106 deletions)
- Hero: "The AI Verification Layer for Global Talent"
- 3 pillars: For Learners / For Universities / For Employers (color-coded)
- Each pillar: 5 feature bullets + 2 CTAs
- Proof bar: 138 exams, 12.5K questions, 34 languages, 8 AI engines
- Featured products: Career Assessment, CAS API, Staff Augmentation
- Softened "48-hour placement" → "48-hour match/shortlist" (defensible claim)

### Track C: Docs Sync
Commits: `6c95809` (gitignore), `2dad2ed` (session 79 close-out)

### Prod State
- Cert RDC-DEMO2026SAMPLE (Priya S., 78/100, full skill breakdown)
- 21 public passports seeded (source=demo_sample)
- Homepage live with 3-pillar layout
- GPT-5.4-nano + gpt-5.4-mini serving all AI

### Monday To-Do (2 min)
1. Rotate Render Postgres password
2. Verify homepage 200
3. Send 5 one-pagers to 5 universities (outbound)

---

# Charvak IT Consulting - Project Status

**Last updated:** 2026-10-23 (Session 78 - email gate + nav redesign live)
**Version:** v3.8-session-78-20261023
**Live:** https://www.charvakit.com
**HEAD:** db6978b

## Session 2026-10-23 (Sessions 76/77/78) - Nav redesign + email gate COMPLETE

### Shipped (verified on prod)

**Session 76 (`e6af6b0`): Nav Phase 2**
- 14 flat nav items to 5 story-driven dropdowns:
  Learn / Prove / Get Hired / For Business / Resources
- All existing links preserved
- Mega-menu CSS inline in base.html

**Session 77 (`cea4e69`): Nav gap fix**
- 12px real gap between Global Platform strip and main nav
- Nav positioned at top:53px (was overlapping strip by 9px)
- Responsive: mobile nav at top:60px

**Session 78 (`db6978b`): Email gate**
- Anonymous visitors to /readiness/{cert_id} prompted for email
- Emails stored + PDF sent via SendGrid
- Skip works (soft gate), authed users bypass
- Fixed 2 bugs: modal trapped in #rdContent + cross-IIFE ReferenceError

### Session 79 plan
1. Flag 1: Amrita email to Prof. Raj
2. Flag 3: GPT-4o env flip on Render
3. Flag 2: Rotate Render Postgres password

After these 3: zero unblocked work remains.

---

# Charvak IT Consulting - Project Status

**Last updated:** October 22, 2026 (Session 74 extended — revenue CTAs + Azure role)
**Version:** v3.7-session-74-extended-20261022
**Live:** https://www.charvakit.com
**HEAD:** 6535cec

## Session 74 Extended — COMPLETE (2026-10-22)

### Production Status (verified)

- Homepage: 200 (0.42s)
- Cert page: 200 (0.39s)
- Azure role: 200 (0.25s)
- Open roles: 200 (0.36s)
- Resume Roast: 200 (0.28s)
- Razorpay: live, working

### What Shipped Today

Bug Fixes:
- Production CSS layout failure (missing .dropdown-menu rule)
- Pre-existing backtick-n JS syntax error in readiness.html

Features:
- Certificate page CTAs (2 HTML-only links)

Business:
- Azure & Hybrid Infrastructure Engineer role posted
- 12 screening questions configured

### Backup Created

- C:\projects\Charvak_Complete_Backup_20261022_235656.zip
- 48.20 MB (677 files + 197 DB tables)
- Contains .env + .env.local (sensitive — do not share)

### Session 75 Ready

Read SESSION-CONTEXT.md for full state. Priorities:
1. Homepage CTA to /ai-assessment
2. Email capture before cert download
3. Nav Phase 2 (VS Code direct edit)

---

# Charvak IT Consulting - Project Status

**Last updated:** 2026-10-20 (Session 70 — Wave 3 100% COMPLETE)
**Version:** v3.7-session-70-20261020
**Live:** https://www.charvakit.com
**HEAD:** a016814

## Session 2026-10-20 (Session 70) — Wave 3 100% COMPLETE

**Commit:** `a016814` (S67b AI Tutor frontend)
**38 commits shipped across sessions 51-70 today.**

### S67b — AI Tutor Frontend Chat Panel

Completes Wave 3 feature B. The S67a backend now has a full frontend
that reuses the S65 chat pattern.

**templates/my-course.html (+343 lines):**
- Floating 💡 FAB button (bottom-right)
- Slide-in chat panel (top:100px, right:0, 400px wide)
- Teal header with white circular × (36px, clickable)
- Context label auto-updates on resume
- Message bubbles (user/assistant/system)
- Textarea + Send (Enter to send)
- Typing indicator
- localStorage session persistence
- Auto-resume via GET /api/ai-tutor/session/{id}

**Verified E2E:**
- Panel opens: rect.x=561, transform=translateX(0)
- Panel closes: rect.x=961, transform=translateX(400px)
- Chat works: "what week 1 covers" → 8-point response with real
  lesson content from charvak_course_lessons
- Session persists across page reload

### Wave 3: 100% Complete

| Feature | Commits | Status |
|---|---|---|
| A — Interview Prep AI depth | 2d1f1a4 + 336afbb | ✅ |
| B — AI Tutor (backend) | 581a8f9 | ✅ |
| B — AI Tutor (frontend) | a016814 | ✅ |
| C — Career Certifications | 766fb6b | ✅ |

### Platform Status — All 100%

- Wave 1 + Wave 2 ✅
- Track D Phase A ✅
- UI Modernization (7/7) ✅
- Interview Prep conversational ✅
- AI Tutor (backend + frontend) ✅
- Career Certifications ✅
- GPT-4o-mini Phase 1-3b ✅
- Zero open bugs
- Zero broken features

### Only 3 Items Left (all 5-min dashboard tasks)

1. Amrita email to Prof. Raj
2. Rotate Render Postgres password
3. Phase 3c env flip (Nov 3 target)

**After these: zero unblocked work remains.**

---
## Session 2026-10-20 - Sessions 65 + 67a + 69 Complete

**Commits:** `2d1f1a4`, `336afbb`, `581a8f9`, `766fb6b`
**36 commits shipped today across sessions 51-69.**

### Sessions Closed

- **S65 - Interview Prep Conversational Mode:** Users choose Quick
  Practice (static) or Full Mock Interview (conversational, adaptive,
  up to 12 turns). AI generates real follow-ups (verified: 3-turn Data
  Scientist interview on L1/L2 regularization). Partial-session
  indicator, avg-per-turn scoring.
- **S67a - AI Tutor Persistent Backend:** Rewrote interactive_tutor.py
  from in-memory to DB-backed with course-context injection. Verified
  persistence across uvicorn restart (turn_count continued 2 → 3).
  Backend ready for S67b frontend.
- **S69 - Career Assessment Certifications:** Standalone B2C-first
  credential. Tiered by score (Certified/Expert/Elite), free ≥85,
  5 credits for 70-84. HMAC verify, PDF, dashboard, share buttons.
  Ready for Amrita students when Amrita signs (zero rework).

### Platform Status — All 100%

- Wave 1: 100%
- Wave 2: 100%
- Track D Phase A: 100%
- UI Modernization: 100%
- Interview Prep conversational: 100%
- AI Tutor backend: 100%
- Career Certifications: 100%
- GPT-4o-mini Phase 1-3b: 100%
- Zero open bugs
- Zero broken features

### Only One Unblocked Build Left

- **S67b — AI Tutor frontend chat panel** (~45 min)

### Then 3 Five-Minute Flags

- Amrita email
- Render password rotation
- Phase 3c env flip (Nov 3 target)

After these: platform at "everything unblocked is built."

---
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
**Version:** v3.7-session-70-20261020
**Live:** https://www.charvakit.com
**Status:** Track A active. Track B flagged.

## Session 2026-10-12 - Session 43

**HEAD:** a016814

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

**HEAD:** a016814
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

**HEAD:** a016814
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
