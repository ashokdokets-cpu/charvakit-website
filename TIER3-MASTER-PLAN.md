# Charvak Tier 3 — Master Completion Plan

**Created:** 2026-09-15
**Last updated:** 2026-09-17
**Status:** 6 of 10 features shipped to production
**Purpose:** Bring all 10 Tier 3 features to production-ready status
**Estimated total:** 15–20 hours across multiple sessions
**Goal:** Every Tier 3 feature persists data to Postgres, handles errors gracefully, and completes end-to-end

---

## The Core Problem (applies to all Tier 3 items)

**Every Tier 3 engine is in-memory.** Data is stored in Python lists/dicts on the engine object, so:

- Every Render restart wipes all data
- Enrollments, referrals, applications, sessions — all lost on every deploy
- Users can "use" features but nothing persists
- Same problem as credits had before Fix B

**The fix pattern (proven with `ai_credit_engine.py` — Fix B):**

1. Create Postgres tables for the feature
2. Refactor engine methods to read/write via `database.db.get_connection()`
3. Preserve exact method signatures + return shapes (so `main.py` doesn't change)
4. Add `_ensure_tables()` in `__init__` (idempotent CREATE TABLE IF NOT EXISTS)
5. Add migration script if there's existing in-memory data to preserve
6. Test locally, then deploy, then verify on prod

---

## Audit Results (2026-09-15)

| # | Feature | Engine Status | Routes | Templates | DB Tables | E2E | Priority |
|---|---|---|---|---|---|---|---|
| 1 | Job Board | IN-MEMORY | ✅ 7 | ✅ 1 | ✅ `jobs` | ⚠️ Partial | **P1** |
| 2 | Referral System | IN-MEMORY | ✅ 9 | ⚠️ 1 (no `/ref/` route) | ❌ | ❌ | **P2** |
| 3 | Interview Prep | IN-MEMORY | ✅ 4 | ✅ 1 | ❌ | ❌ | **P3** |
| 4 | University Portal | IN-MEMORY | ✅ 7 | ✅ 1 | ❌ | ⚠️ Page only | **P3** |
| 5 | Analytics Dashboards | UNKNOWN | ✅ 3 | ❌ | ❌ | ⚠️ API only | **P4** |
| 6 | AI Courses | IN-MEMORY | ✅ 10 | ✅ 1 | ❌ | ❌ | **P5** |
| 7 | Micro-Internship | IN-MEMORY | ✅ 16 | ✅ 4 | ❌ | ❌ | **P5** |
| 8 | Mock Drives | IN-MEMORY | ✅ 3 | ❌ | ❌ | ❌ | **P5** |
| 9 | Enterprise | IN-MEMORY | ✅ 15 | ❌ (404) | ❌ | ❌ | **P5** |
| 10 | WhatsApp Bot | UNKNOWN | ✅ 2 | — | ❌ | ⏸ Meta issue | **Blocked** |

---

## Execution Order (by priority + effort)

### Session 1 — Job Board E2E (2.5 hr) ✅ **COMPLETE 2026-09-15**

**Status:** ✅ Done. Tagged `v1.5-jobboard-persistent-20260915`. Verified on prod (sync version 1.1.0). Tables: `charvak_jobs`, `charvak_applications`, `charvak_synced_users`, `charvak_synced_applications`, `charvak_skill_gaps`.

**Why first:**
- Already has a `jobs` DB table — closest to complete
- Single-engine scope — no cross-dependencies
- Real business value — public job board drives traffic
- Good warmup for the pattern

**Tasks:**
1. Audit `job_board_engine.py` — understand current methods
2. Create missing tables: `charvak_applications` (job applications)
3. Refactor engine to persist:
   - `post_job(data)` → INSERT into `jobs`
   - `get_jobs(filters)` → SELECT from `jobs`
   - `apply_to_job(data)` → INSERT into `charvak_applications`
   - `get_applications(job_id)` → SELECT
4. Wire `/post-job` form → real DB write
5. Wire `/job-board` listing → real DB read
6. Test: post a job, verify it appears, apply, verify application saved
7. Commit + deploy + verify on prod

**Definition of done:**
- A job posted survives a Render restart
- A candidate's application survives a Render restart
- Both are visible in the DB via psycopg2

---

### Session 2 — Referral System E2E (3 hr) **Status:** ✅ Done 2026-09-15. Tagged `v1.6-referral-persistent-20260915`.

**Tasks:**
1. Create tables: `charvak_referrals`, `charvak_referral_clicks`, `charvak_referral_rewards`
2. Refactor `referral_engine.py` to persist
3. Add `/ref/{code}` route → redirects to `/register?ref={code}`
4. Capture `?ref=` on registration → insert into `charvak_referrals`
5. Grant reward on successful signup (credits or cash)
6. Build `/referral-dashboard` — user's own referral stats + share link
7. Email notify referrer when someone signs up
8. Test end-to-end

**Definition of done:**
- User can generate a referral link
- Clicking the link → signup → referrer sees the referral in their dashboard
- Reward granted to referrer's account

---

### Session 3 — Interview Prep E2E (2 hr)  **Status:** ✅ Done 2026-09-16. Tagged `v1.7-interview-prep-ai-20260916`. Full AI scoring + 8 questions + credit integration verified.

**Tasks:**
1. Create tables: `charvak_interview_sessions`, `charvak_interview_questions`
2. Refactor `interview_prep_engine.py` to persist
3. Wire `/interview-prep` page to:
   - Select role → fetch questions from OpenAI → save session
   - Answer → save response
   - Get AI feedback → save feedback
4. Charge credits per session (integrate with `ai_credit_engine`)
5. Test end-to-end

---

### Session 4 — University + Analytics (3 hr)

**University Portal:**
1. Create `charvak_university_partners`, `charvak_university_students`
2. Refactor `university_engine.py` to persist
3. Build signup flow + dashboard

**Analytics:**
1. Audit `admin_analytics.py` (currently UNKNOWN)
2. Wire to real DB queries
3. Add employer + user analytics endpoints

---

### Session 5 — The Big Three (5 hr)   ### AI Courses — ✅ COMPLETE 2026-09-16

**Tag:** `v1.8-ai-courses-20260916`
**Tables:** charvak_courses, charvak_enrollments, charvak_course_lessons, charvak_certificates
**Pages:** /ai-courses, /course/{name}, /my-course/{id}, /my-courses, /certificate/{id}
**Verified:** enroll → 25-course catalog → AI curriculum → lessons → AI tutor (2 credits) → certificate with custom name

---

## TODO — AI Courses: Course Fee + EMI (Next Session)

**Status:** ⏳ Queued 2026-09-16
**Priority:** Tier 3, high (revenue-impacting)
**Estimate:** 2–3 hours

### Business Model

**Two separate revenue streams per student:**

1. **Course Fee** — paid upfront OR via EMI
   - Range: ₹499 – ₹6,999 (already in `charvak_courses.price_inr`)
   - Currently: enrollment is FREE (fee is display-only)
   - Fix: gate enrollment behind payment

2. **AI Credits** — separate, consumable, per-interaction
   - ✅ Already live: AI Tutor = 2 credits/question
   - ✅ Already live: Interview Prep = 8 credits/session
   - ✅ Already live: AI Courses lesson generation = free (cached)
   - Purpose: meters heavy usage, keeps AI costs sustainable

### Implementation Tasks

**A. Database — 3 new tables**

```sql
CREATE TABLE charvak_course_payments (
    payment_id TEXT PRIMARY KEY,
    enrollment_id TEXT NOT NULL,
    email TEXT NOT NULL,
    amount_inr INTEGER NOT NULL,
    payment_type TEXT,  -- 'full' | 'emi_installment'
    razorpay_payment_id TEXT,
    razorpay_order_id TEXT,
    installment_num INTEGER,  -- NULL for full, 1..N for EMI
    status TEXT DEFAULT 'pending',  -- pending | paid | failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE charvak_course_installments (
    installment_id TEXT PRIMARY KEY,
    enrollment_id TEXT NOT NULL,
    email TEXT NOT NULL,
    installment_num INTEGER NOT NULL,
    total_installments INTEGER NOT NULL,
    amount_inr INTEGER NOT NULL,
    due_date DATE NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending | paid | overdue | cancelled
    paid_at TIMESTAMP,
    payment_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

**AI Courses:**
1. Create `charvak_courses`, `charvak_enrollments`, `charvak_lessons`, `charvak_certificates`
2. Refactor `ai_courses.py` + `ai_course_delivery.py`
3. Build payment-gated enrollment flow
4. Build lesson player
5. Certificate generation
6. Replace hardcoded `/ai-courses` list with DB fetch

**Micro-Internship:**
1. Two-sided marketplace tables
2. Escrow integration (with Dokets VouchAI)

**Mock Drives:**
1. Create tables
2. Build the missing `/mock-test` page

---

### Session 6 — Enterprise + WhatsApp + Cleanup (4 hr)     ## Enterprise Page — ✅ Complete 2026-09-16

- **Tag:** `v1.9-enterprise-page-20260916`
- **Route:** `/enterprise`
- **Content:** Hero, 6 features, 3 use-cases, pricing card, lead form
- **Lead capture:** POSTs to `/api/contact` → persists to `contacts` table (verified)
- **TODO — Option B (future session):** Expose enterprise engine features as public pages:
  - `/enterprise/salary-benchmarks` — salary data + benchmarks
  - `/enterprise/employers` — employer tier directory
  - `/enterprise/resume-books` — university resume books
  - `/enterprise/kiosk` — student check-in kiosk
  - Requires: 4 tables + 4 routes + 4 templates (~3 hr)

**Enterprise:**
1. Build the missing `/enterprise` page
2. Persist engine

**WhatsApp:**
1. Resolve Meta number registration (external)
2. Verify bot end-to-end

**Cleanup:**
1. Root directory scripts → `scripts/` (30 min)
2. Root-level `*.bak` files cleanup
3. Full system audit re-run
4. Tag `v2.0-tier3-complete-YYYYMMDD`
5. Final backup

---


### Session 5B - Company Mock Drives E2E (2 hr) - COMPLETE 2026-09-17

**Status:** Shipped as `v2.2-mock-drives-20260917`.

**Tables created:**
- `charvak_mock_sessions` - one row per started mock drive
- `charvak_mock_answers` - one row per answered question
- `charvak_assessment_results` - every assessment result across the platform (backs `results_system.py`)

**Engine refactors (both DB-backed, signatures preserved):**
- `complete_mock_drive.py` - sessions + answers persist across Render restarts
- `results_system.py` - all assessment results persist to Postgres
- `_sanitize_questions` method added to harden AI output (correct value is always int 0..N-1)
- AI prompt updated to specify 'correct is the 0-based INDEX'
- Defensive `int()` on `selected_option`

**Route:**
- `GET /mock-drive` (renders `companies.html`)

**Frontend fixes (4 real bugs in `companies.html`):**
- `completeMock()` was returning a fake 75% score; now calls `/api/mock/complete-full`
- `selectOption()` was browser-only; now POSTs `/api/mock/submit-complete` per answer
- Used browser `prompt()` for email; now reads `localStorage.userEmail`
- Onclick quote escaping killed the entire script block; fixed via `startArgs`/`optArgs`

**Other UX:**
- Converted `companies.html` to `{% extends "base.html" %}` (gets nav, footer, theme)
- Sticky progress bar ("Answered X / N")
- Loading spinner with estimated time for AI generation
- Real results card with pass/fail, "Take Another Mock Drive" button

**Nav:**
- Added "Mock Drives" link after "Assessments"

**Verified:** Real browser E2E - TCS mock drive with 9 answers, real score 18.9%, session + result recorded in DB.

---

### Session 5C - Mock Engine Consolidation (flagged for future, ~2 hr)

**Status:** Queued - not yet started.

Three more in-memory mock systems that also need persisting:

- `advanced_assessment_engine.py` - separate mock-drive variant at `/api/assessment/mock-drive`
- `company_assessment` / `company_mock_complete.py` - separate mock at `/api/company/*-mock`
- `/companies` route currently renders the mock-drive UI; should eventually become a brand directory while the mock UI stays at `/mock-drive`

**Goal:** Consolidate or persist these three, so all mock variants behave consistently.

---

## For Each Session — Checklist

**Before starting:**
- [ ] Read this plan
- [ ] `git pull` + `git status` (clean tree)
- [ ] Verify tag/baseline: `git log --oneline -3`

**During:**
- [ ] Work on a branch (`fix-<feature>-persistence`)
- [ ] Preserve exact method signatures + return shapes
- [ ] Test locally before committing
- [ ] Small commits — one logical change per commit

**After:**
- [ ] Test on prod after Render deploy
- [ ] Update this file's status table
- [ ] Tag if a milestone (e.g., `v1.5-jobboard-complete`)
- [ ] Run backup

---

## Risk Notes

- **Never modify `main.py` method signatures** — the frontend depends on them
- **Always preserve return shapes** — same JSON keys, same types
- **Add, don't replace** — new tables should sit alongside existing ones
- **Test one user journey manually** after each session
- **Keep the fallback pattern** — if DB fails, degrade gracefully to empty state, don't crash
- **Use `[System.IO.File]::WriteAllText` with UTF8Encoding(false)** for editing .py/.html — avoid `Set-Content -Encoding UTF8` (adds BOM, broke the site before)

---

## Reference Files

- `MASTER-REFERENCE.md` — full system documentation
- `ARCHITECTURE.md` — system design
- `PAGES-INVENTORY.md` — every template
- `COMPLETION-PLAN.md` — original plan (Tier 1-5 overview)
- `STATUS.md` — session-by-session history
- `scripts/tier3_audit.py` — rerun this anytime to check progress

---

*Update this file after each session with what's complete.*
