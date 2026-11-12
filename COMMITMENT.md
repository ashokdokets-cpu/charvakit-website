# Charvak - Commitment Tracker

**Last updated:** 2026-11-10 (Session 109 Complete)

---

## Session 109 - COMPLETE (2026-11-10)

### India Requirement Engine (Naukri / Techmap)
- /admin/india-radar: Pulls legal Indian jobs via Techmap API, filters out US jobs, and matches to Indian candidates.
- /job-board/{job_id}: Beautiful job detail page for Indian jobs.
- **AI Pre-fill:** When a candidate clicks "Take Assessment", the AI parses the JD and pre-fills the Role, Industry, and Experience Level automatically.
- **Monetization:** Sends Brevo email alerts to candidates when a job matches their skills.

### Candidate Marketing Engine (US)
- /admin/candidates: View bench candidates, generate AI marketing blurbs, and see reverse-matched US jobs.

### Mobile & UI Polish
- Added 	able-responsive to all new admin dashboards.
- Global mobile CSS ensures all pages work on phone, tablet, and desktop.

---

## Session 108 - COMPLETE (2026-11-08)
All 7 buildable tasks shipped (108A-G).

---

**Next session:** Demo at Eswar Engineering College (Nov 13). Set up daily Cron for India Radar.
- **Session 110:** Built Resume Funnel (/find-jobs) + ?99 Razorpay Paywall for India Jobs (7-day pass).

---

## Session 112 — COMPLETE (2026-11-12)

### B2B Employer Engine (Pay-on-Hire)

Built the complete self-serve B2B onboarding loop:

- **B2B Pricing Page** (/pricing-b2b): ?49,999/year for colleges + 8% pay-on-hire for employers
- **Dual-Mode Signup** (/employer/signup + ?type=institution): Same form, dynamic UI by URL param
- **Admin Approval Queue** (/admin/employer-accounts): Approve/Reject with one click
- **Magic Link Login** (/employer/login?token=...): Passwordless, 30-day session cookie
- **Employer Dashboard** (/employer/dashboard): Shows account details, empty pipeline for now

### Verified end-to-end with Eswar Test 2:
Signup ? Admin approval ? Magic link email ? Passwordless login ? Dashboard loads ?

### Files changed:
- main.py: employer_magic_login, employer_dashboard, send-login-link API
- templates/pricing-b2b.html
- templates/employer-signup.html
- templates/employer-dashboard.html
- templates/employer-login-failed.html
- templates/admin-employer-accounts.html (Send Login button)

### Bugs fixed during build:
- Duplicate /employer/dashboard route from Session 51
- Admin auth middleware blocking employer routes
- template_response signature ({"employer": x} vs employer=x)
- Magic link token rotation on 500 error

### Next session: Session 113 — DigiLocker document verification
