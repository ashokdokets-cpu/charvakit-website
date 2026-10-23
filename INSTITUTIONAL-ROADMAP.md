# CHARVAK INSTITUTIONAL ROADMAP — FLAGGED 2026-10-24

**Purpose:** Master list of what Charvak must build to become the operating
system for institutional placement. Derived from deep analysis of TPO objections.

**Status:** All FLAGGED. None built yet.

**Priority rule:** Build in Phase A order. Do not skip ahead.

---

## THE FOUR CORE TPO OBJECTIONS (What We're Solving For)

| Objection | What It Means | Solution |
|---|---|---|
| "We have an LMS" | I already paid for a system | **A4** LMS Bridge |
| "Students are lazy" | My students won't adopt this | **A3** Engagement Engine |
| "Where are the placements?" | You're not delivering outcomes | **A1** Employer Network |
| "How do I prove ROI to my Dean?" | I need defensible numbers | **A2** Proof Dashboard |

**Every institutional conversation reduces to one of these four.**

---

## PHASE A — CLOSE THE TPO OBJECTIONS (Sessions 81-90, ~21 sessions)

### A1 — Employer Network v1 (6 sessions)

**Problem:** TPOs' #1 ask is "where are the placements?" Without an employer network, Charvak is just another assessment vendor.

**What to build:**
- Employer portal: recruiters see verified candidates, filter by role/score/integrity
- Referral flow: TPO picks top students → sends intro request → Charvak introduces
- Employer onboarding: LinkedIn outreach template + self-serve signup
- Target: 20-50 employer signups (even if free)

**Sessions:** 3 (portal) + 2 (referral flow) + 1 (onboarding) = **6**

**Unlocks:** "I already have X employers waiting"

**Files to build:**
- `templates/employer/recruiter-portal.html` (new)
- `templates/employer/verify-candidates.html` (new)
- `employer_referral_engine.py` (new)
- `templates/employer/referral-flow.html` (new)
- `scripts/employer_onboarding.py` (new)

**Data model:**
- `charvak_employer_accounts` (new table)
- `charvak_referrals` (extend with TPO-initiated rows)

---

### A2 — Proof Dashboard (5 sessions)

**Problem:** TPOs report to Deans. Deans ask "did placement improve?" Charvak has no artifact for this conversation.

**What to build:**
- Print-ready PDF for Deans (their logo, their data)
- Cohort readiness benchmark vs Tier-2 composite
- Department heatmap (which depts are weakest)
- 3-month trend line (showing improvement)
- % students certified
- % certificates viewed by employers (real engagement signal)
- Top 10 students with placement-ready status

**Sessions:** 2 (backend aggregation) + 2 (dashboard UI) + 1 (PDF generator) = **5**

**Unlocks:** "Here's the report for your Dean"

**Files to build:**
- `proof_dashboard_engine.py` (new)
- `templates/admin/proof-dashboard.html` (new)
- `scripts/generate_dean_report_pdf.py` (new)
- Route: `GET /api/proof-dashboard/{institution_id}`
- Route: `GET /api/proof-dashboard/{institution_id}/pdf`

**Data model:**
- `charvak_institutions` (extend — need institution_id for cohort scoping)
- `charvak_certificate_views` (new — track when employers verify certs)

---

### A3 — Engagement Engine v1 (5 sessions)

**Problem:** "Students are lazy" — TPO has no way to nudge students. Charvak has no retention layer.

**What to build:**
- SMS/WhatsApp daily nudges: "Your TCS mock drive is waiting. 5 min."
- Streaks + leaderboards (Cohort Mode exists but not default-on)
- In-app notifications for exam deadlines and new companies
- Weekly "level up" unlocks (badges, certificates, spotlights)

**Sessions:** 2 (notification service) + 2 (habit engine) + 1 (leaderboards) = **5**

**Unlocks:** "Students show up because we nudge them"

**Files to build:**
- `notification_service.py` (extend — currently basic)
- `habit_engine.py` (extend — streak logic exists in cohort_engine)
- `templates/student/dashboard-v2.html` (new)
- Integration: Twilio (SMS), Meta WhatsApp Business API

**Data model:**
- `charvak_notification_queue` (extend)
- `charvak_student_preferences` (new — opt-in/out per channel)
- `charvak_engagement_events` (new — track streak/milestone events)

**Dependencies:**
- Twilio account (Rs ~2K/month for SMS)
- WhatsApp Business API approval (Meta — 2-4 weeks lead time)

---

### A4 — LMS Bridge (5 sessions)

**Problem:** "We already have a system" — Charvak must plug into Moodle/Canvas/Google Classroom instead of replacing them.

**What to build:**
- One-click sync from Moodle (most common in Indian colleges)
- Attendance integration (pull attendance, push completion)
- Grade sync (assessment scores → LMS gradebook)
- Single Sign-On (SAML / Google Workspace for students)
- Generic CSV export/import fallback

**Sessions:** 2 (Moodle plugin) + 2 (Google SSO) + 1 (CSV bridge) = **5**

**Unlocks:** "We plug into your existing system"

**Files to build:**
- `lms_bridge/moodle_plugin/` (new directory — PHP plugin for Moodle)
- `lms_bridge/canvas_adapter.py` (new — Canvas REST API)
- `lms_bridge/google_sso.py` (new — OAuth + SAML)
- `templates/admin/lms-settings.html` (new — configure LMS connection)
- Route: `POST /api/lms/connect` (auth-gated)
- Route: `GET /api/lms/sync-status/{institution_id}`

**Data model:**
- `charvak_lms_connections` (new — per institution)
- `charvak_lms_sync_log` (new — audit trail)

**Dependencies:**
- Google Workspace admin access (per institution)
- Moodle admin access (per institution)
- SAML setup if institution uses it

---

## PHASE B — OWN THE CATEGORY (Sessions 91-105, ~16 sessions)

### B1 — Placement Outcome Tracking + Attribution (5 sessions)

**Problem:** No attribution — Charvak can't prove "students who used us got placed at higher rates."

**What to build:**
- Track "did the student get placed?" (yes/no, company, package, date)
- Attribution: was Charvak used?
- Employer feedback: "how did the charvak-verified candidate perform?"
- Longitudinal tracking (1-year, 2-year post-graduation)

**Sessions:** 2 (schema + student self-report) + 2 (employer feedback) + 1 (dashboard) = **5**

**Unlocks:** "68% of Charvak-certified students placed vs 41% campus average"

**Files to build:**
- `outcome_tracking_engine.py` (new)
- `templates/admin/outcomes-dashboard.html` (new)
- `templates/employer/feedback-form.html` (new)
- `scripts/outcome_reports.py` (new)

**Data model:**
- `charvak_placement_outcomes` (new — student_id, company, package, date, source)
- `charvak_employer_feedback` (new — hire satisfaction ratings)

---

### B2 — Co-Branding Engine (4 sessions)

**Problem:** TPO buys something "theirs." Co-branding makes value visible to their Dean, their students, their employers.

**What to build:**
- "Amrita × Charvak" logo on everything
- Custom landing page per institution (their logo, their colors)
- Custom certificate template (institutional seal)
- Custom email sender ("from Amrita CDC")
- Student dashboard themed to institution

**Sessions:** 2 (white-label engine) + 1 (certificate co-branding) + 1 (theme system) = **4**

**Unlocks:** "It's branded as ours"

**Files to build:**
- `white_label_engine.py` (new)
- `templates/institutions/{slug}/` (theme overrides per institution)
- Extend `pdf_engine.py` — accept institution logo + seal
- Route: `GET /{institution_slug}/readiness-check` (institution-branded entry)

**Data model:**
- `charvak_institutions` (extend — logo_url, primary_color, cert_template)
- `charvak_custom_certificates` (extend — co-branded variants)

---

### B3 — Faculty + Placement Cell Workflow (5 sessions)

**Problem:** "My faculty won't adopt another tool" — Charvak must fit their workflow, not add to it.

**What to build:**
- Faculty dashboard: assign assessments as coursework
- Placement cell inbox: candidate shortlists, employer requests
- WhatsApp broadcast tool: send to a batch instantly
- Attendance-linked "completed" tracker

**Sessions:** 2 (faculty dashboard) + 2 (placement cell workflow) + 1 (WhatsApp broadcast) = **5**

**Unlocks:** "It's a tool for my workflow, not an extra one"

**Files to build:**
- `templates/faculty/assignment-dashboard.html` (new)
- `templates/placement/placement-inbox.html` (new)
- `whatsapp_broadcast_engine.py` (new)
- Routes: `POST /api/faculty/assign`, `GET /api/placement/inbox`

---

### B4 — Cohort Benchmarking (2 sessions)

**Problem:** TPO asks "how do I know this is good?" — Charvak has no peer comparison.

**What to build:**
- Peer institution composites (which colleges are similar?)
- Benchmark percentile ("Your students score in 68th percentile of Tier-2 colleges")
- Department-level peer comparison

**Sessions:** 2 (aggregation + UI) = **2**

**Unlocks:** "Your students are doing better than 2 out of 3 similar colleges"

**Files to build:**
- `cohort_benchmark_engine.py` (new)
- `templates/admin/benchmarking.html` (new)

---

## PHASE C — GLOBAL EXPANSION (Sessions 106+, ~12 sessions)

### C1 — Multi-Country Compliance (3 sessions)
- EU GDPR data residency
- US FERPA compliance
- India DPDP compliance

### C2 — University-Branded Subdomains (2 sessions)
- `amrita.charvakit.com` → institution-scoped experience
- Custom SSL per subdomain

### C3 — Multi-Language Admin UI (3 sessions)
- Admin interface in Hindi, Arabic, Bahasa
- Right-to-left support for Arabic

### C4 — Employer Marketplace (4 sessions)
- Public directory of hiring partners
- Employer self-signup + verification
- Public job board with verified candidates

---

## IMMEDIATE ACTIONS THIS WEEK (Not Sessions, Just Do)

### Action 1 — Reframe the Conversation (0 sessions)
**Stop saying:** "We do AI assessments."
**Start saying:** "We help your students get placed. The assessments are how you prove it works."

Update the homepage hero tagline to reflect this — even before Phase A.

### Action 2 — Write the TPO One-Pager (1 hour)
Replace `01-university-portal.pdf` with a new TPO-focused version:
- Title: "Prove Placement Readiness to Your Dean in 90 Days"
- 3 pages: Proof Dashboard screenshot (mock), Engagement Playbook, Employer Network teaser
- Bottom: "Request a demo — 20-minute call"

### Action 3 — Write the "Students Are Lazy" Playbook (1 hour)
Document:
- How TPOs use streaks to drive 5-day habit
- WhatsApp nudge templates (10 messages ready to copy-paste)
- Leaderboard setup (Cohort Mode, already live)
- Weekly engagement report (what TPO shows Dean)

This becomes a sales asset — attached to every university outreach.

### Action 4 — Start Proof Dashboard (Session 81)
Build A2 first. Highest leverage — unblocks every TPO conversation.

### Action 5 — Start Employer Network Outreach (Sessions 82-87)
Build A1. Master key for long-term moat.

---

## SEQUENCING PRINCIPLE

**Do not skip Phase A for Phase B or C.** Each phase is a layer. Phase A sells
the first contract. Phase B converts it to multi-year. Phase C scales to
multiple countries.

**Do not build all of Phase A at once.** Ship 1 gap, test with Amrita, ship
the next. Every gap should have a live customer verifying it works before
we build the next one.

---

## WHAT'S ALREADY LIVE (Reusable for Phase A)

| Capability | Can We Reuse For? |
|---|---|
| Career Assessment | A1, A2, A3 (as the assessment used) |
| Certificates (HMAC) | A1, A2 (the artifact TPO shows Dean) |
| Employer Dashboard (existing) | A1 (base for recruiter portal) |
| CAS API | A1 (bulk verification for employers) |
| Trust Score API | A1 (single-candidate verification) |
| Cohort Mode (existing) | A3 (base for engagement) |
| Referral System (existing) | A1 (extend for TPO-initiated) |
| Weekly Report Generator (existing) | A2 (base for Dean report) |
| Proof Dashboard Data | A2 (data exists; need PDF + UI) |

**We are 40-60% ready for Phase A already.** The remaining work is connecting existing pieces, not building new systems.

---

## RISK REGISTER

| Risk | Mitigation |
|---|---|
| WhatsApp Business API approval takes 2-4 weeks | Start approval process NOW (Meta) |
| Twilio costs scale with student count | Gate behind pilot tier; track per-institution cost |
| Employer network starts cold (zero signups) | Offer free "priority access" for first 20 employers |
| Proof dashboard needs institution_id (doesn't exist yet) | Add institution_id column in Session 81 |
| Co-branding requires per-institution asset uploads | Build asset upload flow in B2, not A-phase |

---

## DEFINITION OF DONE (Phase A)

- [ ] A1: 20+ employers signed up, TPO can refer candidates
- [ ] A2: Dean-report PDF generated for Amrita in <30 seconds
- [ ] A3: SMS/WhatsApp nudges live, streak leaderboard visible
- [ ] A4: Moodle plugin connects to a real institution
- [ ] All 4 objections can be answered in TPO conversation
- [ ] First paid contract signed using Phase A capabilities

**When Phase A is done, Charvak is a category-defining platform.**
**Until then, Charvak is a very good assessment tool.**

---

**This file is the source of truth for institutional expansion.**
**Re-read at the start of every session that touches university sales.**

**Last updated:** 2026-10-24 (Sessions 79-80 close-out)
---

## A2 — Proof Dashboard — UPDATE (2026-10-24)

**Backend:** ✅ COMPLETE + LIVE ON PROD
- Table: `charvak_certificate_views`
- Engine: `university_engine.get_proof_dashboard()`, `record_cert_view()`
- Routes: `/api/proof-dashboard/{id}`, `/api/proof-dashboard/{id}/pdf`, `/api/certificate/{id}/track-view`
- PDF: `pdf_engine.render_dean_report_pdf()` (4 pages, branded)
- Seeded: 3 institutions (Amrita, VIT, NIT Trichy), 150 students, 222 certs, 207 views
- Verified: PDFs downloaded to Desktop for all 3 institutions

**Frontend:** ⏸ FLAGGED — deferred
- No dashboard UI
- No signed URLs (reverted)
- No login page
- Manual PDF email is the current workflow
- Full build plan in `DEAN_REPORT_FRONTEND_FLAG.md`
- **Trigger to build:** first paying client OR 5+ manual reports/month

**Decision doc:** `DEAN_REPORT_DECISION.md` (committed 489ed68)

**Files:**
- `university_engine.py` (extends with 2 new methods)
- `pdf_engine.py` (extends with render_dean_report_pdf)
- `migrations/20261024_proof_dashboard.sql` (new)
- `scripts/seed_proof_dashboard.py` (new)

**Impact:** Solves "How do I prove ROI to my Dean?" — the #1 TPO objection.

---

## Phase A Progress (2026-10-24 update)

| Item | Sessions Planned | Status | Notes |
|---|---|---|---|
| **A1 — Employer Network** | 6 | **v0.3 SHIPPED** | Public page + referral + signup + admin approval |
| **A2 — Proof Dashboard** | 5 | **Backend 100%** | Dean PDF live; frontend deferred |
| **A3 — Engagement Engine** | 5 | **v1.0 SHIPPED** | Dashboard + badges + leaderboard; SMS/WhatsApp deferred |
| **A4 — LMS Bridge** | 5 | Not started | Next phase |

### A1 remaining (v0.4+)
- Employer dashboard enhancements (filtered views, saved candidates)
- Referral status update UI in admin
- Automated status notifications

### A3 remaining (v0.2+)
- Twilio SMS integration
- WhatsApp Business API integration
- Weekly level-up cron
- Cohort leaderboard surfaced on engagement dashboard

### A2 remaining
- Dean frontend UI (see DEAN_REPORT_FRONTEND_FLAG.md)
- Trigger: first paying client OR 5+ reports/month

---

---

## PLG SaaS Transformation (FLAGGED 2026-10-24)

Full strategic plan at `PLG_SAAS_ROADMAP.md`.

**Summary:** Platform is 60% ready for self-driven SaaS revenue. Missing
pieces are ~20 sessions. Best path is B2B University SaaS (10-20x ROI
vs B2C).

**Do not build speculatively.** Unfreeze only when:
- Amrita signs OR
- 5+ paying customers OR
- ₹50K+ marketing budget OR
- 6+ months runway

**Worst-case scenario for building too early:** You burn 20 sessions
building paywalls for 674 users and still have 674 users.

**Worst-case scenario for waiting:** You sign 3 universities and
*then* need to build infrastructure under pressure. Better problem
than the first.
